# app/views/dashboard.py
from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.models.bacula_models import Job, Client, Pool, Media
from peewee import fn, SQL
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    # Get summary statistics
    total_clients = Client.select().count()
    total_jobs = Job.select().count()
    successful_jobs = Job.select().where(Job.jobstatus == 'T').count()
    failed_jobs = Job.select().where(Job.jobstatus == 'E').count()
    
    # Get recent jobs
    recent_jobs = (Job
                  .select(Job, Client.name.alias('client_name'))
                  .join(Client)
                  .order_by(Job.starttime.desc())
                  .limit(10))
    
    # Get storage usage
    pools = (Pool
            .select(Pool, fn.SUM(Media.volbytes).alias('total_bytes'))
            .join(Media, on=(Pool.poolid == Media.poolid))
            .group_by(Pool.poolid)
            .order_by(SQL('total_bytes').desc()))
    
    return render_template('dashboard/index.html',
                          total_clients=total_clients,
                          total_jobs=total_jobs,
                          successful_jobs=successful_jobs,
                          failed_jobs=failed_jobs,
                          recent_jobs=recent_jobs,
                          pools=pools)

@dashboard_bp.route('/stats/jobs_last_week')
@login_required
def jobs_last_week():
    # Get job statistics for the last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    jobs_by_day = (Job
                  .select(
                      fn.DATE(Job.starttime).alias('date'),
                      fn.COUNT(Job.jobid).alias('count'),
                      Job.jobstatus
                  )
                  .where(Job.starttime.between(start_date, end_date))
                  .group_by(fn.DATE(Job.starttime), Job.jobstatus)
                  .order_by(fn.DATE(Job.starttime)))
    
    # Format data for chart
    dates = []
    successful = []
    failed = []
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        dates.append(date_str)
        
        # Find matching records for this date
        success_count = 0
        fail_count = 0
        
        for job in jobs_by_day:
            if job.date.strftime('%Y-%m-%d') == date_str:
                if job.jobstatus == 'T':
                    success_count = job.count
                elif job.jobstatus == 'E':
                    fail_count = job.count
        
        successful.append(success_count)
        failed.append(fail_count)
        current_date += timedelta(days=1)
    
    return jsonify({
        'labels': dates,
        'datasets': [
            {
                'label': 'Successful Jobs',
                'data': successful,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Failed Jobs',
                'data': failed,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1
            }
        ]
    })