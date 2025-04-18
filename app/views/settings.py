# app/routes/settings.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import os
import json

# Create blueprint
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

# Sample settings data for demonstration
sample_settings = {
    'general': {
        'company_name': 'Acme Corporation',
        'admin_email': 'admin@example.com',
        'retention_period': 30,
        'job_timeout': 3600,
        'max_concurrent_jobs': 5,
        'debug_level': 1,
        'timezone': 'UTC',
        'language': 'en_US',
        'notifications_enabled': True,
        'theme': 'default'
    },
    'email': {
        'smtp_server': 'smtp.example.com',
        'smtp_port': 587,
        'smtp_user': 'backup@example.com',
        'smtp_password': '********',
        'from_email': 'backup@example.com',
        'use_tls': True,
        'send_job_report': True,
        'send_error_only': False,
        'admin_recipients': 'admin@example.com, manager@example.com'
    },
    'backup': {
        'default_pool': 'Default',
        'default_storage': 'File1',
        'default_fileset': 'Full-Set',
        'default_schedule': 'Daily-Incremental',
        'heartbeat_interval': 180,
        'max_volume_size': 5368709120,  # 5GB in bytes
        'max_volume_jobs': 100,
        'max_volume_files': 1000000,
        'auto_prune': True,
        'auto_recycle': True
    },
    'restore': {
        'restore_job_prefix': 'restore-',
        'restore_location': '/tmp/bacula-restores',
        'replace_option': 'always',
        'client_restore_privileges': False,
        'max_concurrent_restores': 2
    },
    'security': {
        'director_name': 'bacula-dir',
        'director_password': '********',
        'console_password': '********',
        'client_connection_timeout': 300,
        'require_ssl': True,
        'allowed_clients': '*',
        'restricted_commands': 'delete, prune'
    }
}

# Routes
@settings_bp.route('/')
def index():
    return redirect(url_for('settings.general'))

@settings_bp.route('/general', methods=['GET', 'POST'])
def general():
    if request.method == 'POST':
        try:
            # Process form data
            sample_settings['general']['company_name'] = request.form['company_name']
            sample_settings['general']['admin_email'] = request.form['admin_email']
            sample_settings['general']['retention_period'] = int(request.form['retention_period'])
            sample_settings['general']['job_timeout'] = int(request.form['job_timeout'])
            sample_settings['general']['max_concurrent_jobs'] = int(request.form['max_concurrent_jobs'])
            sample_settings['general']['debug_level'] = int(request.form['debug_level'])
            sample_settings['general']['timezone'] = request.form['timezone']
            sample_settings['general']['language'] = request.form['language']
            sample_settings['general']['notifications_enabled'] = 'notifications_enabled' in request.form
            sample_settings['general']['theme'] = request.form['theme']
            
            # In a real app, you would save these settings to a database or config file
            flash('General settings saved successfully!', 'success')
            return redirect(url_for('settings.general'))
            
        except Exception as e:
            flash(f'Error saving settings: {str(e)}', 'danger')
    
    return render_template('settings/general.html', settings=sample_settings)

@settings_bp.route('/email', methods=['GET', 'POST'])
def email():
    if request.method == 'POST':
        try:
            # Process form data
            sample_settings['email']['smtp_server'] = request.form['smtp_server']
            sample_settings['email']['smtp_port'] = int(request.form['smtp_port'])
            sample_settings['email']['smtp_user'] = request.form['smtp_user']
            
            # Only update password if provided
            if request.form['smtp_password'] and request.form['smtp_password'] != '********':
                sample_settings['email']['smtp_password'] = request.form['smtp_password']
                
            sample_settings['email']['from_email'] = request.form['from_email']
            sample_settings['email']['use_tls'] = 'use_tls' in request.form
            sample_settings['email']['send_job_report'] = 'send_job_report' in request.form
            sample_settings['email']['send_error_only'] = 'send_error_only' in request.form
            sample_settings['email']['admin_recipients'] = request.form['admin_recipients']
            
            # In a real app, you would save these settings to a database or config file
            flash('Email settings saved successfully!', 'success')
            return redirect(url_for('settings.email'))
            
        except Exception as e:
            flash(f'Error saving email settings: {str(e)}', 'danger')
    
    return render_template('settings/email.html', settings=sample_settings)

@settings_bp.route('/backup', methods=['GET', 'POST'])
def backup():
    if request.method == 'POST':
        try:
            # Process form data
            sample_settings['backup']['default_pool'] = request.form['default_pool']
            sample_settings['backup']['default_storage'] = request.form['default_storage']
            sample_settings['backup']['default_fileset'] = request.form['default_fileset']
            sample_settings['backup']['default_schedule'] = request.form['default_schedule']
            sample_settings['backup']['heartbeat_interval'] = int(request.form['heartbeat_interval'])
            sample_settings['backup']['max_volume_size'] = int(float(request.form['max_volume_size']) * 1024 * 1024 * 1024)  # Convert GB to bytes
            sample_settings['backup']['max_volume_jobs'] = int(request.form['max_volume_jobs'])
            sample_settings['backup']['max_volume_files'] = int(request.form['max_volume_files'])
            sample_settings['backup']['auto_prune'] = 'auto_prune' in request.form
            sample_settings['backup']['auto_recycle'] = 'auto_recycle' in request.form
            
            # In a real app, you would save these settings to a database or config file
            flash('Backup settings saved successfully!', 'success')
            return redirect(url_for('settings.backup'))
            
        except Exception as e:
            flash(f'Error saving backup settings: {str(e)}', 'danger')
    
    # Sample data for dropdowns
    pools = ['Default', 'Full', 'Incremental', 'Differential']
    storages = ['File1', 'File2', 'Tape1', 'Cloud1']
    filesets = ['Full-Set', 'System-Config', 'User-Data', 'Web-Data', 'Database-Backup']
    schedules = ['Daily-Incremental', 'Weekly-Full', 'Monthly-Archive', 'Quarterly-Offsite', 'Hourly-Critical']
    
    return render_template(
        'settings/backup.html', 
        settings=sample_settings, 
        pools=pools, 
        storages=storages, 
        filesets=filesets, 
        schedules=schedules
    )

@settings_bp.route('/restore', methods=['GET', 'POST'])
def restore():
    if request.method == 'POST':
        try:
            # Process form data
            sample_settings['restore']['restore_job_prefix'] = request.form['restore_job_prefix']
            sample_settings['restore']['restore_location'] = request.form['restore_location']
            sample_settings['restore']['replace_option'] = request.form['replace_option']
            sample_settings['restore']['client_restore_privileges'] = 'client_restore_privileges' in request.form
            sample_settings['restore']['max_concurrent_restores'] = int(request.form['max_concurrent_restores'])
            
            # In a real app, you would save these settings to a database or config file
            flash('Restore settings saved successfully!', 'success')
            return redirect(url_for('settings.restore'))
            
        except Exception as e:
            flash(f'Error saving restore settings: {str(e)}', 'danger')
    
    return render_template('settings/restore.html', settings=sample_settings)

@settings_bp.route('/security', methods=['GET', 'POST'])
def security():
    if request.method == 'POST':
        try:
            # Process form data
            sample_settings['security']['director_name'] = request.form['director_name']
            
            # Only update passwords if provided
            if request.form['director_password'] and request.form['director_password'] != '********':
                sample_settings['security']['director_password'] = request.form['director_password']
                
            if request.form['console_password'] and request.form['console_password'] != '********':
                sample_settings['security']['console_password'] = request.form['console_password']
                
            sample_settings['security']['client_connection_timeout'] = int(request.form['client_connection_timeout'])
            sample_settings['security']['require_ssl'] = 'require_ssl' in request.form
            sample_settings['security']['allowed_clients'] = request.form['allowed_clients']
            sample_settings['security']['restricted_commands'] = request.form['restricted_commands']
            
            # In a real app, you would save these settings to a database or config file
            flash('Security settings saved successfully!', 'success')
            return redirect(url_for('settings.security'))
            
        except Exception as e:
            flash(f'Error saving security settings: {str(e)}', 'danger')
    
    return render_template('settings/security.html', settings=sample_settings)

@settings_bp.route('/export')
def export():
    # In a real app, you would fetch the actual settings
    settings_json = json.dumps(sample_settings, indent=2)
    return render_template('settings/export.html', settings_json=settings_json)

@settings_bp.route('/import', methods=['GET', 'POST'])
def import_settings():
    if request.method == 'POST':
        try:
            if 'settings_file' not in request.files:
                flash('No file selected', 'danger')
                return redirect(url_for('settings.import_settings'))
                
            file = request.files['settings_file']
            
            if file.filename == '':
                flash('No file selected', 'danger')
                return redirect(url_for('settings.import_settings'))
                
            if file:
                # Read and parse the JSON file
                settings_data = json.loads(file.read().decode('utf-8'))
                
                # In a real app, you would validate the settings and save them
                global sample_settings
                sample_settings = settings_data
                
                flash('Settings imported successfully!', 'success')
                return redirect(url_for('settings.general'))
                
        except json.JSONDecodeError:
            flash('Invalid JSON file', 'danger')
        except Exception as e:
            flash(f'Error importing settings: {str(e)}', 'danger')
    
    return render_template('settings/import.html')

@settings_bp.route('/test_email', methods=['POST'])
def test_email():
    # In a real app, you would actually send a test email
    # For now, we'll just simulate success
    flash('Test email sent successfully!', 'success')
    return redirect(url_for('settings.email'))
# Add this to app/routes/settings.py

# Add to the sample_settings dictionary:
sample_settings['director'] = {
    'name': 'bacula-dir',
    'address': 'localhost',
    'port': 9101,
    'working_directory': '/var/lib/bacula',
    'pid_directory': '/var/run',
    'maximum_concurrent_jobs': 10,
    'messages': 'Standard',
    'query_file': '/etc/bacula/query.sql',
    'heartbeat_interval': 30,
    'statistics_retention': 30,
    'maximum_volume_jobs': 100,
    'maximum_volume_files': 1000000,
    'maximum_volume_bytes': 50000000000,  # 50GB
    'catalog_retention': 60,  # days
    'auto_prune': True,
    'auto_recycle': True
}

# Add this route to the settings_bp blueprint
@settings_bp.route('/director', methods=['GET', 'POST'])
def director():
    if request.method == 'POST':
        try:
            # Process form data
            sample_settings['director']['name'] = request.form['name']
            sample_settings['director']['address'] = request.form['address']
            sample_settings['director']['port'] = int(request.form['port'])
            sample_settings['director']['working_directory'] = request.form['working_directory']
            sample_settings['director']['pid_directory'] = request.form['pid_directory']
            sample_settings['director']['maximum_concurrent_jobs'] = int(request.form['maximum_concurrent_jobs'])
            sample_settings['director']['messages'] = request.form['messages']
            sample_settings['director']['query_file'] = request.form['query_file']
            sample_settings['director']['heartbeat_interval'] = int(request.form['heartbeat_interval'])
            sample_settings['director']['statistics_retention'] = int(request.form['statistics_retention'])
            sample_settings['director']['maximum_volume_jobs'] = int(request.form['maximum_volume_jobs'])
            sample_settings['director']['maximum_volume_files'] = int(request.form['maximum_volume_files'])
            sample_settings['director']['maximum_volume_bytes'] = int(float(request.form['maximum_volume_bytes']) * 1000000000)  # Convert GB to bytes
            sample_settings['director']['catalog_retention'] = int(request.form['catalog_retention'])
            sample_settings['director']['auto_prune'] = 'auto_prune' in request.form
            sample_settings['director']['auto_recycle'] = 'auto_recycle' in request.form
            
            # In a real app, you would save these settings to a database or config file
            flash('Director settings saved successfully!', 'success')
            return redirect(url_for('settings.director'))
            
        except Exception as e:
            flash(f'Error saving director settings: {str(e)}', 'danger')
    
    # Sample message types for the dropdown
    message_types = ['Standard', 'Daemon', 'Verbose', 'Debug', 'All']
    
    return render_template(
        'settings/director.html', 
        settings=sample_settings,
        message_types=message_types
    )
# Add this function to app/routes/settings.py

@settings_bp.route('/director/export-config')
def export_director_config():
    # Generate Bacula Director configuration based on settings
        config = f"""#
    # Bacula Director Configuration
    # Generated by Bacula Dashboard on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    #

    Director {{
    Name = "{sample_settings['director']['name']}"
    DIRport = {sample_settings['director']['port']}
    QueryFile = "{sample_settings['director']['query_file']}"
    WorkingDirectory = "{sample_settings['director']['working_directory']}"
    PidDirectory = "{sample_settings['director']['pid_directory']}"
    Maximum Concurrent Jobs = {sample_settings['director']['maximum_concurrent_jobs']}
    Password = "{sample_settings['security']['director_password']}"
    Messages = {sample_settings['director']['messages']}
    Heartbeat Interval = {sample_settings['director']['heartbeat_interval']}
    """

        if sample_settings['director']['auto_prune']:
            config += "  AutoPrune = yes\n"
        else:
            config += "  AutoPrune = no\n"
            
        config += f"""  Statistics Retention = {sample_settings['director']['statistics_retention']} days
    }}

    # Catalog section
    Catalog {{
    Name = MyCatalog
    dbname = "bacula"; dbuser = "bacula"; dbpassword = "password"
    }}

    # Standard message resource
    Messages {{
    Name = Standard
    mailcommand = "/usr/sbin/bsmtp -h {sample_settings['email']['smtp_server']} -f \\\"(Bacula) \\\" -s \\"Bacula: %t %e of %c %l\\" %r"
    operatorcommand = "/usr/sbin/bsmtp -h {sample_settings['email']['smtp_server']} -f \\\"(Bacula) \\\" -s \\"Bacula: Intervention needed for %j\\" %r"
    mail = {sample_settings['email']['admin_recipients']} = all, !skipped
    operator = {sample_settings['email']['admin_recipients']} = mount
    console = all, !skipped, !saved
    append = "/var/log/bacula/bacula.log" = all, !skipped
    catalog = all
    }}

    # Default pool definition
    Pool {{
    Name = Default
    Pool Type = Backup
    Recycle = yes
    AutoPrune = {sample_settings['director']['auto_prune']}
    Volume Retention = {sample_settings['general']['retention_period']} days
    Maximum Volume Jobs = {sample_settings['director']['maximum_volume_jobs']}
    Maximum Volume Bytes = {sample_settings['director']['maximum_volume_bytes']}
    Maximum Volume Files = {sample_settings['director']['maximum_volume_files']}
    }}

    # Example of a standard schedule
    Schedule {{
    Name = "WeeklyCycle"
    Run = Full 1st sun at 23:05
    Run = Differential 2nd-5th sun at 23:05
    Run = Incremental mon-sat at 23:05
    }}

    # Example of a FileSet
    FileSet {{
    Name = "Full Set"
    Include {{
        Options {{
        signature = MD5
        compression = GZIP
        }}
        File = /
    }}
    Exclude {{
        File = /var/lib/bacula
        File = /proc
        File = /tmp
        File = /.journal
        File = /.fsck
    }}
    }}

    # Example Job definition
    Job {{
    Name = "BackupClient1"
    JobDefs = "DefaultJob"
    Client = client1-fd
    }}

    # Default job definition
    JobDefs {{
    Name = "DefaultJob"
    Type = Backup
    Level = Incremental
    FileSet = "Full Set"
    Schedule = "WeeklyCycle"
    Storage = File1
    Messages = Standard
    Pool = Default
    Priority = 10
    Write Bootstrap = "{sample_settings['director']['working_directory']}/bootstrap/%c.bsr"
    }}

    # Example Storage definition
    Storage {{
    Name = File1
    Address = localhost
    SDPort = 9103
    Password = "storage-password"
    Device = FileStorage
    Media Type = File
    }}

    # Example Client definition
    Client {{
    Name = client1-fd
    Address = client1.example.com
    FDPort = 9102
    Catalog = MyCatalog
    Password = "client-password"
    File Retention = 30 days
    Job Retention = 6 months
    AutoPrune = {sample_settings['director']['auto_prune']}
    }}
    """
        
        return render_template('settings/export_director_config.html', config=config)

# Add this to app/routes/settings.py

# Add to the sample_settings dictionary:
sample_settings['users'] = {
    'require_email_verification': True,
    'password_policy': {
        'min_length': 8,
        'require_uppercase': True,
        'require_lowercase': True,
        'require_numbers': True,
        'require_special': True
    },
    'session_timeout': 30,  # minutes
    'max_login_attempts': 5,
    'lockout_duration': 15,  # minutes
    'default_role': 'operator'
}

# Sample users data
sample_users = [
    {
        'id': 1,
        'username': 'admin',
        'email': 'admin@example.com',
        'full_name': 'Administrator',
        'role': 'admin',
        'active': True,
        'last_login': datetime.now() - timedelta(days=1, hours=3),
        'created_at': datetime.now() - timedelta(days=180)
    },
    {
        'id': 2,
        'username': 'operator',
        'email': 'operator@example.com',
        'full_name': 'Backup Operator',
        'role': 'operator',
        'active': True,
        'last_login': datetime.now() - timedelta(hours=5),
        'created_at': datetime.now() - timedelta(days=90)
    },
    {
        'id': 3,
        'username': 'viewer',
        'email': 'viewer@example.com',
        'full_name': 'Report Viewer',
        'role': 'viewer',
        'active': True,
        'last_login': datetime.now() - timedelta(days=3),
        'created_at': datetime.now() - timedelta(days=60)
    },
    {
        'id': 4,
        'username': 'inactive_user',
        'email': 'inactive@example.com',
        'full_name': 'Inactive User',
        'role': 'operator',
        'active': False,
        'last_login': datetime.now() - timedelta(days=45),
        'created_at': datetime.now() - timedelta(days=120)
    }
]

# Sample roles data
sample_roles = [
    {
        'name': 'admin',
        'description': 'Full administrative access',
        'permissions': ['manage_users', 'manage_settings', 'manage_backups', 'manage_restores', 'view_logs', 'view_reports']
    },
    {
        'name': 'operator',
        'description': 'Can manage backups and restores',
        'permissions': ['manage_backups', 'manage_restores', 'view_logs', 'view_reports']
    },
    {
        'name': 'viewer',
        'description': 'Read-only access to logs and reports',
        'permissions': ['view_logs', 'view_reports']
    }
]

# Add these routes to the settings_bp blueprint
@settings_bp.route('/users', methods=['GET'])
def users():
    return render_template('settings/users/index.html', users=sample_users, settings=sample_settings)

@settings_bp.route('/users/settings', methods=['GET', 'POST'])
def users_settings():
    if request.method == 'POST':
        try:
            # Process form data
            sample_settings['users']['require_email_verification'] = 'require_email_verification' in request.form
            sample_settings['users']['password_policy']['min_length'] = int(request.form['min_length'])
            sample_settings['users']['password_policy']['require_uppercase'] = 'require_uppercase' in request.form
            sample_settings['users']['password_policy']['require_lowercase'] = 'require_lowercase' in request.form
            sample_settings['users']['password_policy']['require_numbers'] = 'require_numbers' in request.form
            sample_settings['users']['password_policy']['require_special'] = 'require_special' in request.form
            sample_settings['users']['session_timeout'] = int(request.form['session_timeout'])
            sample_settings['users']['max_login_attempts'] = int(request.form['max_login_attempts'])
            sample_settings['users']['lockout_duration'] = int(request.form['lockout_duration'])
            sample_settings['users']['default_role'] = request.form['default_role']
            
            # In a real app, you would save these settings to a database or config file
            flash('User settings saved successfully!', 'success')
            return redirect(url_for('settings.users_settings'))
            
        except Exception as e:
            flash(f'Error saving user settings: {str(e)}', 'danger')
    
    return render_template('settings/users/settings.html', settings=sample_settings, roles=sample_roles)

@settings_bp.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        try:
            # Process form data
            username = request.form['username']
            email = request.form['email']
            full_name = request.form['full_name']
            role = request.form['role']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            # Basic validation
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return render_template('settings/users/add.html', roles=sample_roles)
            
            # In a real app, you would create a new user in the database
            # Here we'll just simulate success
            
            flash('User added successfully!', 'success')
            return redirect(url_for('settings.users'))
            
        except Exception as e:
            flash(f'Error adding user: {str(e)}', 'danger')
    
    return render_template('settings/users/add.html', roles=sample_roles)

@settings_bp.route('/users/<int:user_id>', methods=['GET'])
def view_user(user_id):
    # Find the user by ID
    user = next((u for u in sample_users if u['id'] == user_id), None)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('settings.users'))
    
    return render_template('settings/users/view.html', user=user, roles=sample_roles)

@settings_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    # Find the user by ID
    user = next((u for u in sample_users if u['id'] == user_id), None)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('settings.users'))
    
    if request.method == 'POST':
        try:
            # Process form data
            user['username'] = request.form['username']
            user['email'] = request.form['email']
            user['full_name'] = request.form['full_name']
            user['role'] = request.form['role']
            user['active'] = 'active' in request.form
            
            # Check if password is being updated
            if request.form['password'] and request.form['confirm_password']:
                if request.form['password'] != request.form['confirm_password']:
                    flash('Passwords do not match', 'danger')
                    return render_template('settings/users/edit.html', user=user, roles=sample_roles)
            
            # In a real app, you would update the user in the database
            flash('User updated successfully!', 'success')
            return redirect(url_for('settings.view_user', user_id=user_id))
            
        except Exception as e:
            flash(f'Error updating user: {str(e)}', 'danger')
    
    return render_template('settings/users/edit.html', user=user, roles=sample_roles)

@settings_bp.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    # In a real app, you would delete or deactivate the user in the database
    flash('User deleted successfully!', 'success')
    return redirect(url_for('settings.users'))

@settings_bp.route('/users/roles', methods=['GET'])
def roles():
    return render_template('settings/users/roles.html', roles=sample_roles)

@settings_bp.route('/users/roles/add', methods=['GET', 'POST'])
def add_role():
    if request.method == 'POST':
        try:
            # Process form data
            name = request.form['name']
            description = request.form['description']
            
            # Get selected permissions
            permissions = []
            all_permissions = ['manage_users', 'manage_settings', 'manage_backups', 'manage_restores', 'view_logs', 'view_reports']
            for perm in all_permissions:
                if perm in request.form:
                    permissions.append(perm)
            
            # In a real app, you would create a new role in the database
            # Here we'll just simulate success
            
            flash('Role added successfully!', 'success')
            return redirect(url_for('settings.roles'))
            
        except Exception as e:
            flash(f'Error adding role: {str(e)}', 'danger')
    
    # List of all available permissions
    all_permissions = [
        {'name': 'manage_users', 'description': 'Create, edit, and delete users'},
        {'name': 'manage_settings', 'description': 'Modify system settings'},
        {'name': 'manage_backups', 'description': 'Run and manage backup jobs'},
        {'name': 'manage_restores', 'description': 'Run and manage restore jobs'},
        {'name': 'view_logs', 'description': 'View system and job logs'},
        {'name': 'view_reports', 'description': 'View reports and statistics'}
    ]
    
    return render_template('settings/users/add_role.html', permissions=all_permissions)

@settings_bp.route('/users/roles/<role_name>/edit', methods=['GET', 'POST'])
def edit_role(role_name):
    # Find the role by name
    role = next((r for r in sample_roles if r['name'] == role_name), None)
    if not role:
        flash('Role not found', 'danger')
        return redirect(url_for('settings.roles'))
    
    if request.method == 'POST':
        try:
            # Process form data
            role['description'] = request.form['description']
            
            # Get selected permissions
            role['permissions'] = []
            all_permissions = ['manage_users', 'manage_settings', 'manage_backups', 'manage_restores', 'view_logs', 'view_reports']
            for perm in all_permissions:
                if perm in request.form:
                    role['permissions'].append(perm)
            
            # In a real app, you would update the role in the database
            flash('Role updated successfully!', 'success')
            return redirect(url_for('settings.roles'))
            
        except Exception as e:
            flash(f'Error updating role: {str(e)}', 'danger')
    
    # List of all available permissions
    all_permissions = [
        {'name': 'manage_users', 'description': 'Create, edit, and delete users'},
        {'name': 'manage_settings', 'description': 'Modify system settings'},
        {'name': 'manage_backups', 'description': 'Run and manage backup jobs'},
        {'name': 'manage_restores', 'description': 'Run and manage restore jobs'},
        {'name': 'view_logs', 'description': 'View system and job logs'},
        {'name': 'view_reports', 'description': 'View reports and statistics'}
    ]
    
    return render_template('settings/users/edit_role.html', role=role, permissions=all_permissions)

@settings_bp.route('/users/roles/<role_name>/delete', methods=['POST'])
def delete_role(role_name):
    # In a real app, you would delete the role from the database
    flash('Role deleted successfully!', 'success')
    return redirect(url_for('settings.roles'))



# NOTIFICATION Settings
sample_settings['notifications'] = {
    'email': {
        'enabled': True,
        'send_job_success': True,
        'send_job_error': True,
        'send_job_warning': True,
        'send_volume_warning': True,
        'send_catalog_warning': True,
        'daily_report': True,
        'weekly_report': True,
        'monthly_report': False
    },
    'web': {
        'enabled': True,
        'job_notifications': True,
        'system_notifications': True,
        'admin_notifications': True,
        'keep_days': 30
    },
    'sms': {
        'enabled': False,
        'provider': 'twilio',
        'account_sid': '',
        'auth_token': '',
        'from_number': '',
        'to_numbers': '',
        'only_critical': True
    },
    'slack': {
        'enabled': False,
        'webhook_url': '',
        'channel': '#backups',
        'username': 'Bacula Bot',
        'icon_emoji': ':floppy_disk:',
        'detailed_messages': True
    },
    'telegram': {
        'enabled': False,
        'bot_token': '',
        'chat_id': '',
        'only_critical': True
    }
}

# Add these routes to the settings_bp blueprint
@settings_bp.route('/notifications', methods=['GET'])
def notifications():
    return render_template('settings/notifications/index.html', settings=sample_settings)

@settings_bp.route('/notifications/email', methods=['GET', 'POST'])
def notifications_email():
    if request.method == 'POST':
        try:
            # Process form data
            sample_settings['notifications']['email']['enabled'] = 'enabled' in request.form
            sample_settings['notifications']['email']['send_job_success'] = 'send_job_success' in request.form
            sample_settings['notifications']['email']['send_job_error'] = 'send_job_error' in request.form
            sample_settings['notifications']['email']['send_job_warning'] = 'send_job_warning' in request.form
            sample_settings['notifications']['email']['send_volume_warning'] = 'send_volume_warning' in request.form
            sample_settings['notifications']['email']['send_catalog_warning'] = 'send_catalog_warning' in request.form
            sample_settings['notifications']['email']['daily_report'] = 'daily_report' in request.form
            sample_settings['notifications']['email']['weekly_report'] = 'weekly_report' in request.form
            sample_settings['notifications']['email']['monthly_report'] = 'monthly_report' in request.form
            
            # In a real app, you would save these settings to a database or config file
            flash('Email notification settings saved successfully!', 'success')
            return redirect(url_for('settings.notifications_email'))
            
        except Exception as e:
            flash(f'Error saving email notification settings: {str(e)}', 'danger')
    
    return render_template('settings/notifications/email.html', settings=sample_settings)

@settings_bp.route('/notifications/web', methods=['GET', 'POST'])
def notifications_web():
    if request.method == 'POST':
        try:
            # Process form data
            sample_settings['notifications']['web']['enabled'] = 'enabled' in request.form
            sample_settings['notifications']['web']['job_notifications'] = 'job_notifications' in request.form
            sample_settings['notifications']['web']['system_notifications'] = 'system_notifications' in request.form
            sample_settings['notifications']['web']['admin_notifications'] = 'admin_notifications' in request.form
            sample_settings['notifications']['web']['keep_days'] = int(request.form['keep_days'])
            
            # In a real app, you would save these settings to a database or config file
            flash('Web notification settings saved successfully!', 'success')
            return redirect(url_for('settings.notifications_web'))
            
        except Exception as e:
            flash(f'Error saving web notification settings: {str(e)}', 'danger')
    
    return render_template('settings/notifications/web.html', settings=sample_settings)

@settings_bp.route('/notifications/sms', methods=['GET', 'POST'])
def notifications_sms():
    if request.method == 'POST':
        try:
            # Process form data
            sample_settings['notifications']['sms']['enabled'] = 'enabled' in request.form
            sample_settings['notifications']['sms']['provider'] = request.form['provider']
            sample_settings['notifications']['sms']['account_sid'] = request.form['account_sid']
            
            # Only update auth token if provided
            if request.form['auth_token'] and request.form['auth_token'] != '********':
                sample_settings['notifications']['sms']['auth_token'] = request.form['auth_token']
                
            sample_settings['notifications']['sms']['from_number'] = request.form['from_number']
            sample_settings['notifications']['sms']['to_numbers'] = request.form['to_numbers']
            sample_settings['notifications']['sms']['only_critical'] = 'only_critical' in request.form
            
            # In a real app, you would save these settings to a database or config file
            flash('SMS notification settings saved successfully!', 'success')
            return redirect(url_for('settings.notifications_sms'))
            
        except Exception as e:
            flash(f'Error saving SMS notification settings: {str(e)}', 'danger')
    
    return render_template('settings/notifications/sms.html', settings=sample_settings)

@settings_bp.route('/notifications/slack', methods=['GET', 'POST'])
def notifications_slack():
    if request.method == 'POST':
        try:
            # Process form data
            sample_settings['notifications']['slack']['enabled'] = 'enabled' in request.form
            sample_settings['notifications']['slack']['webhook_url'] = request.form['webhook_url']
            sample_settings['notifications']['slack']['channel'] = request.form['channel']
            sample_settings['notifications']['slack']['username'] = request.form['username']
            sample_settings['notifications']['slack']['icon_emoji'] = request.form['icon_emoji']
            sample_settings['notifications']['slack']['detailed_messages'] = 'detailed_messages' in request.form
            
            # In a real app, you would save these settings to a database or config file
            flash('Slack notification settings saved successfully!', 'success')
            return redirect(url_for('settings.notifications_slack'))
            
        except Exception as e:
            flash(f'Error saving Slack notification settings: {str(e)}', 'danger')
    
    return render_template('settings/notifications/slack.html', settings=sample_settings)

@settings_bp.route('/notifications/telegram', methods=['GET', 'POST'])
def notifications_telegram():
    if request.method == 'POST':
        try:
            # Process form data
            sample_settings['notifications']['telegram']['enabled'] = 'enabled' in request.form
            sample_settings['notifications']['telegram']['bot_token'] = request.form['bot_token']
            sample_settings['notifications']['telegram']['chat_id'] = request.form['chat_id']
            sample_settings['notifications']['telegram']['only_critical'] = 'only_critical' in request.form
            
            # In a real app, you would save these settings to a database or config file
            flash('Telegram notification settings saved successfully!', 'success')
            return redirect(url_for('settings.notifications_telegram'))
            
        except Exception as e:
            flash(f'Error saving Telegram notification settings: {str(e)}', 'danger')
    
    return render_template('settings/notifications/telegram.html', settings=sample_settings)

@settings_bp.route('/notifications/test/<channel>', methods=['POST'])
def test_notification(channel):
    # In a real app, you would actually send a test notification
    # For now, we'll just simulate success
    flash(f'Test notification sent via {channel} successfully!', 'success')
    
    if channel == 'email':
        return redirect(url_for('settings.notifications_email'))
    elif channel == 'sms':
        return redirect(url_for('settings.notifications_sms'))
    elif channel == 'slack':
        return redirect(url_for('settings.notifications_slack'))
    elif channel == 'telegram':
        return redirect(url_for('settings.notifications_telegram'))
    else:
        return redirect(url_for('settings.notifications'))