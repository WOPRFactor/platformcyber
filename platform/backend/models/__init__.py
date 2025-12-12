"""
Database Models
===============

Modelos SQLAlchemy para la base de datos.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """
    Inicializa la base de datos.
    
    Args:
        app: Instancia de Flask
    """
    with app.app_context():
        db.create_all()


# Importar modelos para que sean reconocidos por SQLAlchemy
from .user import User
from .workspace import Workspace
from .workspace_log import WorkspaceLog
from .scan import Scan, ScanResult
from .vulnerability import Vulnerability
from .report import Report
from .audit_log import AuditLog

__all__ = [
    'db',
    'init_db',
    'User',
    'Workspace',
    'WorkspaceLog',
    'Scan',
    'ScanResult',
    'Vulnerability',
    'Report',
    'AuditLog'
]



