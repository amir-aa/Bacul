# app/routes/volumes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import random

# Create blueprint
volumes_bp = Blueprint('volumes', __name__, url_prefix='/volumes')

# Sample data for demonstration
sample_volumes = [
    {
        'mediaid': 1,
        'volumename': 'Default-202501',
        'poolid': 1,
        'pool_name': 'Default',
        'mediatype': 'File',
        'first_written': datetime.now() - timedelta(days=15),
        'last_written': datetime.now() - timedelta(days=1),
        'volbytes': 1.2 * 1024 * 1024 * 1024,  # 1.2 GB
        'volstatus': 'Full',
        'enabled': 1,
        'recycle': 1,
        'slot': 0,
        'inchanger': 0,
        'volretention': 30 * 24 * 3600,  # 30 days in seconds
        'voljobs': 5,
        'volfiles': 12500,
        'max_volbytes': 5 * 1024 * 1024 * 1024,  # 5 GB
        'usage_percent': 24
    },
    {
        'mediaid': 2,
        'volumename': 'Default-202502',
        'poolid': 1,
        'pool_name': 'Default',
        'mediatype': 'File',
        'first_written': datetime.now() - timedelta(days=10),
        'last_written': datetime.now() - timedelta(days=3),
        'volbytes': 3.5 * 1024 * 1024 * 1024,  # 3.5 GB
        'volstatus': 'Append',
        'enabled': 1,
        'recycle': 1,
        'slot': 0,
        'inchanger': 0,
        'volretention': 30 * 24 * 3600,  # 30 days in seconds
        'voljobs': 8,
        'volfiles': 22000,
        'max_volbytes': 5 * 1024 * 1024 * 1024,  # 5 GB
        'usage_percent': 70
    },
    {
        'mediaid': 3,
        'volumename': 'Full-202501',
        'poolid': 2,
        'pool_name': 'Full',
        'mediatype': 'File',
        'first_written': datetime.now() - timedelta(days=30),
        'last_written': datetime.now() - timedelta(days=7),
        'volbytes': 8.2 * 1024 * 1024 * 1024,  # 8.2 GB
        'volstatus': 'Full',
        'enabled': 1,
        'recycle': 1,
        'slot': 0,
        'inchanger': 0,
        'volretention': 60 * 24 * 3600,  # 60 days in seconds
        'voljobs': 1,
        'volfiles': 85000,
        'max_volbytes': 10 * 1024 * 1024 * 1024,  # 10 GB
        'usage_percent': 82
    }
]

# Helper function to format bytes
def format_bytes(bytes):
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024 * 1024 * 1024:
        return f"{bytes / (1024 * 1024):.2f} MB"
    elif bytes < 1024 * 1024 * 1024 * 1024:
        return f"{bytes / (1024 * 1024 * 1024):.2f} GB"
    else:
        return f"{bytes / (1024 * 1024 * 1024 * 1024):.2f} TB"

# Routes
@volumes_bp.route('/')
def index():
    # Calculate volume statistics
    stats = {
        'total_volumes': len(sample_volumes),
        'full_volumes': sum(1 for v in sample_volumes if v['volstatus'] == 'Full'),
        'append_volumes': sum(1 for v in sample_volumes if v['volstatus'] == 'Append'),
        'total_bytes': sum(v['volbytes'] for v in sample_volumes),
        'avg_usage': int(sum(v['usage_percent'] for v in sample_volumes) / len(sample_volumes)) if sample_volumes else 0
    }
    
    return render_template('volumes/index.html', 
                          volumes=sample_volumes, 
                          stats=stats,
                          format_bytes=format_bytes)

@volumes_bp.route('/<int:volume_id>')
def detail(volume_id):
    # Find the volume by ID
    volume = next((v for v in sample_volumes if v['mediaid'] == volume_id), None)
    if not volume:
        flash('Volume not found', 'danger')
        return redirect(url_for('volumes.index'))
    
    return render_template('volumes/detail.html', volume=volume, format_bytes=format_bytes)

@volumes_bp.route('/add')
def add_volume():
    # Sample pool data for the form
    pools = [
        {'poolid': 1, 'name': 'Default'},
        {'poolid': 2, 'name': 'Full'},
        {'poolid': 3, 'name': 'Incremental'},
        {'poolid': 4, 'name': 'Archive'}
    ]
    
    # Sample storage data for the form
    storages = [
        {'storageid': 1, 'name': 'File1'},
        {'storageid': 2, 'name': 'Tape1'},
        {'storageid': 3, 'name': 'Cloud1'}
    ]
    
    return render_template('volumes/add_volume.html', pools=pools, storages=storages)

@volumes_bp.route('/add', methods=['POST'])
def add_volume_post():
    try:
        # Get form data
        name = request.form['name']
        pool_id = int(request.form['pool_id'])
        storage_id = int(request.form['storage_id'])
        
        # In a real application, you would add the volume to Bacula using bconsole or API
        # For this example, we'll simulate success
        
        flash('Volume created successfully!', 'success')
        return redirect(url_for('volumes.index'))
    
    except Exception as e:
        flash(f'Error creating volume: {str(e)}', 'danger')
        return redirect(url_for('volumes.add_volume'))

@volumes_bp.route('/<int:volume_id>/update_status', methods=['POST'])
def update_status(volume_id):
    # In a real app, this would update the volume status in Bacula
    status = request.form.get('status')
    flash(f'Volume status updated to {status}!', 'success')
    return redirect(url_for('volumes.detail', volume_id=volume_id))

@volumes_bp.route('/<int:volume_id>/delete', methods=['POST'])
def delete_volume(volume_id):
    # In a real app, this would delete the volume from Bacula
    flash('Volume deleted successfully!', 'success')
    return redirect(url_for('volumes.index'))

# Register template filters
@volumes_bp.app_template_filter('format_bytes')
def _format_bytes(bytes):
    return format_bytes(bytes)