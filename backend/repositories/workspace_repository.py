"""
Workspace Repository
====================

Repository para operaciones de workspaces.
"""

from typing import Optional, List
from models import db, Workspace


class WorkspaceRepository:
    """Repository para gestión de workspaces."""
    
    @staticmethod
    def create(
        name: str,
        owner_id: int,
        description: str = None,
        client_name: str = None,
        client_contact: str = None,
        target_domain: str = None,
        target_ip: str = None,
        target_type: str = None,
        in_scope: str = None,
        out_of_scope: str = None,
        start_date = None,
        end_date = None,
        notes: str = None,
        is_active: bool = True
    ) -> Workspace:
        """Crea un nuevo workspace."""
        workspace = Workspace(
            name=name,
            owner_id=owner_id,
            description=description,
            client_name=client_name,
            client_contact=client_contact,
            target_domain=target_domain,
            target_ip=target_ip,
            target_type=target_type,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
            is_active=is_active
        )
        
        db.session.add(workspace)
        db.session.commit()
        
        return workspace
    
    @staticmethod
    def find_by_id(workspace_id: int) -> Optional[Workspace]:
        """Busca workspace por ID."""
        return Workspace.query.get(workspace_id)
    
    @staticmethod
    def find_by_owner(owner_id: int, is_active: bool = True) -> List[Workspace]:
        """Busca workspaces por owner."""
        query = Workspace.query.filter_by(owner_id=owner_id)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        return query.order_by(Workspace.created_at.desc()).all()
    
    @staticmethod
    def find_all(is_active: bool = True) -> List[Workspace]:
        """Lista todos los workspaces."""
        query = Workspace.query
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        return query.order_by(Workspace.created_at.desc()).all()
    
    @staticmethod
    def update(workspace: Workspace) -> Workspace:
        """Actualiza un workspace."""
        db.session.commit()
        return workspace
    
    @staticmethod
    def delete(workspace: Workspace) -> None:
        """
        Elimina un workspace permanentemente (hard delete).
        
        Elimina el registro de la base de datos. Las relaciones
        con cascade='all, delete-orphan' se eliminarán automáticamente.
        """
        db.session.delete(workspace)
        db.session.commit()



