"""
Audit Log Model
===============

Modelo de auditoría para tracking de acciones.
"""

from datetime import datetime
from . import db


class AuditLog(db.Model):
    """Modelo de log de auditoría."""
    
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Usuario
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='audit_logs')
    
    # Acción
    action = db.Column(db.String(100), nullable=False)
    # Ejemplos: scan_started, exploit_executed, report_generated
    
    resource_type = db.Column(db.String(50))  # scan, vulnerability, report
    resource_id = db.Column(db.Integer)
    
    # Detalles
    details = db.Column(db.JSON)  # Información adicional de la acción
    ip_address = db.Column(db.String(45))  # IPv4 o IPv6
    user_agent = db.Column(db.String(255))
    
    # Resultado
    success = db.Column(db.Boolean, default=True, nullable=False)
    error_message = db.Column(db.Text)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self) -> dict:
        """Serializa el audit log a diccionario."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'success': self.success,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AuditLog {self.action} by user {self.user_id}>'



