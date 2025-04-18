from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import os
import subprocess
import random

# Create blueprint
pools_bp = Blueprint('pools', __name__, url_prefix='/pools')

# Sample data for demonstration
sample_pools = [
    {
        'poolid': 1,
        'name': 'Default',
        'pool_type': 'Backup',
        'storage': 'File1',
        'num_vols': 10,
        'max_vols': 20,
        'used_vols': 5,
        'recycle': 'yes',
        'auto_prune': 'yes',
        'vol_retention': '30 days',
        'max_vol_jobs': 1,
        'max_vol_bytes': 5 * 1024 * 1024 * 1024,  # 5 GB
        'label_format': 'Default-${Year}${Month}',
        'description': 'Default backup pool',
        'created': datetime.now() - timedelta(days=90),
        'last_written': datetime.now() - timedelta(days=1),
        'usage_percent': 45
    },
    {
        'poolid': 2,
        'name': 'Full',
        'pool_type': 'Backup',
        'storage': 'File1',
        'num_vols': 5,
        'max_vols': 10,
        'used_vols': 3,
        'recycle': 'yes',
        'auto_prune': 'yes',
        'vol_retention': '60 days',
        'max_vol_jobs': 1,
        'max_vol_bytes': 10 * 1024 * 1024 * 1024,  # 10 GB
        'label_format': 'Full-${Year}${Month}',
        'description': 'Pool for full backups',
        'created': datetime.now() - timedelta(days=60),
        'last_written': datetime.now() - timedelta(days=7),
        'usage_percent': 75
    },
    {
        'poolid': 3,
        'name': 'Incremental',
        'pool_type': 'Backup',
        'storage': 'File1',
        'num_vols': 15,
        'max_vols': 30,
        'used_vols': 10,
        'recycle': 'yes',
        'auto_prune': 'yes',
        'vol_retention': '14 days',
        'max_vol_jobs': 10,
        'max_vol_bytes': 2 * 1024 * 1024 * 1024,  # 2 GB
        'label_format': 'Inc-${Year}${Month}',
        'description': 'Pool for incremental backups',
        'created': datetime.now() - timedelta(days=45),
        'last_written': datetime.now() - timedelta(hours=12),
        'usage_percent': 35
    },
    {
        'poolid': 4,
        'name': 'Archive',
        'pool_type': 'Archive',
        'storage': 'Tape1',
        'num_vols': 3,
        'max_vols': 5,
        'used_vols': 2,
        'recycle': 'no',
        'auto_prune': 'no',
        'vol_retention': '5 years',
        'max_vol_jobs': 1,
        'max_vol_bytes': 100 * 1024 * 1024 * 1024,  # 100 GB
        'label_format': 'Archive-${Year}',
        'description': 'Long-term archive pool',
        'created': datetime.now() - timedelta(days=180),
        'last_written': datetime.now() - timedelta(days=30),
        'usage_percent': 90
    }
]

# Sample volumes data
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
@pools_bp.route('/')
def index():
    # Calculate pool statistics
    stats = {
        'total_pools': len(sample_pools),
        'total_volumes': sum(pool['num_vols'] for pool in sample_pools),
        'used_volumes': sum(pool['used_vols'] for pool in sample_pools),
        'avg_usage': int(sum(pool['usage_percent'] for pool in sample_pools) / len(sample_pools)) if sample_pools else 0
    }
    
    return render_template('pools/index.html', 
                          pools=sample_pools, 
                          stats=stats,
                          format_bytes=format_bytes)

@pools_bp.route('/add')
def add_pool():
    # Sample storage data for the form
    storages = [
        {'name': 'File1', 'type': 'File'},
        {'name': 'Tape1', 'type': 'Tape'},
        {'name': 'Cloud1', 'type': 'Cloud'}
    ]
    
    return render_template('pools/add_pool.html', storages=storages)

@pools_bp.route('/add', methods=['POST'])
def add_pool_post():
    try:
        # Get form data
        name = request.form['name']
        pool_type = request.form['pool_type']
        storage = request.form['storage']
        label_format = request.form.get('label_format', '')
        max_volumes = int(request.form.get('max_volumes', 100))
        volume_retention = int(request.form.get('volume_retention', 30))
        retention_unit = request.form.get('retention_unit', 'days')
        max_volume_jobs = int(request.form.get('max_volume_jobs', 1))
        max_volume_bytes = float(request.form.get('max_volume_bytes', 5)) * 1024 * 1024 * 1024  # Convert GB to bytes
        recycle = request.form.get('recycle', 'yes')
        auto_prune = request.form.get('auto_prune', 'yes')
        description = request.form.get('description', '')
        
        # Check if create initial volumes
        create_volumes = 'create_volumes' in request.form
        volume_count = int(request.form.get('volume_count', 5)) if create_volumes else 0
        volume_prefix = request.form.get('volume_prefix', '')
        
        # In a real application, you would add the pool to Bacula using bconsole or API
        # For this example, we'll simulate success
        
        # Create pool command (would be executed in a real application)
        pool_cmd = f"""
        create pool name={name} 
        pooltype={pool_type}
        labelformat="{label_format}"
        maximumvolumes={max_volumes}
        volumeretention={volume_retention} {retention_unit}
        maximumvolumejobs={max_volume_jobs}
        maximumvolumebytes={int(max_volume_bytes)}
        recycle={recycle}
        autoprune={auto_prune}
        storage={storage}
        """
        
        # Log the command that would be executed
        print(f"Would execute: {pool_cmd}")
        
        # If creating volumes, generate volume creation commands
        if create_volumes:
            for i in range(1, volume_count + 1):
                volume_name = f"{volume_prefix}{i:02d}"
                volume_cmd = f"label volume={volume_name} pool={name} storage={storage}"
                print(f"Would execute: {volume_cmd}")
        
        flash('Pool created successfully!', 'success')
        
        # If volumes were created, show additional message
        if create_volumes:
            flash(f'Created {volume_count} initial volumes in the pool.', 'info')
            
        return redirect(url_for('pools.index'))
    
    except Exception as e:
        flash(f'Error creating pool: {str(e)}', 'danger')
        return redirect(url_for('pools.add_pool'))

@pools_bp.route('/<int:pool_id>')
def detail(pool_id):
    # Find the pool by ID
    pool = next((p for p in sample_pools if p['poolid'] == pool_id), None)
    if not pool:
        flash('Pool not found', 'danger')
        return redirect(url_for('pools.index'))
    
    # Get volumes for this pool
    volumes = [v for v in sample_volumes if v['poolid'] == pool_id]
    
    # Generate volume usage history data
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    data = []
    
    # Start with a base value and generate somewhat realistic looking data
    base_value = pool['usage_percent'] * 0.7
    for i in range(30):
        # Add some randomness but with an upward trend
        change = random.uniform(-5, 7)
        value = base_value + change
        # Ensure value stays within reasonable bounds
        value = max(0, min(100, value))
        data.append(value)
        # Update base value with a slight upward trend
        base_value = value + 0.5
    
    volume_usage = {
        'labels': dates,
        'data': data
    }
    
    return render_template('pools/detail.html', 
                          pool=pool, 
                          volumes=volumes,
                          volume_usage=volume_usage,
                          format_bytes=format_bytes)

@pools_bp.route('/<int:pool_id>/edit')
def edit_pool(pool_id):
    # Find the pool by ID
    pool = next((p for p in sample_pools if p['poolid'] == pool_id), None)
    if not pool:
        flash('Pool not found', 'danger')
        return redirect(url_for('pools.index'))
    
    # Sample storage data for the form
    storages = [
        {'name': 'File1', 'type': 'File'},
        {'name': 'Tape1', 'type': 'Tape'},
        {'name': 'Cloud1', 'type': 'Cloud'}
    ]
    
    return render_template('pools/edit_pool.html', pool=pool, storages=storages)

@pools_bp.route('/<int:pool_id>/edit', methods=['POST'])
def edit_pool_post(pool_id):
    # In a real app, this would update the pool in Bacula
    flash('Pool updated successfully!', 'success')
    return redirect(url_for('pools.detail', pool_id=pool_id))

@pools_bp.route('/<int:pool_id>/delete', methods=['POST'])
def delete_pool(pool_id):
    # In a real app, this would delete the pool from Bacula
    flash('Pool deleted successfully!', 'success')
    return redirect(url_for('pools.index'))

@pools_bp.route('/<int:pool_id>/update_volumes', methods=['POST'])
def update_volumes(pool_id):
    # In a real app, this would update volume status in Bacula
    flash('Volume status updated successfully!', 'success')
    return redirect(url_for('pools.detail', pool_id=pool_id))

@pools_bp.route('/<int:pool_id>/add_volumes')
def add_volumes(pool_id):
    # Find the pool by ID
    pool = next((p for p in sample_pools if p['poolid'] == pool_id), None)
    if not pool:
        flash('Pool not found', 'danger')
        return redirect(url_for('pools.index'))
    
    return render_template('pools/add_volumes.html', pool=pool)

@pools_bp.route('/<int:pool_id>/add_volumes', methods=['POST'])
def add_volumes_post(pool_id):
    # In a real app, this would add volumes to the pool in Bacula
    volume_count = int(request.form.get('volume_count', 1))
    flash(f'{volume_count} volumes added to the pool successfully!', 'success')
    return redirect(url_for('pools.detail', pool_id=pool_id))

# Register template filters
@pools_bp.app_template_filter('format_bytes')
def _format_bytes(bytes):
    return format_bytes(bytes)