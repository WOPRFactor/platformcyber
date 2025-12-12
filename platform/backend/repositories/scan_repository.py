"""
Scan Repository
===============

Repository para operaciones de escaneos.
"""

from typing import Optional, List
from datetime import datetime
from models import db, Scan, ScanResult


class ScanRepository:
    """Repository para gestión de escaneos."""
    
    @staticmethod
    def create(
        scan_type: str,
        target: str,
        workspace_id: int,
        user_id: int,
        options: dict = None
    ) -> Scan:
        """
        Crea un nuevo escaneo.
        
        Args:
            scan_type: Tipo de escaneo
            target: Target del escaneo
            workspace_id: ID del workspace
            user_id: ID del usuario
            options: Opciones adicionales
        
        Returns:
            Escaneo creado
        """
        scan = Scan(
            scan_type=scan_type,
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            options=options or {},
            status='pending'
        )
        
        db.session.add(scan)
        db.session.commit()
        
        return scan
    
    @staticmethod
    def find_by_id(scan_id: int) -> Optional[Scan]:
        """Busca escaneo por ID."""
        return Scan.query.get(scan_id)
    
    @staticmethod
    def find_by_workspace(
        workspace_id: int,
        status: Optional[str] = None,
        scan_type: Optional[str] = None
    ) -> List[Scan]:
        """
        Busca escaneos por workspace.
        
        Args:
            workspace_id: ID del workspace
            status: Filtrar por estado (opcional)
            scan_type: Filtrar por tipo (opcional)
        
        Returns:
            Lista de escaneos
        """
        query = Scan.query.filter_by(workspace_id=workspace_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if scan_type:
            query = query.filter_by(scan_type=scan_type)
        
        return query.order_by(Scan.created_at.desc()).all()
    
    @staticmethod
    def find_by_user(user_id: int, limit: int = 50) -> List[Scan]:
        """Busca escaneos por usuario."""
        return Scan.query.filter_by(user_id=user_id)\
            .order_by(Scan.created_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def update_status(scan: Scan, status: str, error: str = None) -> Scan:
        """
        Actualiza el estado de un escaneo.
        
        Args:
            scan: Escaneo a actualizar
            status: Nuevo estado
            error: Mensaje de error (opcional)
        
        Returns:
            Escaneo actualizado
        """
        scan.status = status
        
        if error:
            scan.error = error
        
        if status == 'running' and not scan.started_at:
            scan.started_at = datetime.utcnow()
        
        if status in ['completed', 'failed', 'cancelled']:
            scan.completed_at = datetime.utcnow()
        
        db.session.commit()
        return scan
    
    @staticmethod
    def update_progress(scan: Scan, progress: int, output: str = None) -> Scan:
        """Actualiza el progreso de un escaneo."""
        scan.progress = progress
        
        if output:
            scan.output = output
        
        db.session.commit()
        return scan
    
    @staticmethod
    def add_result(
        scan: Scan,
        result_type: str,
        data: dict,
        severity: str = None
    ) -> ScanResult:
        """
        Agrega un resultado al escaneo.
        
        Args:
            scan: Escaneo
            result_type: Tipo de resultado
            data: Datos del resultado
            severity: Severidad (opcional)
        
        Returns:
            Resultado creado
        """
        result = ScanResult(
            scan_id=scan.id,
            result_type=result_type,
            data=data,
            severity=severity
        )
        
        db.session.add(result)
        db.session.commit()
        
        return result
    
    @staticmethod
    def get_running_scans() -> List[Scan]:
        """Obtiene todos los escaneos en ejecución."""
        return Scan.query.filter_by(status='running').all()
    
    @staticmethod
    def update_options(scan: Scan, options: dict) -> Scan:
        """
        Actualiza las opciones de un escaneo.
        
        Args:
            scan: Escaneo a actualizar
            options: Nuevas opciones (se fusionan con las existentes)
        
        Returns:
            Escaneo actualizado
        """
        from sqlalchemy.orm.attributes import flag_modified
        
        if scan.options is None:
            scan.options = {}
        scan.options.update(options)
        # Marcar el campo JSON como modificado para que SQLAlchemy detecte el cambio
        flag_modified(scan, 'options')
        db.session.commit()
        return scan
    
    @staticmethod
    def delete(scan: Scan) -> None:
        """Elimina un escaneo."""
        db.session.delete(scan)
        db.session.commit()



