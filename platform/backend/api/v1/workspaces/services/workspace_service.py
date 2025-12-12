"""
Workspace Service
================

Servicio para operaciones de workspaces.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from repositories.workspace_repository import WorkspaceRepository
from models import Workspace

logger = logging.getLogger(__name__)


class WorkspaceService:
    """Servicio para operaciones de workspaces."""
    
    def __init__(self, workspace_repository: WorkspaceRepository = None):
        """Inicializa el servicio."""
        self.workspace_repo = workspace_repository or WorkspaceRepository()
    
    def serialize_workspace(self, workspace: Workspace) -> Dict[str, Any]:
        """
        Serializa un workspace a diccionario.
        
        Args:
            workspace: Workspace object
        
        Returns:
            Dict con datos del workspace
        """
        return {
            'id': workspace.id,
            'name': workspace.name,
            'description': workspace.description,
            'client_name': workspace.client_name,
            'client_contact': workspace.client_contact,
            'target_domain': workspace.target_domain,
            'target_ip': workspace.target_ip,
            'target_type': workspace.target_type,
            'in_scope': workspace.in_scope,
            'out_of_scope': workspace.out_of_scope,
            'start_date': workspace.start_date.isoformat() if workspace.start_date else None,
            'end_date': workspace.end_date.isoformat() if workspace.end_date else None,
            'notes': workspace.notes,
            'is_active': workspace.is_active,
            'created_at': workspace.created_at.isoformat() if workspace.created_at else None,
            'updated_at': workspace.updated_at.isoformat() if workspace.updated_at else None,
            'owner_id': workspace.owner_id
        }
    
    def list_workspaces(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Lista todos los workspaces del usuario.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Lista de workspaces serializados
        """
        workspaces = self.workspace_repo.find_by_owner(user_id)
        return [self.serialize_workspace(ws) for ws in workspaces]
    
    def get_workspace(self, workspace_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un workspace específico.
        
        Args:
            workspace_id: ID del workspace
        
        Returns:
            Workspace serializado o None si no existe
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        return self.serialize_workspace(workspace)
    
    def create_workspace(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo workspace.
        
        Args:
            user_id: ID del usuario
            data: Datos del workspace
        
        Returns:
            Workspace creado serializado
        """
        # Parsear fechas si existen
        start_date = None
        end_date = None
        
        if data.get('start_date'):
            try:
                start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                pass
        
        if data.get('end_date'):
            try:
                end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                pass
        
        workspace = self.workspace_repo.create(
            name=data['name'],
            description=data.get('description', ''),
            owner_id=user_id,
            client_name=data.get('client_name'),
            client_contact=data.get('client_contact'),
            target_domain=data.get('target_domain'),
            target_ip=data.get('target_ip'),
            target_type=data.get('target_type'),
            in_scope=data.get('in_scope'),
            out_of_scope=data.get('out_of_scope'),
            start_date=start_date,
            end_date=end_date,
            notes=data.get('notes'),
            is_active=data.get('is_active', True)
        )
        
        result = self.serialize_workspace(workspace)
        result['message'] = 'Workspace created successfully'
        return result
    
    def update_workspace(self, workspace_id: int, user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Actualiza un workspace existente.
        
        Args:
            workspace_id: ID del workspace
            user_id: ID del usuario
            data: Datos a actualizar
        
        Returns:
            Workspace actualizado serializado o None si no existe
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        # Verificar permisos
        if workspace.owner_id != user_id:
            raise PermissionError('You do not have permission to update this workspace')
        
        # Parsear fechas si existen
        if 'start_date' in data:
            try:
                data['start_date'] = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                data['start_date'] = None
        
        if 'end_date' in data:
            try:
                data['end_date'] = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                data['end_date'] = None
        
        updated_workspace = self.workspace_repo.update(workspace_id, **data)
        return self.serialize_workspace(updated_workspace)
    
    def delete_workspace(self, workspace_id: int, user_id: int) -> bool:
        """
        Elimina un workspace.
        
        Args:
            workspace_id: ID del workspace
            user_id: ID del usuario
        
        Returns:
            True si se eliminó, False si no existe
        
        Raises:
            PermissionError: Si el usuario no tiene permisos
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return False
        
        if workspace.owner_id != user_id:
            raise PermissionError('You do not have permission to delete this workspace')
        
        self.workspace_repo.delete(workspace_id)
        return True
    
    def archive_workspace(self, workspace_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Archiva un workspace.
        
        Args:
            workspace_id: ID del workspace
            user_id: ID del usuario
        
        Returns:
            Workspace archivado serializado o None si no existe
        
        Raises:
            PermissionError: Si el usuario no tiene permisos
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        if workspace.owner_id != user_id:
            raise PermissionError('You do not have permission to archive this workspace')
        
        workspace.is_active = False
        from models import db
        db.session.commit()
        
        return self.serialize_workspace(workspace)


