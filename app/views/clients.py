# app/routes/clients.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import random

# Create blueprint
clients_bp = Blueprint('clients', __name__, url_prefix='/clients')

# Sample data for demonstration
sample_clients = [
    {
        'clientid': 1,
        'name': 'server1-fd',
        'address': '192.168.1.100',
        'fdport': 9102,
        'catalog': 'MyCatalog',
        'password': 'secret',
        'file_retention': 60,
        'job_retention': 180,
        'autoprune': 'yes',
        'description': 'Main web server',
        'enabled': True,
        'max_concurrent_jobs': 1,
        'heartbeat_interval': 0,
        'tls_enable': 'no',
        'tls_require': 'no',
        'status': 'online',
        'backup_state': 'backed_up_today',
        'last_backup': datetime.now() - timedelta(hours=3),
        'files': 125000,
        'bytes': 1024 * 1024 * 1024 * 5,  # 5 GB
        'jobs': 120,
        'total_jobs': 120,
        'successful_jobs': 110,
        'failed_jobs': 8,
        'running_jobs': 2,
        'total_files': 125000,
        'total_bytes': 1024 * 1024 * 1024 * 5  # 5 GB
    },
    {
        'clientid': 2,
        'name': 'db-server-fd',
        'address': '192.168.1.101',
        'fdport': 9102,
        'catalog': 'MyCatalog',
        'password': 'secret',
        'file_retention': 90,
        'job_retention': 365,
        'autoprune': 'yes',
        'description': 'Database server',
        'enabled': True,
        'max_concurrent_jobs': 1,
        'heartbeat_interval': 0,
        'tls_enable': 'yes',
        'tls_require': 'yes',
        'status': 'online',
        'backup_state': 'backed_up_today',
        'last_backup': datetime.now() - timedelta(hours=5),
        'files': 85000,
        'bytes': 1024 * 1024 * 1024 * 10,  # 10 GB
        'jobs': 90,
        'total_jobs': 90,
        'successful_jobs': 88,
        'failed_jobs': 2,
        'running_jobs': 0,
        'total_files': 85000,
        'total_bytes': 1024 * 1024 * 1024 * 10  # 10 GB
    },
    {
        'clientid': 3,
        'name': 'fileserver-fd',
        'address': '192.168.1.102',
        'fdport': 9102,
        'catalog': 'MyCatalog',
        'password': 'secret',
        'file_retention': 30,
        'job_retention': 90,
        'autoprune': 'yes',
        'description': 'File server',
        'enabled': True,
        'max_concurrent_jobs': 2,
        'heartbeat_interval': 0,
        'tls_enable': 'no',
        'tls_require': 'no',
        'status': 'offline',
        'backup_state': 'backed_up_week',
        'last_backup': datetime.now() - timedelta(days=2),
        'files': 500000,
        'bytes': 1024 * 1024 * 1024 * 50,  # 50 GB
        'jobs': 60,
        'total_jobs': 60,
        'successful_jobs': 55,
        'failed_jobs': 5,
        'running_jobs': 0,
        'total_files': 500000,
        'total_bytes': 1024 * 1024 * 1024 * 50  # 50 GB
    },
    {
        'clientid': 4,
        'name': 'workstation-fd',
        'address': '192.168.1.103',
        'fdport': 9102,
        'catalog': 'MyCatalog',
        'password': 'secret',
        'file_retention': 30,
        'job_retention': 60,
        'autoprune': 'yes',
        'description': 'Developer workstation',
        'enabled': True,
        'max_concurrent_jobs': 1,
        'heartbeat_interval': 0,
        'tls_enable': 'no',
        'tls_require': 'no',
        'status': 'offline',
        'backup_state': 'never_backed_up',
        'last_backup': None,
        'files': 0,
        'bytes': 0,
        'jobs': 0,
        'total_jobs': 0,
        'successful_jobs': 0,
        'failed_jobs': 0,
        'running_jobs': 0,
        'total_files': 0,
        'total_bytes': 0
    }
]

# Sample jobs data
sample_jobs = [
    {
        'jobid': 1001,
        'name': 'server1-fd_backup',
        'type': 'B',
        'level': 'F',
        'clientid': 1,
        'starttime': datetime.now() - timedelta(hours=3),
        'endtime': datetime.now() - timedelta(hours=2, minutes=45),
        'jobstatus': 'T',
        'jobfiles': 125000,
        'jobbytes': 1024 * 1024 * 1024 * 5,  # 5 GB
        'progress': 100
    },
    {
        'jobid': 1002,
        'name': 'server1-fd_backup',
        'type': 'B',
        'level': 'I',
        'clientid': 1,
        'starttime': datetime.now() - timedelta(minutes=30),
        'endtime': None,
        'jobstatus': 'R',
        'jobfiles': 5000,
        'jobbytes': 1024 * 1024 * 500,  # 500 MB
        'progress': 65
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

# Helper function to format duration
def format_duration(duration):
    total_seconds = duration.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

@clients_bp.route('/')
def index():
    # Calculate overall client statistics (for summary cards, if needed)
    stats = {
        'total': len(sample_clients),
        'online': sum(1 for client in sample_clients if client['status'] == 'online'),
        'backed_up_today': sum(1 for client in sample_clients if client['backup_state'] == 'backed_up_today'),
        'never_backed_up': sum(1 for client in sample_clients if client['backup_state'] == 'never_backed_up')
    }
    
    # Generate client-specific statistics as expected by the template
    client_stats = {}
    now = datetime.now()
    
    for client in sample_clients:
        # Create random stats for each client
        last_successful = None
        if client['backup_state'] != 'never_backed_up':
            # Generate a random date for the last successful backup
            days_ago = 0 if client['backup_state'] == 'backed_up_today' else random.randint(1, 10)
            last_successful = now - timedelta(days=days_ago, 
                                              hours=random.randint(0, 23), 
                                              minutes=random.randint(0, 59))
        
        total_jobs = random.randint(5, 100)
        successful_jobs = int(total_jobs * random.uniform(0.7, 0.95))  # 70-95% success rate
        failed_jobs = total_jobs - successful_jobs
        
        client_stats[client['clientid']] = {
            'total_jobs': total_jobs,
            'successful_jobs': successful_jobs,
            'failed_jobs': failed_jobs,
            'last_successful': last_successful
        }
    
    # Generate backup history data for the last 30 days
    dates = [(now - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    successful = [random.randint(3, 15) for _ in range(30)]
    failed = [random.randint(0, 2) for _ in range(30)]
    
    backup_history = {
        'labels': dates,
        'successful': successful,
        'failed': failed
    }
    
    # Generate top clients by data size
    sorted_by_data = sorted(sample_clients, key=lambda x: x['bytes'], reverse=True)[:5]
    top_clients_data = {
        'labels': [client['name'] for client in sorted_by_data],
        'data': [client['bytes'] / (1024 * 1024 * 1024) for client in sorted_by_data] # Convert to GB
    }
    
    # Generate top clients by file count
    sorted_by_files = sorted(sample_clients, key=lambda x: x['files'], reverse=True)[:5]
    top_clients_files = {
        'labels': [client['name'] for client in sorted_by_files],
        'data': [client['files'] for client in sorted_by_files]
    }
    
    return render_template('clients/index.html', 
                          clients=sample_clients, 
                          stats=stats,
                          client_stats=client_stats,
                          now=now,  # Pass the current datetime to the template
                          backup_history=backup_history,
                          top_clients_data=top_clients_data,
                          top_clients_files=top_clients_files,
                          format_bytes=format_bytes)

@clients_bp.route('/add')
def add_client():
    # Sample data for the form
    filesets = [
        {'fileset': 'Standard'},
        {'fileset': 'Windows All Drives'},
        {'fileset': 'Linux Root'},
        {'fileset': 'MySQL Backup'}
    ]
    
    return render_template('clients/add_client.html', filesets=filesets)

@clients_bp.route('/add', methods=['POST'])
def add_client_post():
    # In a real app, this would add the client to the database
    flash('Client added successfully!', 'success')
    return redirect(url_for('clients.index'))

@clients_bp.route('/<int:client_id>')
def detail(client_id):
    # Find the client by ID
    client = next((c for c in sample_clients if c['clientid'] == client_id), None)
    if not client:
        flash('Client not found', 'danger')
        return redirect(url_for('clients.index'))
    
    # Get jobs for this client
    jobs = [job for job in sample_jobs if job['clientid'] == client_id]
    
    # Calculate job statistics
    total_jobs = len(jobs)
    successful_jobs = sum(1 for job in jobs if job['jobstatus'] == 'T')
    failed_jobs = sum(1 for job in jobs if job['jobstatus'] == 'E')
    
    # If there are no jobs, create some sample data
    if not jobs:
        total_jobs = random.randint(10, 100)
        successful_jobs = int(total_jobs * random.uniform(0.7, 0.95))
        failed_jobs = total_jobs - successful_jobs
    
    # Generate backup size history data
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    bytes_data = [random.randint(50000000, 5000000000) for _ in range(30)]  # Random bytes values
    
    backup_size = {
        'labels': dates,
        'data': [b / (1024 * 1024) for b in bytes_data]  # Convert to MB for display
    }
    
    # Generate sample directories
    directories = [
        {'path': '/var/www', 'files': 50000, 'bytes': 1024 * 1024 * 1024 * 2},  # 2 GB
        {'path': '/home', 'files': 30000, 'bytes': 1024 * 1024 * 1024 * 1.5},  # 1.5 GB
        {'path': '/etc', 'files': 5000, 'bytes': 1024 * 1024 * 500},  # 500 MB
        {'path': '/var/log', 'files': 2000, 'bytes': 1024 * 1024 * 300}  # 300 MB
    ]
    
    # Generate file types data
    file_types = {
        'labels': ['Documents', 'Images', 'Videos', 'Databases', 'Other'],
        'data': [15, 25, 35, 15, 10],
        'colors': ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b'],
        'hover_colors': ['#2e59d9', '#17a673', '#2c9faf', '#dda20a', '#be2617']
    }
    
    # Get recent jobs (limit to 10)
    recent_jobs = sorted(jobs, key=lambda x: x['starttime'], reverse=True)[:10]
    
    return render_template('clients/detail.html', 
        client=client, 
        jobs=jobs,
        total_jobs=total_jobs,
        successful_jobs=successful_jobs,
        failed_jobs=failed_jobs,
        backup_size=backup_size,
        directories=directories,
        file_types=file_types,
        recent_jobs=recent_jobs,  # Added this
        dates=dates,  # Added for the chart
        bytes_data=bytes_data,  # Added for the chart
        format_bytes=format_bytes,
        format_duration=format_duration)
@clients_bp.route('/<int:client_id>/edit')
def edit_client(client_id):
    # Find the client by ID
    client = next((c for c in sample_clients if c['clientid'] == client_id), None)
    if not client:
        flash('Client not found', 'danger')
        return redirect(url_for('clients.index'))
    
    return render_template('clients/edit_client.html', client=client)

@clients_bp.route('/<int:client_id>/edit', methods=['POST'])
def edit_client_post(client_id):
    # In a real app, this would update the client in the database
    flash('Client updated successfully!', 'success')
    return redirect(url_for('clients.detail', client_id=client_id))

@clients_bp.route('/<int:client_id>/delete', methods=['POST'])
def delete_client(client_id):
    # In a real app, this would delete the client from the database
    flash('Client deleted successfully!', 'success')
    return redirect(url_for('clients.index'))

@clients_bp.route('/<int:client_id>/run_job')
def run_job(client_id):
    # Find the client by ID
    client = next((c for c in sample_clients if c['clientid'] == client_id), None)
    if not client:
        flash('Client not found', 'danger')
        return redirect(url_for('clients.index'))
    
    # Sample data for the form
    filesets = [
        {'fileset': 'Standard'},
        {'fileset': 'Windows All Drives'},
        {'fileset': 'Linux Root'},
        {'fileset': 'MySQL Backup'}
    ]
    
    pools = [
        {'name': 'Default'},
        {'name': 'Full'},
        {'name': 'Incremental'},
        {'name': 'Monthly'}
    ]
    
    storages = [
        {'name': 'File1'},
        {'name': 'Tape1'},
        {'name': 'Cloud1'}
    ]
    
    # Get recent jobs for this client
    recent_jobs = [job for job in sample_jobs if job['clientid'] == client_id]
    
    return render_template('clients/run_job.html', 
                          client=client, 
                          filesets=filesets,
                          pools=pools,
                          storages=storages,
                          recent_jobs=recent_jobs,
                          format_bytes=format_bytes)

@clients_bp.route('/<int:client_id>/run_job', methods=['POST'])
def run_job_post(client_id):
    # In a real app, this would schedule a job in Bacula
    flash('Backup job started successfully!', 'success')
    return redirect(url_for('clients.detail', client_id=client_id))

@clients_bp.route('/<int:client_id>/status')
def status(client_id):
    # Find the client by ID
    client = next((c for c in sample_clients if c['clientid'] == client_id), None)
    if not client:
        flash('Client not found', 'danger')
        return redirect(url_for('clients.index'))
    
    # Sample client info
    client_info = None
    if client['status'] == 'online':
        client_info = {
            'version': '9.6.7',
            'os': 'Ubuntu 20.04 LTS',
            'arch': 'x86_64',
            'started': datetime.now() - timedelta(days=5),
            'last_contact': datetime.now() - timedelta(minutes=5),
            'jobs_running': 1 if client['running_jobs'] > 0 else 0,
            'cpu_usage': random.randint(10, 90),
            'memory_usage': random.randint(20, 80),
            'disk_usage': [
                {'mount': '/ (root)', 'used': '15 GB', 'total': '50 GB', 'percent': 30},
                {'mount': '/home', 'used': '120 GB', 'total': '500 GB', 'percent': 24},
                {'mount': '/var', 'used': '8 GB', 'total': '20 GB', 'percent': 40}
            ],
            'network_in': f"{random.randint(50, 500)} KB/s",
            'network_out': f"{random.randint(20, 200)} KB/s"
        }
    
    # Get running jobs for this client
    running_jobs = [job for job in sample_jobs if job['clientid'] == client_id and job['jobstatus'] == 'R']
    
    return render_template('clients/status.html', 
                          client=client, 
                          client_info=client_info,
                          running_jobs=running_jobs,
                          format_bytes=format_bytes)

@clients_bp.route('/<int:client_id>/prune', methods=['POST'])
def prune_client(client_id):
    # In a real app, this would prune the client's records in Bacula
    flash('Client records pruned successfully!', 'success')
    return redirect(url_for('clients.edit_client', client_id=client_id))

@clients_bp.route('/status/all')
def status_all():
    # In a real app, this would check the status of all clients
    # For this example, we'll just return the current status
    client_status = [{'clientid': client['clientid'], 'status': client['status']} for client in sample_clients]
    return jsonify(client_status)

# Register template filters
@clients_bp.app_template_filter('format_bytes')
def _format_bytes(bytes):
    return format_bytes(bytes)

@clients_bp.app_template_filter('format_duration')
def _format_duration(duration):
    return format_duration(duration)