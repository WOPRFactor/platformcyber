"""
Report Model
============

Modelo de reportes generados.
"""

from datetime import datetime
from pathlib import Path
import hashlib
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
    
    # Versionado
    version = db.Column(db.Integer, default=1, nullable=False)
    is_latest = db.Column(db.Boolean, default=True, nullable=False)
    
    # Contenido
    content = db.Column(db.Text)  # Contenido markdown/html
    file_path = db.Column(db.String(500))  # Path al archivo generado
    file_size = db.Column(db.Integer)  # Tamaño en bytes
    file_hash = db.Column(db.String(64))  # SHA-256 hash del archivo
    
    # Metadata del contenido
    total_findings = db.Column(db.Integer, default=0)
    critical_count = db.Column(db.Integer, default=0)
    high_count = db.Column(db.Integer, default=0)
    medium_count = db.Column(db.Integer, default=0)
    low_count = db.Column(db.Integer, default=0)
    info_count = db.Column(db.Integer, default=0)
    risk_score = db.Column(db.Float)  # 0-10
    
    # Metadata de procesamiento
    files_processed = db.Column(db.Integer, default=0)
    tools_used = db.Column(db.JSON)  # ['nmap', 'nuclei', ...]
    generation_time_seconds = db.Column(db.Float)
    
    # Estado
    status = db.Column(db.String(20), default='pending', nullable=False)
    # Estados: pending, generating, completed, failed
    error_message = db.Column(db.Text)
    
    # Timestamps
    generated_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    workspace = db.relationship('Workspace', back_populates='reports')
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by_user = db.relationship('User', back_populates='reports')
    
    def calculate_file_hash(self):
        """Calcula SHA-256 hash del archivo."""
        if not self.file_path:
            return None
            
        file_path = Path(self.file_path)
        if not file_path.exists():
            return None
        
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return None
    
    def verify_integrity(self) -> bool:
        """Verifica integridad del archivo."""
        if not self.file_hash:
            return False
        return self.calculate_file_hash() == self.file_hash
    
    def to_dict(self) -> dict:
        """Serializa el reporte a diccionario."""
        return {
            'id': self.id,
            'title': self.title,
            'report_type': self.report_type,
            'format': self.format,
            'version': self.version,
            'is_latest': self.is_latest,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'total_findings': self.total_findings,
            'severity_counts': {
                'critical': self.critical_count,
                'high': self.high_count,
                'medium': self.medium_count,
                'low': self.low_count,
                'info': self.info_count
            },
            'risk_score': self.risk_score,
            'files_processed': self.files_processed,
            'tools_used': self.tools_used,
            'generation_time_seconds': self.generation_time_seconds,
            'status': self.status,
            'error_message': self.error_message,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'workspace_id': self.workspace_id,
            'created_by': self.created_by
        }
    
    def __repr__(self):
        return f'<Report {self.title}>'



