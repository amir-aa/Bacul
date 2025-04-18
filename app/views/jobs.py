# app/views/jobs.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.models.bacula_models import Job, Client, FileSet, Pool
from app.utils.bacula_cmd import run_bconsole_command
from peewee import fn, JOIN
import json
from datetime import datetime, timedelta

jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')

def format_bytes(size):
    """Format bytes to human-readable format"""
    power = 2**10
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

def format_duration(duration):
    """Format timedelta to human-readable format"""
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

@jobs_bp.route('/')
@login_required
def index():
    # Get all jobs with client names
    jobs = (Job
           .select(Job, Client.name.alias('client_name'))
           .join(Client)
           .order_by(Job.starttime.desc())
           .limit(100))
    
    # Get all clients for filter
    clients = Client.select()
    
    # Get statistics
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    
    stats = {
        'total_24h': Job.select().where(Job.starttime > yesterday).count(),
        'successful_24h': Job.select().where(Job.starttime > yesterday, Job.jobstatus == 'T').count(),
        'failed_24h': Job.select().where(Job.starttime > yesterday, Job.jobstatus == 'E').count(),
        'running': Job.select().where(Job.jobstatus == 'R').count()
    }
    
    # Get success rate data for the last 7 days
    success_rate_data = {'labels': [], 'success_rate': [], 'total_jobs': []}
    
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day)
        day_end = datetime(day.year, day.month, day.day, 23, 59, 59)
        
        total = Job.select().where(Job.starttime.between(day_start, day_end)).count()
        successful = Job.select().where(
            Job.starttime.between(day_start, day_end),
            Job.jobstatus == 'T'
        ).count()
        
        rate = (successful / total * 100) if total > 0 else 0
        
        success_rate_data['labels'].append(day_start.strftime('%Y-%m-%d'))
        success_rate_data['success_rate'].append(round(rate, 2))
        success_rate_data['total_jobs'].append(total)
    
    # Get job types distribution
    job_types = {
        'F': Job.select().where(Job.level == 'F').count(),
        'I': Job.select().where(Job.level == 'I').count(),
        'D': Job.select().where(Job.level == 'D').count()
    }
    job_types_data = [job_types['F'], job_types['I'], job_types['D']]
    
    # Get data transfer volume
    data_transfer = {'labels': [], 'data': []}
    
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day)
        day_end = datetime(day.year, day.month, day.day, 23, 59, 59)
        
        total_bytes = Job.select(fn.SUM(Job.jobbytes)).where(
            Job.starttime.between(day_start, day_end),
            Job.jobstatus == 'T'
        ).scalar() or 0
        
        # Convert to GB
        gb = total_bytes / (1024 * 1024 * 1024)
        
        data_transfer['labels'].append(day_start.strftime('%Y-%m-%d'))
        data_transfer['data'].append(round(gb, 2))
    
    # Get error types
    error_types = []
    # In a real application, you would parse job logs to get error types
    # This is a simplified example
    error_types = [
        {'type': 'Connection refused', 'count': 5, 'last_occurrence': now - timedelta(hours=3)},
        {'type': 'File not found', 'count': 3, 'last_occurrence': now - timedelta(hours=8)},
        {'type': 'Permission denied', 'count': 2, 'last_occurrence': now - timedelta(hours=12)}
    ]
    
    # Get clients with most failures
    client_failures = {'labels': [], 'data': []}
    
    client_failures_query = (Job
                            .select(Client.name, fn.COUNT(Job.jobid).alias('failures'))
                            .join(Client)
                            .where(Job.jobstatus == 'E', Job.starttime > (now - timedelta(days=30)))
                            .group_by(Client.name)
                            .order_by(fn.COUNT(Job.jobid).desc())
                            .limit(5))
    
    for result in client_failures_query:
        client_failures['labels'].append(result.client.name)
        client_failures['data'].append(result.failures)
    
    # Get currently running jobs
    running_jobs = []
    running_jobs_query = (Job
                         .select(Job, Client.name.alias('client_name'))
                         .join(Client)
                         .where(Job.jobstatus == 'R')
                         .order_by(Job.starttime))
    
    for job in running_jobs_query:
        # Calculate progress (this would typically come from Bacula's API or logs)
        # Here we're just estimating based on time elapsed
        start_time = job.starttime
        elapsed = (now - start_time).total_seconds()
        # Assuming an average job takes 1 hour
        progress = min(round(elapsed / 3600 * 100), 99)
        if progress < 10:
            progress = 10  # Always show at least 10% progress for visual feedback
            
        job.progress = progress
        running_jobs.append(job)
    
    return render_template('jobs/index.html',
                          jobs=jobs,
                          clients=clients,
                          stats=stats,
                          success_rate_data=success_rate_data,
                          job_types_data=job_types_data,
                          data_transfer=data_transfer,
                          error_types=error_types,
                          client_failures=client_failures,
                          running_jobs=running_jobs,
                          now=now,
                          format_bytes=format_bytes,
                          format_duration=format_duration)

@jobs_bp.route('/run', methods=['GET', 'POST'])
@login_required
def run_job():
    clients = Client.select()
    filesets = FileSet.select(FileSet.fileset).distinct()
    pools = Pool.select()
    
    if request.method == 'POST':
        job_name = request.form.get('job_name')
        client_name = request.form.get('client_name')
        fileset_name = request.form.get('fileset_name')
        pool_name = request.form.get('pool_name')
        level = request.form.get('level', 'Incremental')
        priority = request.form.get('priority', '10')
        
        # Construct bconsole command
        cmd = f"run job={job_name} client={client_name}"
        
        if fileset_name:
            cmd += f" fileset={fileset_name}"
        
        if pool_name:
            cmd += f" pool={pool_name}"
        
        cmd += f" level={level} priority={priority} yes"
        
        result = run_bconsole_command(cmd)
        flash(f"Job started: {result}", 'success')
        return redirect(url_for('jobs.index'))
    
    return render_template('jobs/run_job.html', 
                          clients=clients,
                          filesets=filesets,
                          pools=pools)

@jobs_bp.route('/<int:job_id>/status')
@login_required
def job_status(job_id):
    job = Job.get_or_none(Job.jobid == job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('jobs.index'))
    
    # Get job status from bconsole
    cmd = f"status jobid={job_id}"
    result = run_bconsole_command(cmd)
    
    # Get job log
    cmd = f"list joblog jobid={job_id}"
    log_result = run_bconsole_command(cmd)
    
    # Get client name
    client = Client.get_or_none(Client.clientid == job.clientid)
    client_name = client.name if client else "Unknown"
    
    return render_template('jobs/status.html', 
                          job=job,
                          client_name=client_name,
                          status_output=result,
                          log_output=log_result,
                          format_bytes=format_bytes,
                          format_duration=format_duration)

@jobs_bp.route('/<int:job_id>/cancel', methods=['POST'])
@login_required
def cancel_job(job_id):
    job = Job.get_or_none(Job.jobid == job_id)
    if not job:
        return jsonify({'success': False, 'message': 'Job not found'})
    
    cmd = f"cancel jobid={job_id}"
    result = run_bconsole_command(cmd)
    
    return jsonify({'success': True, 'message': result})

@jobs_bp.route('/running')
@login_required
def running_jobs():
    """API endpoint to get currently running jobs"""
    now = datetime.now()
    running_jobs = []
    
    running_jobs_query = (Job
                         .select(Job, Client.name.alias('client_name'))
                         .join(Client)
                         .where(Job.jobstatus == 'R')
                         .order_by(Job.starttime))
    
    for job in running_jobs_query:
        # Calculate progress
        start_time = job.starttime
        elapsed = (now - start_time).total_seconds()
        progress = min(round(elapsed / 3600 * 100), 99)
        if progress < 10:
            progress = 10
            
        running_jobs.append({
            'jobid': job.jobid,
            'name': job.name,
            'client_name': job.client_name,
            'type': job.type,
            'level': job.level,
            'starttime': job.starttime.strftime('%Y-%m-%d %H:%M:%S'),
            'runtime': format_duration(now - job.starttime),
            'progress': progress,
            'jobfiles': job.jobfiles,
            'jobbytes': format_bytes(job.jobbytes)
        })
    
    return jsonify(running_jobs)