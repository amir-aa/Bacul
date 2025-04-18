# app/routes/filesets.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import random

# Create blueprint
filesets_bp = Blueprint('filesets', __name__, url_prefix='/filesets')

# Sample data for demonstration
sample_filesets = [
    {
        'filesetid': 1,
        'fileset': 'Full-Set',
        'md5': 'f8c3a2d5e6b7c8a9d0e1f2a3b4c5d6e7',
        'createtime': datetime.now() - timedelta(days=90),
        'is_active': True,
        'description': 'Full system backup including all user data',
        'include_paths': [
            '/etc',
            '/home',
            '/var/www',
            '/usr/local',
            '/opt'
        ],
        'exclude_paths': [
            '/home/*/tmp',
            '/home/*/.cache',
            '*.tmp',
            '*.temp',
            '*.log'
        ],
        'compression': True,
        'signature': 'MD5'
    },
    {
        'filesetid': 2,
        'fileset': 'System-Config',
        'md5': 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6',
        'createtime': datetime.now() - timedelta(days=45),
        'is_active': True,
        'description': 'System configuration files only',
        'include_paths': [
            '/etc',
            '/usr/local/etc',
            '/opt/*/etc'
        ],
        'exclude_paths': [
            '*.bak',
            '*~'
        ],
        'compression': True,
        'signature': 'SHA1'
    },
    {
        'filesetid': 3,
        'fileset': 'User-Data',
        'md5': 'd1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6',
        'createtime': datetime.now() - timedelta(days=30),
        'is_active': True,
        'description': 'User home directories only',
        'include_paths': [
            '/home'
        ],
        'exclude_paths': [
            '/home/*/tmp',
            '/home/*/.cache',
            '/home/*/Downloads',
            '/home/*/.local/share/Trash',
            '*.mp4',
            '*.avi',
            '*.mkv'
        ],
        'compression': True,
        'signature': 'MD5'
    },
    {
        'filesetid': 4,
        'fileset': 'Web-Data',
        'md5': 'e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6',
        'createtime': datetime.now() - timedelta(days=15),
        'is_active': True,
        'description': 'Web server data and configurations',
        'include_paths': [
            '/var/www',
            '/etc/nginx',
            '/etc/apache2',
            '/etc/php'
        ],
        'exclude_paths': [
            '*.log',
            '*.tmp',
            'cache/*'
        ],
        'compression': False,
        'signature': 'SHA1'
    },
    {
        'filesetid': 5,
        'fileset': 'Database-Backup',
        'md5': 'b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6',
        'createtime': datetime.now() - timedelta(days=7),
        'is_active': True,
        'description': 'Database data directories',
        'include_paths': [
            '/var/lib/mysql',
            '/var/lib/postgresql',
            '/var/lib/mongodb'
        ],
        'exclude_paths': [
            '*.pid',
            '*.sock',
            'lost+found'
        ],
        'compression': True,
        'signature': 'SHA256'
    }
]

# Routes
@filesets_bp.route('/')
def index():
    return render_template('filesets/index.html', filesets=sample_filesets)

@filesets_bp.route('/<int:fileset_id>')
def detail(fileset_id):
    # Find the fileset by ID
    fileset = next((fs for fs in sample_filesets if fs['filesetid'] == fileset_id), None)
    if not fileset:
        flash('FileSet not found', 'danger')
        return redirect(url_for('filesets.index'))
    
    return render_template('filesets/detail.html', fileset=fileset)

@filesets_bp.route('/add')
def add_fileset():
    return render_template('filesets/add_fileset.html')

@filesets_bp.route('/add', methods=['POST'])
def add_fileset_post():
    try:
        # Get form data
        name = request.form['name']
        description = request.form['description']
        include_paths = request.form['include_paths'].split('\n')
        exclude_paths = request.form['exclude_paths'].split('\n')
        compression = 'compression' in request.form
        signature = request.form['signature']
        
        # In a real application, you would add the fileset to Bacula using bconsole or API
        # For this example, we'll simulate success
        
        flash('FileSet created successfully!', 'success')
        return redirect(url_for('filesets.index'))
    
    except Exception as e:
        flash(f'Error creating FileSet: {str(e)}', 'danger')
        return redirect(url_for('filesets.add_fileset'))

@filesets_bp.route('/<int:fileset_id>/edit')
def edit_fileset(fileset_id):
    # Find the fileset by ID
    fileset = next((fs for fs in sample_filesets if fs['filesetid'] == fileset_id), None)
    if not fileset:
        flash('FileSet not found', 'danger')
        return redirect(url_for('filesets.index'))
    
    return render_template('filesets/edit_fileset.html', fileset=fileset)

@filesets_bp.route('/<int:fileset_id>/edit', methods=['POST'])
def edit_fileset_post(fileset_id):
    try:
        # Get form data
        name = request.form['name']
        description = request.form['description']
        include_paths = request.form['include_paths'].split('\n')
        exclude_paths = request.form['exclude_paths'].split('\n')
        compression = 'compression' in request.form
        signature = request.form['signature']
        
        # In a real application, you would update the fileset in Bacula
        # For this example, we'll simulate success
        
        flash('FileSet updated successfully!', 'success')
        return redirect(url_for('filesets.detail', fileset_id=fileset_id))
    
    except Exception as e:
        flash(f'Error updating FileSet: {str(e)}', 'danger')
        return redirect(url_for('filesets.edit_fileset', fileset_id=fileset_id))

@filesets_bp.route('/<int:fileset_id>/delete', methods=['POST'])
def delete_fileset(fileset_id):
    # In a real app, this would delete the fileset from Bacula
    flash('FileSet deleted successfully!', 'success')
    return redirect(url_for('filesets.index'))

@filesets_bp.route('/export/<int:fileset_id>')
def export_fileset(fileset_id):
    # Find the fileset by ID
    fileset = next((fs for fs in sample_filesets if fs['filesetid'] == fileset_id), None)
    if not fileset:
        flash('FileSet not found', 'danger')
        return redirect(url_for('filesets.index'))
    
    # Generate Bacula configuration
    config = f"""
FileSet {{
    Name = "{fileset['fileset']}"
    Description = "{fileset['description']}"
    Include {{
        Options {{
            signature = {fileset['signature']}
            {'compression = GZIP' if fileset['compression'] else '# compression disabled'}
        }}
"""
    
    for path in fileset['include_paths']:
        if path.strip():
            config += f"        File = {path.strip()}\n"
    
    config += "    }\n"
    
    if fileset['exclude_paths']:
        config += "    Exclude {\n"
        for path in fileset['exclude_paths']:
            if path.strip():
                config += f"        File = {path.strip()}\n"
        config += "    }\n"
    
    config += "}\n"
    
    # In a real app, you might return this as a downloadable file
    return render_template('filesets/export_fileset.html', fileset=fileset, config=config)