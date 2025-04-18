# app/__init__.py
from flask import Flask
from flask_login import LoginManager
from app.models.bacula_models import *
from app.models.user_models import *
import os
from werkzeug.security import generate_password_hash
from datetime import timedelta ,datetime
login_manager = LoginManager()
now=datetime.now()


def format_number(value):
    """Format a number with commas as thousands separators"""
    return "{:,}".format(value)
def create_app(config=None):
    app = Flask(__name__)
    app.jinja_env.globals.update(min=min)
    app.jinja_env.globals.update(timedelta=timedelta)
    app.jinja_env.globals.update(now=now)
    # Load configuration
    if config:
        app.config.from_object(config)
    else:
        app.config.from_object('config.ProductionConfig')
    
    # Initialize database
    #database.init(app.config['BACULA_DB_NAME'])
            #     host=app.config['BACULA_DB_HOST'],
            #     user=app.config['BACULA_DB_USER'],
             #    password=app.config['BACULA_DB_PASSWORD'])
    
    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_or_none(User.id == int(user_id))
    app.jinja_env.filters['format_number'] = format_number
    # Create tables if they don't exist
    with app.app_context():
        database.create_tables([User,Client,Pool,Job,FileSet,Storage,Media], safe=True)
        
        # Create default admin user if no users exist
        if User.select().count() == 0:
            default_admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            default_admin.set_password('amiraa74')
            default_admin.save()
            app.logger.info('Created default admin user: admin/admin123')
    
    # Register blueprints
    from app.views.auth import auth_bp
    from app.views.dashboard import dashboard_bp
    from app.views.clients import clients_bp
    from app.views.jobs import jobs_bp
    from app.views.storage import storage_bp
    from app.views.config import config_bp
    from app.views.restore import restore_bp
    from app.views.pools import pools_bp
    from app.views.volumes import volumes_bp
    from app.views.filesets import filesets_bp
    from app.views.schedules import schedules_bp
    from app.views.settings import settings_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(storage_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(restore_bp)
    app.register_blueprint(pools_bp)
    app.register_blueprint(volumes_bp)
    app.register_blueprint(filesets_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(settings_bp)
    
    return app