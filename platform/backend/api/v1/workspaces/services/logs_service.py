"""
Logs Service for Workspaces
==========================

Servicio para operaciones de logs de workspaces.
"""

import logging
import json
import tempfile
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_, extract
from models import WorkspaceLog, Workspace, db
from repositories.workspace_repository import WorkspaceRepository

logger = logging.getLogger(__name__)


class WorkspaceLogsService:
    """Servicio para operaciones de logs de workspaces."""
    
    def __init__(self, workspace_repository: WorkspaceRepository = None):
        """Inicializa el servicio."""
        self.workspace_repo = workspace_repository or WorkspaceRepository()
    
    def _parse_metadata(self, metadata):
        """Parsea metadata de logs, manejando diferentes formatos."""
        if metadata is None:
            return {}
        if isinstance(metadata, dict):
            return metadata
        if isinstance(metadata, str):
            try:
                return json.loads(metadata)
            except (json.JSONDecodeError, TypeError):
                return {}
        # Si es otro tipo (como MetaData de SQLAlchemy), retornar dict vacío
        return {}
    
    def get_logs(
        self,
        workspace_id: int,
        limit: int = 100,
        offset: int = 0,
        level: Optional[str] = None,
        source: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene logs del workspace.
        
        Args:
            workspace_id: ID del workspace
            limit: Límite de resultados
            offset: Offset para paginación
            level: Filtrar por nivel
            source: Filtrar por fuente
            start_date: Fecha de inicio
            end_date: Fecha de fin
        
        Returns:
            Dict con logs y metadatos
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        query = WorkspaceLog.query.filter_by(workspace_id=workspace_id)
        
        if level:
            query = query.filter_by(level=level.upper())
        
        if source:
            query = query.filter_by(source=source)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(WorkspaceLog.timestamp >= start_dt)
            except (ValueError, AttributeError):
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(WorkspaceLog.timestamp <= end_dt)
            except (ValueError, AttributeError):
                pass
        
        total = query.count()
        logs = query.order_by(WorkspaceLog.timestamp.desc()).limit(limit).offset(offset).all()
        
        return {
            'logs': [{
                'id': log.id,
                'level': log.level,
                'source': log.source,
                'message': log.message,
                'metadata': log.get_metadata() if hasattr(log, 'get_metadata') else self._parse_metadata(getattr(log, 'log_metadata', None)),
                'timestamp': log.timestamp.isoformat() if log.timestamp else None
            } for log in logs],
            'total': total,
            'limit': limit,
            'offset': offset
        }
    
    def get_logs_stats(self, workspace_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de logs del workspace.
        
        Args:
            workspace_id: ID del workspace
        
        Returns:
            Dict con estadísticas
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        # Total de logs
        total_logs = WorkspaceLog.query.filter_by(workspace_id=workspace_id).count()
        
        # Logs por nivel
        logs_by_level = db.session.query(
            WorkspaceLog.level,
            func.count(WorkspaceLog.id).label('count')
        ).filter_by(workspace_id=workspace_id).group_by(WorkspaceLog.level).all()
        
        # Logs por fuente
        logs_by_source = db.session.query(
            WorkspaceLog.source,
            func.count(WorkspaceLog.id).label('count')
        ).filter_by(workspace_id=workspace_id).group_by(WorkspaceLog.source).all()
        
        # Logs por día (últimos 30 días)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        logs_by_day = db.session.query(
            func.date(WorkspaceLog.timestamp).label('date'),
            func.count(WorkspaceLog.id).label('count')
        ).filter(
            and_(
                WorkspaceLog.workspace_id == workspace_id,
                WorkspaceLog.timestamp >= thirty_days_ago
            )
        ).group_by(func.date(WorkspaceLog.timestamp)).order_by(func.date(WorkspaceLog.timestamp)).all()
        
        # Obtener primera y última fecha de logs
        first_log = WorkspaceLog.query.filter_by(workspace_id=workspace_id).order_by(WorkspaceLog.timestamp.asc()).first()
        last_log = WorkspaceLog.query.filter_by(workspace_id=workspace_id).order_by(WorkspaceLog.timestamp.desc()).first()
        
        # Calcular tamaño aproximado (estimación: ~500 bytes por log)
        size_mb = (total_logs * 500) / (1024 * 1024)
        
        return {
            'total_logs': total_logs,
            'size_mb': round(size_mb, 2),
            'by_level': {level: count for level, count in logs_by_level},
            'by_source': {source: count for source, count in logs_by_source},
            'by_day': [{'date': str(date) if date else None, 'count': count} for date, count in logs_by_day],
            'date_range': {
                'first': first_log.timestamp.isoformat() if first_log and first_log.timestamp else None,
                'last': last_log.timestamp.isoformat() if last_log and last_log.timestamp else None
            }
        }
    
    def export_logs(self, workspace_id: int) -> Optional[str]:
        """
        Exporta logs del workspace a archivo temporal.
        
        Args:
            workspace_id: ID del workspace
        
        Returns:
            Path al archivo temporal o None si no existe el workspace
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        logs = WorkspaceLog.query.filter_by(workspace_id=workspace_id).order_by(WorkspaceLog.timestamp.desc()).all()
        
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        
        logs_data = [{
            'id': log.id,
            'level': log.level,
            'source': log.source,
            'message': log.message,
            'metadata': log.metadata if isinstance(log.metadata, dict) else json.loads(log.metadata) if log.metadata else {},
            'timestamp': log.timestamp.isoformat() if log.timestamp else None
        } for log in logs]
        
        json.dump(logs_data, temp_file, indent=2)
        temp_file.close()
        
        return temp_file.name
    
    def delete_logs(self, workspace_id: int, days: Optional[int] = None) -> bool:
        """
        Elimina logs del workspace.
        
        Args:
            workspace_id: ID del workspace
            days: Días de antigüedad (si es None, elimina todos)
        
        Returns:
            True si se eliminaron logs, False si no existe el workspace
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return False
        
        query = WorkspaceLog.query.filter_by(workspace_id=workspace_id)
        
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            query = query.filter(WorkspaceLog.timestamp < cutoff_date)
        
        deleted_count = query.delete()
        db.session.commit()
        
        return deleted_count > 0

