import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'Passw0rd123'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'maintenance_system_v2'
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'sessions')
    
    # =====================
    # Mail Configuration (matches gmailtest.py)
    # =====================
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'maintenancesysteme05@gmail.com'
    MAIL_PASSWORD = 'fngx gpfe apiy qqxw'
    MAIL_DEFAULT_SENDER = 'maintenancesysteme05@gmail.com'
    
    # Email Settings



    EMAILS_ENABLED = True
    # Whether to send low-stock alert emails to stock agents (set to False to stop quantity alert emails)
    EMAIL_LOW_STOCK_ALERTS_ENABLED = os.environ.get('EMAIL_LOW_STOCK_ALERTS_ENABLED', 'True').lower() in ['1', 'true', 'yes']
    # Whether to send critical stock alert emails (items at or below minimum stock)
    # Set to False to stop the automated critical quantity/email alerts.
    EMAIL_CRITICAL_STOCK_ALERTS_ENABLED = os.environ.get('EMAIL_CRITICAL_STOCK_ALERTS_ENABLED', 'True').lower() in ['1', 'true', 'yes']
    
    # Application Settings
    ITEMS_PER_PAGE = 20
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    
    # Company Information
    COMPANY_NAME = 'Sumitomo Wiring Systems'
    COMPANY_LOGO = 'images/logo.png'
    # Logo URL for emails - hosted on GitHub
    LOGO_URL = 'https://raw.githubusercontent.com/GHAITHBT/appstage2026PFE/main/app/static/images/logo.png'

    # Base URL for links in emails (ensure this matches your deployed host)
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig 
}
