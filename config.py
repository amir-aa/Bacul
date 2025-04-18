# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    BACULA_DB_HOST = os.environ.get('BACULA_DB_HOST') or 'localhost'
    BACULA_DB_USER = os.environ.get('BACULA_DB_USER') or 'bacula'
    BACULA_DB_PASSWORD = os.environ.get('BACULA_DB_PASSWORD') or 'bacula'
    BACULA_DB_NAME = os.environ.get('BACULA_DB_NAME') or 'bacula'
    BCONSOLE_PATH = os.environ.get('BCONSOLE_PATH') or '/usr/sbin/bconsole'
    BCONSOLE_CONFIG = os.environ.get('BCONSOLE_CONFIG') or '/etc/bacula/bconsole.conf'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False