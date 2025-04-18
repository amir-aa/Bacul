# app/views/restore.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required
from app.models.bacula_models import Client, FileSet, Job
from app.utils.bacula_cmd import run_bconsole_command
from datetime import datetime

restore_bp = Blueprint('restore', __name__, url_prefix='/restore')

@restore_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    clients = Client.select()
    filesets = FileSet.select(FileSet.fileset).distinct()
    
    if request.method == 'POST':
        client_name = request.form.get('client_name')
        fileset_name = request.form.get('fileset_name')
        job_id = request.form.get('job_id')
        
        session['restore_client'] = client_name
        session['restore_fileset'] = fileset_name
        session['restore_jobid'] = job_id
        
        return redirect(url_for('restore.file_selection'))
    
    return render_template('restore/index.html', 
                          clients=clients,
                          filesets=filesets)

@restore_bp.route('/jobs/<client_name>')
@login_required
def get_jobs(client_name):
    client = Client.get_or_none(Client.name == client_name)
    if not client:
        return jsonify([])
    
    jobs = (Job
           .select(Job.jobid, Job.name, Job.starttime, Job.level)
           .where(Job.clientid == client.clientid, Job.jobstatus == 'T')
           .order_by(Job.starttime.desc())
           .limit(50))
    
    return jsonify([{
        'jobid': job.jobid,
        'name': job.name,
        'starttime': job.starttime.strftime('%Y-%m-%d %H:%M:%S'),
        'level': job.level
    } for job in jobs])

@restore_bp.route('/file_selection', methods=['GET', 'POST'])
@login_required
def file_selection():
    client_name = session.get('restore_client')
    fileset_name = session.get('restore_fileset')
    job_id = session.get('restore_jobid')
    
    if not all([client_name, job_id]):
        flash('Missing restore parameters', 'danger')
        return redirect(url_for('restore.index'))
    
    if request.method == 'POST':
        files = request.form.getlist('files[]')
        restore_location = request.form.get('restore_location')
        
        # Build restore command
        cmd = f"""restore jobid={job_id} client={client_name} file="{','.join(files)}" where={restore_location} yes"""
        result = run_bconsole_command(cmd)
        
        flash(f"Restore job started: {result}", 'success')
        return redirect(url_for('jobs.index'))
    
    # Get file list for job
    cmd = f"list files jobid={job_id}"
    result = run_bconsole_command(cmd)
    
    # Parse file list (simplified, would need proper parsing in production)
    files = [line.strip() for line in result.split('\n') if line.strip() and not line.startswith('|')]
    
    return render_template('restore/file_selection.html',
                          client_name=client_name,
                          job_id=job_id,
                          files=files)