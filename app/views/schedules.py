from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import random

# Create blueprint
schedules_bp = Blueprint('schedules', __name__, url_prefix='/schedules')

# Sample data for demonstration
sample_schedules = [
    {
        'scheduleid': 1,
        'name': 'Daily-Incremental',
        'description': 'Daily incremental backups on weekdays',
        'is_active': True,
        'created': datetime.now() - timedelta(days=120),
        'runs': [
            {'level': 'Incremental', 'day': 'Monday', 'time': '20:00', 'enabled': True},
            {'level': 'Incremental', 'day': 'Tuesday', 'time': '20:00', 'enabled': True},
            {'level': 'Incremental', 'day': 'Wednesday', 'time': '20:00', 'enabled': True},
            {'level': 'Incremental', 'day': 'Thursday', 'time': '20:00', 'enabled': True},
            {'level': 'Incremental', 'day': 'Friday', 'time': '20:00', 'enabled': True}
        ],
        'next_run': datetime.now() + timedelta(hours=5)
    },
    {
        'scheduleid': 2,
        'name': 'Weekly-Full',
        'description': 'Full backup every Sunday',
        'is_active': True,
        'created': datetime.now() - timedelta(days=90),
        'runs': [
            {'level': 'Full', 'day': 'Sunday', 'time': '01:00', 'enabled': True}
        ],
        'next_run': datetime.now() + timedelta(days=2, hours=8)
    },
    {
        'scheduleid': 3,
        'name': 'Monthly-Archive',
        'description': 'Archive backup on the first day of each month',
        'is_active': True,
        'created': datetime.now() - timedelta(days=60),
        'runs': [
            {'level': 'Full', 'day': '1st', 'time': '02:00', 'enabled': True}
        ],
        'next_run': datetime.now() + timedelta(days=15, hours=10)
    },
    {
        'scheduleid': 4,
        'name': 'Quarterly-Offsite',
        'description': 'Quarterly full backup for offsite storage',
        'is_active': False,
        'created': datetime.now() - timedelta(days=45),
        'runs': [
            {'level': 'Full', 'day': 'January 1', 'time': '03:00', 'enabled': True},
            {'level': 'Full', 'day': 'April 1', 'time': '03:00', 'enabled': True},
            {'level': 'Full', 'day': 'July 1', 'time': '03:00', 'enabled': True},
            {'level': 'Full', 'day': 'October 1', 'time': '03:00', 'enabled': True}
        ],
        'next_run': datetime.now() + timedelta(days=45, hours=3)
    },
    {
        'scheduleid': 5,
        'name': 'Hourly-Critical',
        'description': 'Hourly differential backup for critical systems',
        'is_active': True,
        'created': datetime.now() - timedelta(days=15),
        'runs': [
            {'level': 'Differential', 'day': 'Hourly', 'time': '00:00', 'enabled': True}
        ],
        'next_run': datetime.now() + timedelta(minutes=35)
    }
]

# Routes
@schedules_bp.route('/')
def index():
    # Calculate schedule statistics
    stats = {
        'total': len(sample_schedules),
        'active': sum(1 for s in sample_schedules if s['is_active']),
        'inactive': sum(1 for s in sample_schedules if not s['is_active']),
        'runs_today': random.randint(3, 8)
    }
    
    return render_template('schedules/index.html', schedules=sample_schedules, stats=stats)

@schedules_bp.route('/<int:schedule_id>')
def detail(schedule_id):
    # Find the schedule by ID
    schedule = next((s for s in sample_schedules if s['scheduleid'] == schedule_id), None)
    if not schedule:
        flash('Schedule not found', 'danger')
        return redirect(url_for('schedules.index'))
    
    # Sample job data that uses this schedule
    sample_jobs = [
        {
            'jobid': 101,
            'name': 'Backup-System',
            'client': 'server1.example.com',
            'last_run': datetime.now() - timedelta(days=1, hours=2),
            'status': 'Completed'
        },
        {
            'jobid': 102,
            'name': 'Backup-Database',
            'client': 'db.example.com',
            'last_run': datetime.now() - timedelta(hours=14),
            'status': 'Completed'
        },
        {
            'jobid': 103,
            'name': 'Backup-Web',
            'client': 'web.example.com',
            'last_run': datetime.now() - timedelta(days=1, hours=1, minutes=30),
            'status': 'Failed'
        }
    ]
    
    return render_template('schedules/detail.html', schedule=schedule, jobs=sample_jobs)

@schedules_bp.route('/add')
def add_schedule():
    return render_template('schedules/add_schedule.html')

@schedules_bp.route('/add', methods=['POST'])
def add_schedule_post():
    try:
        # Get form data
        name = request.form['name']
        description = request.form['description']
        is_active = 'is_active' in request.form
        
        # Process run configurations from the form
        runs = []
        for i in range(10):  # Assuming maximum 10 runs in the form
            day_key = f'day_{i}'
            time_key = f'time_{i}'
            level_key = f'level_{i}'
            enabled_key = f'enabled_{i}'
            
            if day_key in request.form and time_key in request.form and level_key in request.form:
                runs.append({
                    'day': request.form[day_key],
                    'time': request.form[time_key],
                    'level': request.form[level_key],
                    'enabled': enabled_key in request.form
                })
        
        # In a real application, you would add the schedule to Bacula using bconsole or API
        # For this example, we'll simulate success
        
        flash('Schedule created successfully!', 'success')
        return redirect(url_for('schedules.index'))
    
    except Exception as e:
        flash(f'Error creating schedule: {str(e)}', 'danger')
        return redirect(url_for('schedules.add_schedule'))

@schedules_bp.route('/<int:schedule_id>/edit')
def edit_schedule(schedule_id):
    # Find the schedule by ID
    schedule = next((s for s in sample_schedules if s['scheduleid'] == schedule_id), None)
    if not schedule:
        flash('Schedule not found', 'danger')
        return redirect(url_for('schedules.index'))
    
    return render_template('schedules/edit_schedule.html', schedule=schedule)

@schedules_bp.route('/<int:schedule_id>/edit', methods=['POST'])
def edit_schedule_post(schedule_id):
    try:
        # Get form data
        name = request.form['name']
        description = request.form['description']
        is_active = 'is_active' in request.form
        
        # Process run configurations from the form
        runs = []
        for i in range(10):  # Assuming maximum 10 runs in the form
            day_key = f'day_{i}'
            time_key = f'time_{i}'
            level_key = f'level_{i}'
            enabled_key = f'enabled_{i}'
            
            if day_key in request.form and time_key in request.form and level_key in request.form:
                runs.append({
                    'day': request.form[day_key],
                    'time': request.form[time_key],
                    'level': request.form[level_key],
                    'enabled': enabled_key in request.form
                })
        
        # In a real application, you would update the schedule in Bacula
        # For this example, we'll simulate success
        
        flash('Schedule updated successfully!', 'success')
        return redirect(url_for('schedules.detail', schedule_id=schedule_id))
    
    except Exception as e:
        flash(f'Error updating schedule: {str(e)}', 'danger')
        return redirect(url_for('schedules.edit_schedule', schedule_id=schedule_id))

@schedules_bp.route('/<int:schedule_id>/toggle', methods=['POST'])
def toggle_schedule(schedule_id):
    # Find the schedule by ID
    schedule = next((s for s in sample_schedules if s['scheduleid'] == schedule_id), None)
    if not schedule:
        flash('Schedule not found', 'danger')
        return redirect(url_for('schedules.index'))
    
    # Toggle the active status
    schedule['is_active'] = not schedule['is_active']
    
    status = 'activated' if schedule['is_active'] else 'deactivated'
    flash(f'Schedule {schedule["name"]} {status} successfully!', 'success')
    return redirect(url_for('schedules.detail', schedule_id=schedule_id))

@schedules_bp.route('/<int:schedule_id>/delete', methods=['POST'])
def delete_schedule(schedule_id):
    # In a real app, this would delete the schedule from Bacula
    flash('Schedule deleted successfully!', 'success')
    return redirect(url_for('schedules.index'))

@schedules_bp.route('/export/<int:schedule_id>')
def export_schedule(schedule_id):
    # Find the schedule by ID
    schedule = next((s for s in sample_schedules if s['scheduleid'] == schedule_id), None)
    if not schedule:
        flash('Schedule not found', 'danger')
        return redirect(url_for('schedules.index'))
    
    # Generate Bacula configuration
    config = f"""
Schedule {{
    Name = "{schedule['name']}"
"""
    
    for run in schedule['runs']:
        config += f"    Run = Level={run['level']} "
        
        if run['day'] == 'Hourly':
            config += "Hourly "
        elif run['day'] in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            config += f"{run['day']} "
        elif run['day'] == '1st':
            config += "1st day of month "
        else:
            config += f"{run['day']} "
        
        config += f"at {run['time']}\n"
    
    config += "}\n"
    
    # In a real app, you might return this as a downloadable file
    return render_template('schedules/export_schedule.html', schedule=schedule, config=config)

@schedules_bp.route('/run-now/<int:schedule_id>', methods=['POST'])
def run_now(schedule_id):
    # In a real app, this would trigger the schedule immediately in Bacula
    flash('Schedule triggered successfully!', 'success')
    return redirect(url_for('schedules.detail', schedule_id=schedule_id))