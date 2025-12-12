"""
Workspace Log Model
===================

Modelo para persistencia de logs por workspace.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import json
from . import db


class WorkspaceLog(db.Model):
    """Modelo de log persistente por workspace."""
    
    __tablename__ = 'workspace_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False)
    source = db.Column(db.String(50), nullable=False)  # BACKEND, CELERY, NIKTO, etc.
    level = db.Column(db.String(10), nullable=False)  # DEBUG, INFO, WARNING, ERROR
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Campos opcionales
    task_id = db.Column(db.String(100), nullable=True)
    log_metadata = db.Column(db.Text, nullable=True)  # JSON string (metadata es reservado en SQLAlchemy)
    
    # Relación
    workspace = db.relationship('Workspace', backref='logs', lazy='select')
    
    def __init__(self, **kwargs):
        """Inicializa el log."""
        # Convertir metadata dict a JSON string si es necesario
        if 'log_metadata' in kwargs and isinstance(kwargs['log_metadata'], dict):
            kwargs['log_metadata'] = json.dumps(kwargs['log_metadata'])
        elif 'metadata' in kwargs and isinstance(kwargs['metadata'], dict):
            # Compatibilidad: aceptar 'metadata' y convertir a 'log_metadata'
            kwargs['log_metadata'] = json.dumps(kwargs['metadata'])
            del kwargs['metadata']
        super().__init__(**kwargs)
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Obtiene metadata como diccionario."""
        if not self.log_metadata:
            return None
        try:
            return json.loads(self.log_metadata)
        except (json.JSONDecodeError, TypeError):
            return None
    
    def set_metadata(self, data: Dict[str, Any]) -> None:
        """Establece metadata desde diccionario."""
        self.log_metadata = json.dumps(data) if data else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa el log a diccionario."""
        return {
            'id': self.id,
            'workspace_id': self.workspace_id,
            'source': self.source,
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'task_id': self.task_id,
            'metadata': self.get_metadata()
        }
    
    def __repr__(self):
        return f'<WorkspaceLog {self.source} {self.level} @ {self.timestamp}>'

