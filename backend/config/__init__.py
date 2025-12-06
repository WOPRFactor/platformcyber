"""
Configuration Module
====================

Gestión centralizada de configuración por ambiente.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
basedir = Path(__file__).parent.parent
env_path = basedir / '.env'
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """Configuración base compartida por todos los ambientes."""
    
    # App
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required")
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 días
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT = ["200 per day", "50 per hour"]
    RATE_LIMIT_STORAGE_URI = os.getenv('RATE_LIMIT_STORAGE_URI', 'memory://')
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_ENABLED = True
    
    # Logging
    LOG_LEVEL = 'INFO'
    # Ruta de logs (relativa al directorio del entorno, no del código)
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    # Rotación de logs (en horas)
    LOG_RETENTION_HOURS = int(os.getenv('LOG_RETENTION_HOURS', '12'))  # 12 horas por defecto
    # LOG_MAX_BYTES en bytes (50MB por defecto)
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', str(50 * 1024 * 1024)))
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '3'))  # 3 archivos de backup
    
    # Pentesting Tools
    TOOLS_TIMEOUT = 300  # 5 minutos timeout por defecto
    MAX_CONCURRENT_SCANS = 5


class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    
    ENV = 'development'
    DEBUG = True
    TESTING = False
    
    # Database
    # Usar ruta absoluta para evitar que Flask-SQLAlchemy use instance/
    basedir = Path(__file__).parent.parent
    default_db_path = basedir / 'dev3_pentest.db'
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{default_db_path}'
    )
    SQLALCHEMY_ECHO = True  # Log SQL queries
    
    # Security (menos restrictivo en dev)
    SESSION_COOKIE_SECURE = False
    
    # CORS (permisivo en dev)
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173', 'http://localhost:5176', 'http://localhost:5177', 'http://localhost:5178', 'http://localhost:5179', 'http://192.168.0.11:5176', 'http://192.168.0.11:5177', 'http://192.168.0.11:5178', 'http://192.168.0.11:5179']
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    # Logs en desarrollo: retención corta (6 horas)
    LOG_RETENTION_HOURS = int(os.getenv('LOG_RETENTION_HOURS', '6'))
    # 20MB en dev
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', str(20 * 1024 * 1024)))
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '2'))


class ProductionConfig(Config):
    """Configuración para producción."""
    
    ENV = 'production'
    DEBUG = False
    TESTING = False
    
    # Database (PostgreSQL en producción)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is required in production")
    
    # Security
    if not os.getenv('JWT_SECRET_KEY'):
        raise ValueError("JWT_SECRET_KEY must be set in production")
    
    # Rate Limiting (más estricto en producción)
    RATE_LIMIT_DEFAULT = ["100 per day", "20 per hour"]
    RATE_LIMIT_STORAGE_URI = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # CORS (restrictivo en producción)
    cors_env = os.getenv('CORS_ORIGINS', '')
    if cors_env:
        CORS_ORIGINS = cors_env.split(',')
    else:
        # En producción sin CORS_ORIGINS configurado, usar lista vacía por defecto
        CORS_ORIGINS = []


class TestingConfig(Config):
    """Configuración para testing."""
    
    ENV = 'testing'
    DEBUG = True
    TESTING = True
    
    # Database (SQLite en memoria para tests)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False
    
    # Security (deshabilitado en tests)
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    
    # JWT (tokens de corta duración para tests)
    JWT_ACCESS_TOKEN_EXPIRES = 300  # 5 minutos
    
    # CORS (permisivo en tests)
    CORS_ORIGINS = ['*']
    
    # Rate Limiting (deshabilitado en tests)
    RATE_LIMIT_DEFAULT = []
    RATE_LIMIT_ENABLED = False
    
    # Celery (modo eager para tests síncronos)
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
    
    # Logging
    LOG_LEVEL = 'ERROR'  # Solo errores en tests
    # Logs en tests: retención mínima (2 horas)
    LOG_RETENTION_HOURS = int(os.getenv('LOG_RETENTION_HOURS', '2'))
    # 10MB en test
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', str(10 * 1024 * 1024)))
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '1'))
    
    # Tools
    TOOLS_TIMEOUT = 10  # Timeout corto para tests


# Mapeo de configuraciones
config_map: Dict[str, Any] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = 'development') -> Any:
    """
    Obtiene la configuración según el ambiente.
    
    Args:
        config_name: Nombre del ambiente
    
    Returns:
        Clase de configuración
    """
    return config_map.get(config_name, DevelopmentConfig)


