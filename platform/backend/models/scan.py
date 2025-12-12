"""
Scan Models
===========

Modelos para escaneos y resultados.
"""

from datetime import datetime
from . import db


class Scan(db.Model):
    """Modelo de escaneo."""
    
    __tablename__ = 'scans'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Metadata
    scan_type = db.Column(db.String(50), nullable=False)
    # Tipos: reconnaissance, port_scan, vuln_scan, exploit, post_exploit, ad_enum, cloud_audit
    
    target = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    # Estados: pending, running, completed, failed, cancelled
    
    # Configuración
    options = db.Column(db.JSON)  # Opciones específicas del scan
    
    # Resultados
    progress = db.Column(db.Integer, default=0)  # 0-100
    output = db.Column(db.Text)  # Output del comando
    error = db.Column(db.Text)   # Errores si falla
    
    # Timestamps
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    workspace = db.relationship('Workspace', back_populates='scans')
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='scans')
    
    results = db.relationship('ScanResult', back_populates='scan', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self) -> dict:
        """Serializa el scan a diccionario."""
        return {
            'id': self.id,
            'scan_type': self.scan_type,
            'target': self.target,
            'status': self.status,
            'progress': self.progress,
            'options': self.options,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'workspace_id': self.workspace_id,
            'user_id': self.user_id,
            'results_count': self.results.count()
        }
    
    def __repr__(self):
        return f'<Scan {self.scan_type} on {self.target}>'


class ScanResult(db.Model):
    """Resultado individual de un escaneo."""
    
    __tablename__ = 'scan_results'
    
    id = db.Column(db.Integer, primary_key=True)
    
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    scan = db.relationship('Scan', back_populates='results')
    
    # Datos del resultado
    result_type = db.Column(db.String(50), nullable=False)
    # Tipos: open_port, subdomain, vulnerability, credential, etc
    
    data = db.Column(db.JSON, nullable=False)  # Datos estructurados
    severity = db.Column(db.String(20))  # critical, high, medium, low, info
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self) -> dict:
        """Serializa el resultado a diccionario."""
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'result_type': self.result_type,
            'data': self.data,
            'severity': self.severity,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ScanResult {self.result_type}>'



