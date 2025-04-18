# app/routes/storage.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import random
import subprocess
import os

# Create blueprint
storage_bp = Blueprint('storage', __name__, url_prefix='/storage')

# Sample data for demonstration
sample_storage = [
    {
        'storageid': 1,
        'name': 'File1',
        'storage_type': 'File',
        'address': 'localhost',
        'sd_port': 9103,
        'device_name': 'FileStorage',
        'media_type': 'File',
        'archive_device': '/var/lib/bacula/storage',
        'max_concurrent_jobs': 10,
        'enabled': True,
        'description': 'Local file storage',
        'created': datetime.now() - timedelta(days=120),
        'last_accessed': datetime.now() - timedelta(hours=3),
        'status': 'online',
        'free_space': 500 * 1024 * 1024 * 1024,  # 500 GB
        'total_space': 1024 * 1024 * 1024 * 1024,  # 1 TB
        'volumes': 15,
        'usage_percent': 52
    },
    {
        'storageid': 2,
        'name': 'Tape1',
        'storage_type': 'Tape',
        'address': 'tape-server',
        'sd_port': 9103,
        'device_name': 'TapeStorage',
        'media_type': 'LTO-8',
        'drive_index': 0,
        'auto_changer': 'yes',
        'changer_device': '/dev/sg0',
        'max_concurrent_jobs': 1,
        'enabled': True,
        'description': 'Tape library for long-term storage',
        'created': datetime.now() - timedelta(days=90),
        'last_accessed': datetime.now() - timedelta(days=2),
        'status': 'online',
        'free_slots': 10,
        'total_slots': 24,
        'volumes': 14,
        'usage_percent': 58
    },
    {
        'storageid': 3,
        'name': 'Cloud1',
        'storage_type': 'Cloud',
        'address': 'cloud-gateway',
        'sd_port': 9103,
        'device_name': 'CloudStorage',
        'media_type': 'Cloud',
        'cloud_provider': 's3',
        'bucket_name': 'bacula-backups',
        'region': 'us-east-1',
        'max_concurrent_jobs': 5,
        'enabled': True,
        'description': 'Amazon S3 cloud storage',
        'created': datetime.now() - timedelta(days=30),
        'last_accessed': datetime.now() - timedelta(days=1),
        'status': 'online',
        'volumes': 8,
        'usage_percent': 35
    },
    {
        'storageid': 4,
        'name': 'OfflineStorage',
        'storage_type': 'File',
        'address': 'backup-server',
        'sd_port': 9103,
        'device_name': 'OfflineStorage',
        'media_type': 'File',
        'archive_device': '/mnt/external/backups',
        'max_concurrent_jobs': 2,
        'enabled': False,
        'description': 'Offline external drive storage',
        'created': datetime.now() - timedelta(days=180),
        'last_accessed': datetime.now() - timedelta(days=45),
        'status': 'offline',
        'free_space': 200 * 1024 * 1024 * 1024,  # 200 GB
        'total_space': 2 * 1024 * 1024 * 1024 * 1024,  # 2 TB
        'volumes': 5,
        'usage_percent': 90
    }
]

# Sample devices data
sample_devices = [
    {
        'deviceid': 1,
        'name': 'FileStorage',
        'storageid': 1,
        'storage_name': 'File1',
        'device_type': 'File',
        'archive_device': '/var/lib/bacula/storage',
        'media_type': 'File',
        'status': 'online',
        'enabled': True,
        'read_only': False,
        'automatic_mount': True,
        'removable_media': False,
        'random_access': True,
        'volumes': 15
    },
    {
        'deviceid': 2,
        'name': 'TapeStorage',
        'storageid': 2,
        'storage_name': 'Tape1',
        'device_type': 'Tape',
        'archive_device': '/dev/nst0',
        'media_type': 'LTO-8',
        'status': 'online',
        'enabled': True,
        'read_only': False,
        'automatic_mount': True,
        'removable_media': True,
        'random_access': False,
        'volumes': 14
    },
    {
        'deviceid': 3,
        'name': 'CloudStorage',
        'storageid': 3,
        'storage_name': 'Cloud1',
        'device_type': 'Cloud',
        'archive_device': 's3://bacula-backups',
        'media_type': 'Cloud',
        'status': 'online',
        'enabled': True,
        'read_only': False,
        'automatic_mount': True,
        'removable_media': False,
        'random_access': True,
        'volumes': 8
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
@storage_bp.route('/')
def index():
    # Calculate storage statistics
    stats = {
        'total_storage': len(sample_storage),
        'online_storage': sum(1 for s in sample_storage if s['status'] == 'online'),
        'total_volumes': sum(s['volumes'] for s in sample_storage),
        'avg_usage': int(sum(s['usage_percent'] for s in sample_storage) / len(sample_storage)) if sample_storage else 0
    }
    
    return render_template('storage/index.html', 
                          storages=sample_storage, 
                          stats=stats,
                          format_bytes=format_bytes)

@storage_bp.route('/add')
def add_storage():
    return render_template('storage/add_storage.html')

@storage_bp.route('/add', methods=['POST'])
def add_storage_post():
    try:
        # Get form data
        name = request.form['name']
        storage_type = request.form['storage_type']
        address = request.form['address']
        sd_port = int(request.form.get('sd_port', 9103))
        password = request.form['password']
        device_name = request.form['device_name']
        media_type = request.form['media_type']
        max_concurrent_jobs = int(request.form.get('max_concurrent_jobs', 5))
        heartbeat_interval = int(request.form.get('heartbeat_interval', 30))
        description = request.form.get('description', '')
        enabled = 'enabled' in request.form
        
        # Storage type specific data
        if storage_type == 'File':
            archive_device = request.form['archive_device']
            
            # Create storage command (would be executed in a real application)
            storage_cmd = f"""
            configure add storage name={name} address={address} sdport={sd_port} password={password}
            device={device_name} mediatype={media_type} archivedevice={archive_device}
            maximumconcurrentjobs={max_concurrent_jobs} heartbeatinterval={heartbeat_interval}
            """
            
        elif storage_type == 'Tape':
            drive_index = int(request.form.get('drive_index', 0))
            auto_changer = request.form.get('auto_changer', 'no')
            changer_device = request.form.get('changer_device', '')
            
            # Create storage command for tape
            storage_cmd = f"""
            configure add storage name={name} address={address} sdport={sd_port} password={password}
            device={device_name} mediatype={media_type} driveindex={drive_index}
            autochanger={auto_changer} changerdevice={changer_device}
            maximumconcurrentjobs={max_concurrent_jobs} heartbeatinterval={heartbeat_interval}
            """
            
        elif storage_type == 'Cloud':
            cloud_provider = request.form.get('cloud_provider', 's3')
            bucket_name = request.form.get('bucket_name', '')
            access_key = request.form.get('access_key', '')
            secret_key = request.form.get('secret_key', '')
            region = request.form.get('region', '')
            
            # Create storage command for cloud
            storage_cmd = f"""
            configure add storage name={name} address={address} sdport={sd_port} password={password}
            device={device_name} mediatype={media_type} cloudprovider={cloud_provider}
            bucket={bucket_name} accesskey={access_key} secretkey={secret_key} region={region}
            maximumconcurrentjobs={max_concurrent_jobs} heartbeatinterval={heartbeat_interval}
            """
        
        # Log the command that would be executed
        print(f"Would execute: {storage_cmd}")
        
        flash('Storage device created successfully!', 'success')
        return redirect(url_for('storage.index'))
    
    except Exception as e:
        flash(f'Error creating storage device: {str(e)}', 'danger')
        return redirect(url_for('storage.add_storage'))

@storage_bp.route('/<int:storage_id>')
def detail(storage_id):
    # Find the storage by ID
    storage = next((s for s in sample_storage if s['storageid'] == storage_id), None)
    if not storage:
        flash('Storage not found', 'danger')
        return redirect(url_for('storage.index'))
    
    # Get devices for this storage
    devices = [d for d in sample_devices if d['storageid'] == storage_id]
    
    # Generate usage history data
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    data = []
    
    # Start with a base value and generate somewhat realistic looking data
    base_value = storage['usage_percent'] * 0.8
    for i in range(30):
        # Add some randomness but with an upward trend
        change = random.uniform(-3, 5)
        value = base_value + change
        # Ensure value stays within reasonable bounds
        value = max(0, min(100, value))
        data.append(value)
        # Update base value with a slight upward trend
        base_value = value + 0.3
    
    storage_usage = {
        'labels': dates,
        'data': data
    }
    
    # Generate throughput data (MB/s over time)
    throughput_data = {
        'labels': [(datetime.now() - timedelta(hours=i)).strftime('%H:%M') for i in range(24, 0, -1)],
        'read': [random.uniform(1, 50) for _ in range(24)],
        'write': [random.uniform(5, 100) for _ in range(24)]
    }
    
    return render_template('storage/detail.html', 
                          storage=storage, 
                          devices=devices,
                          storage_usage=storage_usage,
                          throughput_data=throughput_data,
                          format_bytes=format_bytes)

@storage_bp.route('/<int:storage_id>/edit')
def edit_storage(storage_id):
    # Find the storage by ID
    storage = next((s for s in sample_storage if s['storageid'] == storage_id), None)
    if not storage:
        flash('Storage not found', 'danger')
        return redirect(url_for('storage.index'))
    
    return render_template('storage/edit_storage.html', storage=storage)

@storage_bp.route('/<int:storage_id>/edit', methods=['POST'])
def edit_storage_post(storage_id):
    # In a real app, this would update the storage in Bacula
    flash('Storage device updated successfully!', 'success')
    return redirect(url_for('storage.detail', storage_id=storage_id))

@storage_bp.route('/<int:storage_id>/delete', methods=['POST'])
def delete_storage(storage_id):
    # In a real app, this would delete the storage from Bacula
    flash('Storage device deleted successfully!', 'success')
    return redirect(url_for('storage.index'))

@storage_bp.route('/<int:storage_id>/status', methods=['POST'])
def update_status(storage_id):
    # In a real app, this would check the status of the storage device
    flash('Storage status updated successfully!', 'success')
    return redirect(url_for('storage.detail', storage_id=storage_id))

@storage_bp.route('/devices')
def devices():
    return render_template('storage/devices.html', devices=sample_devices)

@storage_bp.route('/device/<int:device_id>')
def device_detail(device_id):
    # Find the device by ID
    device = next((d for d in sample_devices if d['deviceid'] == device_id), None)
    if not device:
        flash('Device not found', 'danger')
        return redirect(url_for('storage.devices'))
    
    return render_template('storage/device_detail.html', device=device)

# Register template filters
@storage_bp.app_template_filter('format_bytes')
def _format_bytes(bytes):
    return format_bytes(bytes)





sample_jobs = [
    {
        'jobid': 1,
        'name': 'Daily-Backup-Server1',
        'type': 'B',  # B for Backup
        'level': 'F',  # F for Full
        'clientid': 1,
        'client_name': 'server1.example.com',
        'jobstatus': 'T',  # T for Terminated successfully
        'starttime': '2023-04-17 01:00:00',
        'endtime': '2023-04-17 01:45:30',
        'jobbytes': 15728640000,  # 15 GB
        'jobfiles': 250000,
        'storageid': 1
    },
    {
        'jobid': 2,
        'name': 'Daily-Backup-Server2',
        'type': 'B',
        'level': 'F',
        'clientid': 2,
        'client_name': 'server2.example.com',
        'jobstatus': 'T',
        'starttime': '2023-04-17 02:00:00',
        'endtime': '2023-04-17 02:30:45',
        'jobbytes': 10737418240,  # 10 GB
        'jobfiles': 180000,
        'storageid': 1
    },
    {
        'jobid': 3,
        'name': 'Daily-Backup-Server3',
        'type': 'B',
        'level': 'I',  # I for Incremental
        'clientid': 3,
        'client_name': 'server3.example.com',
        'jobstatus': 'E',  # E for Error
        'starttime': '2023-04-17 03:00:00',
        'endtime': '2023-04-17 03:05:20',
        'jobbytes': 0,
        'jobfiles': 0,
        'storageid': 2
    },
    {
        'jobid': 4,
        'name': 'Weekly-Backup-Server1',
        'type': 'B',
        'level': 'F',
        'clientid': 1,
        'client_name': 'server1.example.com',
        'jobstatus': 'T',
        'starttime': '2023-04-16 01:00:00',
        'endtime': '2023-04-16 02:10:15',
        'jobbytes': 16106127360,  # 15 GB
        'jobfiles': 260000,
        'storageid': 2
    },
    {
        'jobid': 5,
        'name': 'Restore-Server2-Files',
        'type': 'R',  # R for Restore
        'level': '',
        'clientid': 2,
        'client_name': 'server2.example.com',
        'jobstatus': 'T',
        'starttime': '2023-04-16 10:30:00',
        'endtime': '2023-04-16 11:15:45',
        'jobbytes': 5368709120,  # 5 GB
        'jobfiles': 75000,
        'storageid': 1
    },
    {
        'jobid': 6,
        'name': 'Daily-Backup-Server4',
        'type': 'B',
        'level': 'D',  # D for Differential
        'clientid': 4,
        'client_name': 'server4.example.com',
        'jobstatus': 'T',
        'starttime': '2023-04-17 04:00:00',
        'endtime': '2023-04-17 04:20:30',
        'jobbytes': 3221225472,  # 3 GB
        'jobfiles': 45000,
        'storageid': 3
    },
    {
        'jobid': 7,
        'name': 'Daily-Backup-Server5',
        'type': 'B',
        'level': 'F',
        'clientid': 5,
        'client_name': 'server5.example.com',
        'jobstatus': 'R',  # R for Running
        'starttime': '2023-04-17 05:00:00',
        'endtime': None,
        'jobbytes': 1073741824,  # 1 GB so far
        'jobfiles': 15000,
        'storageid': 1
    },
    {
        'jobid': 8,
        'name': 'Monthly-Backup-Server1',
        'type': 'B',
        'level': 'F',
        'clientid': 1,
        'client_name': 'server1.example.com',
        'jobstatus': 'T',
        'starttime': '2023-04-01 01:00:00',
        'endtime': '2023-04-01 02:30:45',
        'jobbytes': 17179869184,  # 16 GB
        'jobfiles': 275000,
        'storageid': 3
    },
    {
        'jobid': 9,
        'name': 'Daily-Backup-Server2',
        'type': 'B',
        'level': 'I',
        'clientid': 2,
        'client_name': 'server2.example.com',
        'jobstatus': 'T',
        'starttime': '2023-04-18 02:00:00',
        'endtime': '2023-04-18 02:15:30',
        'jobbytes': 1073741824,  # 1 GB
        'jobfiles': 20000,
        'storageid': 2
    },
    {
        'jobid': 10,
        'name': 'Daily-Backup-Server3',
        'type': 'B',
        'level': 'I',
        'clientid': 3,
        'client_name': 'server3.example.com',
        'jobstatus': 'T',
        'starttime': '2023-04-18 03:00:00',
        'endtime': '2023-04-18 03:10:15',
        'jobbytes': 2147483648,  # 2 GB
        'jobfiles': 35000,
        'storageid': 1
    }
]

# Sample volumes data
sample_volumes = [
    {
        'mediaid': 1,
        'volumename': 'Full-0001',
        'volstatus': 'Full',
        'pool_name': 'Full Pool',
        'storageid': 1,
        'mediatype': 'File',
        'volbytes': 15728640000,  # 15 GB
        'volfiles': 250000,
        'lastwritten': '2023-04-17 01:45:30'
    },
    {
        'mediaid': 2,
        'volumename': 'Full-0002',
        'volstatus': 'Full',
        'pool_name': 'Full Pool',
        'storageid': 1,
        'mediatype': 'File',
        'volbytes': 10737418240,  # 10 GB
        'volfiles': 180000,
        'lastwritten': '2023-04-17 02:30:45'
    },
    {
        'mediaid': 3,
        'volumename': 'Incremental-0001',
        'volstatus': 'Append',
        'pool_name': 'Incremental Pool',
        'storageid': 1,
        'mediatype': 'File',
        'volbytes': 3221225472,  # 3 GB
        'volfiles': 55000,
        'lastwritten': '2023-04-18 03:10:15'
    },
    {
        'mediaid': 4,
        'volumename': 'Full-0003',
        'volstatus': 'Full',
        'pool_name': 'Full Pool',
        'storageid': 2,
        'mediatype': 'File',
        'volbytes': 16106127360,  # 15 GB
        'volfiles': 260000,
        'lastwritten': '2023-04-16 02:10:15'
    },
    {
        'mediaid': 5,
        'volumename': 'Differential-0001',
        'volstatus': 'Append',
        'pool_name': 'Differential Pool',
        'storageid': 2,
        'mediatype': 'File',
        'volbytes': 3221225472,  # 3 GB
        'volfiles': 55000,
        'lastwritten': '2023-04-18 02:15:30'
    },
    {
        'mediaid': 6,
        'volumename': 'Full-0004',
        'volstatus': 'Full',
        'pool_name': 'Full Pool',
        'storageid': 3,
        'mediatype': 'File',
        'volbytes': 17179869184,  # 16 GB
        'volfiles': 275000,
        'lastwritten': '2023-04-01 02:30:45'
    },
    {
        'mediaid': 7,
        'volumename': 'Differential-0002',
        'volstatus': 'Append',
        'pool_name': 'Differential Pool',
        'storageid': 3,
        'mediatype': 'File',
        'volbytes': 3221225472,  # 3 GB
        'volfiles': 45000,
        'lastwritten': '2023-04-17 04:20:30'
    },
    {
        'mediaid': 8,
        'volumename': 'Full-0005',
        'volstatus': 'Append',
        'pool_name': 'Full Pool',
        'storageid': 1,
        'mediatype': 'File',
        'volbytes': 1073741824,  # 1 GB
        'volfiles': 15000,
        'lastwritten': '2023-04-17 05:00:00'
    },
    {
        'mediaid': 9,
        'volumename': 'Archive-0001',
        'volstatus': 'Used',
        'pool_name': 'Archive Pool',
        'storageid': 2,
        'mediatype': 'File',
        'volbytes': 5368709120,  # 5 GB
        'volfiles': 75000,
        'lastwritten': '2023-04-16 11:15:45'
    },
    {
        'mediaid': 10,
        'volumename': 'Scratch-0001',
        'volstatus': 'Append',
        'pool_name': 'Scratch Pool',
        'storageid': 3,
        'mediatype': 'File',
        'volbytes': 0,
        'volfiles': 0,
        'lastwritten': None
    }
]


@storage_bp.route('/status/<int:storage_id>')
def storage_status(storage_id):
    """
    Display detailed status information for a specific storage device
    """
    # Find the storage by ID
    storage = next((s for s in sample_storage if s['storageid'] == storage_id), None)
    if not storage:
        flash('Storage device not found', 'danger')
        return redirect(url_for('storage.index'))
    
    # Get volumes for this storage
    volumes = [vol for vol in sample_volumes if vol['storageid'] == storage_id]
    
    # Calculate storage statistics
    total_bytes = sum(vol['volbytes'] for vol in volumes)
    total_files = sum(vol['volfiles'] for vol in volumes)
    
    # Generate usage history data (last 30 days)
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    usage_data = []
    
    # Generate random increasing usage data
    current_usage = 0.3  # Start at 30% usage
    for i in range(30):
        # Add a small random amount each day (between -1% and +3%)
        change = random.uniform(-0.01, 0.03)
        current_usage += change
        # Keep within reasonable bounds
        current_usage = max(0.1, min(0.95, current_usage))
        usage_data.append(current_usage)
    
    # Generate volume usage data for pie chart
    volume_labels = [vol['volumename'] for vol in volumes[:10]]  # Limit to 10 volumes
    volume_data = [vol['volbytes'] for vol in volumes[:10]]
    
    # Generate random colors for the pie chart
    def random_color():
        return f"rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.8)"
    
    volume_colors = [random_color() for _ in volume_labels]
    
    # Generate recent jobs that used this storage
    recent_jobs = []
    for job in sample_jobs:
        if job.get('storageid') == storage_id:
            recent_jobs.append(job)
    
    # Sort by start time and limit to 10
    recent_jobs = sorted(recent_jobs, key=lambda x: x['starttime'], reverse=True)[:10]
    
    return render_template('storage/status.html',
                          storage=storage,
                          volumes=volumes,
                          total_bytes=total_bytes,
                          total_files=total_files,
                          dates=dates,
                          usage_data=usage_data,
                          volume_labels=volume_labels,
                          volume_data=volume_data,
                          volume_colors=volume_colors,
                          recent_jobs=recent_jobs,
                          format_bytes=format_bytes)