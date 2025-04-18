# app/views/config.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.bacula_models import Client, Storage, Pool, FileSet, Job
from app.utils.bacula_cmd import run_bconsole_command
import os
import tempfile

config_bp = Blueprint('config', __name__, url_prefix='/config')

@config_bp.route('/')
@login_required
def index():
    # Get summary counts
    clients_count = Client.select().count()
    filesets_count = FileSet.select(FileSet.fileset).distinct().count()
    storages_count = Storage.select().count()
    pools_count = Pool.select().count()
    
    # Get Bacula Director status
    director_status = run_bconsole_command("status director")
    
    return render_template('config/index.html',
                          clients_count=clients_count,
                          filesets_count=filesets_count,
                          storages_count=storages_count,
                          pools_count=pools_count,
                          director_status=director_status)

@config_bp.route('/filesets')
@login_required
def filesets():
    filesets = FileSet.select(FileSet.filesetid, FileSet.fileset).distinct()
    
    # Get detailed information about each fileset
    fileset_details = {}
    for fs in filesets:
        cmd = f"show fileset={fs.fileset}"
        result = run_bconsole_command(cmd)
        fileset_details[fs.fileset] = result
    
    return render_template('config/filesets.html',
                          filesets=filesets,
                          fileset_details=fileset_details)

@config_bp.route('/filesets/add', methods=['GET', 'POST'])
@login_required
def add_fileset():
    if request.method == 'POST':
        name = request.form.get('name')
        include_paths = request.form.getlist('include_paths')
        exclude_paths = request.form.getlist('exclude_paths')
        
        # Create a temporary file with the fileset configuration
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            f.write(f"fileset name={name} \n")
            f.write("  include {\n")
            for path in include_paths:
                if path.strip():
                    f.write(f"    file = {path.strip()}\n")
            f.write("  }\n")
            
            if any(path.strip() for path in exclude_paths):
                f.write("  exclude {\n")
                for path in exclude_paths:
                    if path.strip():
                        f.write(f"    file = {path.strip()}\n")
                f.write("  }\n")
            
            f.write("}\n")
            temp_filename = f.name
        
        try:
            # In a real implementation, we would update the bacula-dir.conf file
            # and reload the configuration. Here we just simulate it.
            
            flash(f'FileSet {name} created successfully', 'success')
            return redirect(url_for('config.filesets'))
            
        except Exception as e:
            flash(f'Error creating fileset: {str(e)}', 'danger')
        finally:
            # Clean up the temporary file
            os.unlink(temp_filename)
    
    return render_template('config/add_fileset.html')

@config_bp.route('/schedules')
@login_required
def schedules():
    # Get schedules from Bacula
    cmd = "list schedules"
    result = run_bconsole_command(cmd)
    
    # Parse the schedule names (simplified, would need proper parsing)
    schedules = []
    for line in result.split('\n'):
        if line.strip().startswith('Schedule:'):
            schedules.append(line.strip().split('Schedule:')[1].strip())
    
    # Get detailed information about each schedule
    schedule_details = {}
    for schedule in schedules:
        cmd = f"show schedule={schedule}"
        result = run_bconsole_command(cmd)
        schedule_details[schedule] = result
    
    return render_template('config/schedules.html',
                          schedules=schedules,
                          schedule_details=schedule_details)

@config_bp.route('/jobs')
@login_required
def jobs():
    # Get job definitions (not job runs)
    cmd = "list jobs"
    result = run_bconsole_command(cmd)
    
    # Parse the job names (simplified, would need proper parsing)
    jobs = []
    for line in result.split('\n'):
        if line.strip().startswith('Job:'):
            jobs.append(line.strip().split('Job:')[1].strip())
    
    # Get detailed information about each job
    job_details = {}
    for job in jobs:
        cmd = f"show job={job}"
        result = run_bconsole_command(cmd)
        job_details[job] = result
    
    return render_template('config/jobs.html',
                          jobs=jobs,
                          job_details=job_details)

@config_bp.route('/jobs/add', methods=['GET', 'POST'])
@login_required
def add_job():
    clients = Client.select()
    filesets = FileSet.select(FileSet.fileset).distinct()
    pools = Pool.select()
    storages = Storage.select()
    
    if request.method == 'POST':
        name = request.form.get('name')
        client = request.form.get('client')
        fileset = request.form.get('fileset')
        pool = request.form.get('pool')
        storage = request.form.get('storage')
        level = request.form.get('level', 'Incremental')
        schedule = request.form.get('schedule')
        
        # Create a temporary file with the job configuration
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            f.write(f"job name={name} \n")
            f.write(f"  client = {client}\n")
            f.write(f"  fileset = {fileset}\n")
            f.write(f"  pool = {pool}\n")
            f.write(f"  storage = {storage}\n")
            f.write(f"  level = {level}\n")
            if schedule:
                f.write(f"  schedule = {schedule}\n")
            f.write("  type = Backup\n")
            f.write("}\n")
            temp_filename = f.name
        
        try:
            # In a real implementation, we would update the bacula-dir.conf file
            # and reload the configuration. Here we just simulate it.
            
            flash(f'Job {name} created successfully', 'success')
            return redirect(url_for('config.jobs'))
            
        except Exception as e:
            flash(f'Error creating job: {str(e)}', 'danger')
        finally:
            # Clean up the temporary file
            os.unlink(temp_filename)
    
    # Get available schedules
    cmd = "list schedules"
    result = run_bconsole_command(cmd)
    schedules = []
    for line in result.split('\n'):
        if line.strip().startswith('Schedule:'):
            schedules.append(line.strip().split('Schedule:')[1].strip())
    
    return render_template('config/add_job.html',
                          clients=clients,
                          filesets=filesets,
                          pools=pools,
                          storages=storages,
                          schedules=schedules)

@config_bp.route('/reload', methods=['POST'])
@login_required
def reload_config():
    cmd = "reload"
    result = run_bconsole_command(cmd)
    
    return jsonify({
        'success': True,
        'message': result
    })

@config_bp.route('/console', methods=['GET', 'POST'])
@login_required
def console():
    result = ""
    
    if request.method == 'POST':
        command = request.form.get('command')
        result = run_bconsole_command(command)
    
    return render_template('config/console.html', result=result)