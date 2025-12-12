"""
User Model
==========

Modelo de usuario con autenticación y roles.
"""

from datetime import datetime
from . import db
import bcrypt


class User(db.Model):
    """Modelo de usuario del sistema."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Roles y permisos
    role = db.Column(db.String(20), nullable=False, default='analyst')
    # Roles: admin, pentester, analyst, viewer
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relaciones
    workspaces = db.relationship('Workspace', back_populates='owner', lazy='dynamic')
    scans = db.relationship('Scan', back_populates='user', lazy='dynamic')
    reports = db.relationship('Report', back_populates='created_by_user', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', back_populates='user', lazy='dynamic')
    
    def set_password(self, password: str) -> None:
        """Hashea y guarda la contraseña."""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verifica la contraseña."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def has_permission(self, permission: str) -> bool:
        """Verifica si el usuario tiene un permiso."""
        permissions_map = {
            'admin': ['*'],  # Todos los permisos
            'pentester': ['scan', 'exploit', 'report', 'read'],
            'analyst': ['scan', 'report', 'read'],
            'viewer': ['read']
        }
        
        user_permissions = permissions_map.get(self.role, [])
        return '*' in user_permissions or permission in user_permissions
    
    def to_dict(self) -> dict:
        """Serializa el usuario a diccionario."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'



