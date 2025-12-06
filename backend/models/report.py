"""
Report Model
============

Modelo de reportes generados.
"""

from datetime import datetime
from . import db


class Report(db.Model):
    """Modelo de reporte."""
    
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Metadata
    title = db.Column(db.String(255), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)
    # Tipos: executive, technical, compliance, full
    
    # Formato
    format = db.Column(db.String(20), nullable=False)
    # pdf, html, json, markdown
    
    # Contenido
    content = db.Column(db.Text)  # Contenido markdown/html
    file_path = db.Column(db.String(500))  # Path al archivo generado
    file_size = db.Column(db.Integer)  # Tamaño en bytes
    
    # Estado
    status = db.Column(db.String(20), default='draft', nullable=False)
    # draft, generating, completed, failed
    
    # Timestamps
    generated_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    workspace = db.relationship('Workspace', back_populates='reports')
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by_user = db.relationship('User', back_populates='reports')
    
    def to_dict(self) -> dict:
        """Serializa el reporte a diccionario."""
        return {
            'id': self.id,
            'title': self.title,
            'report_type': self.report_type,
            'format': self.format,
            'status': self.status,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'workspace_id': self.workspace_id,
            'created_by': self.created_by
        }
    
    def __repr__(self):
        return f'<Report {self.title}>'



