"""
Workspace Model
===============

Modelo de workspace para aislamiento por cliente/proyecto.
"""

from datetime import datetime
from sqlalchemy import event
from . import db
import logging


class Workspace(db.Model):
    """Modelo de workspace (proyecto/cliente)."""
    
    __tablename__ = 'workspaces'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Cliente
    client_name = db.Column(db.String(100))
    client_contact = db.Column(db.String(100))
    
    # Target Principal
    target_domain = db.Column(db.String(255))  # Dominio o URL principal
    target_ip = db.Column(db.String(50))  # IP del target (opcional)
    target_type = db.Column(db.String(50))  # Tipo: 'web', 'api', 'mobile', 'network', 'other'
    
    # Scope del Proyecto
    in_scope = db.Column(db.Text)  # Qué está dentro del scope
    out_of_scope = db.Column(db.Text)  # Qué está fuera del scope
    
    # Fechas del Proyecto
    start_date = db.Column(db.Date)  # Fecha de inicio del proyecto
    end_date = db.Column(db.Date)  # Fecha límite del proyecto
    
    # Notas
    notes = db.Column(db.Text)  # Notas adicionales
    
    # Configuración
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # Deprecated: usar status
    status = db.Column(db.String(20), default='active', nullable=False)  # active, paused, archived, completed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Owner
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', back_populates='workspaces')
    
    # Relaciones
    scans = db.relationship('Scan', back_populates='workspace', lazy='dynamic', cascade='all, delete-orphan')
    vulnerabilities = db.relationship('Vulnerability', back_populates='workspace', lazy='dynamic', cascade='all, delete-orphan')
    reports = db.relationship('Report', back_populates='workspace', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self) -> dict:
        """Serializa el workspace a diccionario."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'client_name': self.client_name,
            'client_contact': self.client_contact,
            'target_domain': self.target_domain,
            'target_ip': self.target_ip,
            'target_type': self.target_type,
            'in_scope': self.in_scope,
            'out_of_scope': self.out_of_scope,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'notes': self.notes,
            'is_active': self.is_active,
            'status': getattr(self, 'status', 'active'),  # Compatibilidad si no existe
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_scans': self.scans.count(),
            'total_vulnerabilities': self.vulnerabilities.count()
        }
    
    def __repr__(self):
        return f'<Workspace {self.name}>'


@event.listens_for(Workspace, 'after_insert')
def create_workspace_directory(mapper, connection, target):
    """
    Crea directorio de archivos al crear un workspace.
    
    Hook de SQLAlchemy que se ejecuta automáticamente después de insertar
    un nuevo workspace en la base de datos.
    """
    from utils.workspace_filesystem import create_workspace_directory_structure
    
    try:
        create_workspace_directory_structure(target.id, target.name)
    except Exception as e:
        # Log error pero no fallar la creación del workspace
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creando directorio para workspace {target.id}: {e}")



