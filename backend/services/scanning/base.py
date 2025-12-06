"""
Base Scanning Service
=====================

Clase base para servicios de escaneo.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
from repositories import ScanRepository
from utils.workspace_filesystem import get_workspace_output_dir_from_scan

logger = logging.getLogger(__name__)


class BaseScanningService:
    """Clase base para servicios de escaneo."""
    
    def __init__(self, scan_repository: ScanRepository = None):
        """Inicializa el servicio base."""
        self.scan_repo = scan_repository or ScanRepository()
    
    def _get_workspace_output_dir(self, scan_id: int, subdir: str = 'scans') -> Path:
        """
        Obtiene directorio de output del workspace para un scan.
        
        Args:
            scan_id: ID del scan
            subdir: Subdirectorio (scans, enumeration, etc.)
        
        Returns:
            Path al directorio de output del workspace
        """
        return get_workspace_output_dir_from_scan(scan_id, subdir)
    
    def _create_scan(
        self,
        scan_type: str,
        target: str,
        workspace_id: int,
        user_id: int,
        tool: str,
        options: Dict[str, Any]
    ):
        """
        Crea un registro de scan en la base de datos.
        
        Args:
            scan_type: Tipo de scan
            target: Target del scan
            workspace_id: ID del workspace
            user_id: ID del usuario
            tool: Nombre de la herramienta
            options: Opciones del scan
        
        Returns:
            Scan object
        """
        options['tool'] = tool
        return self.scan_repo.create(
            scan_type=scan_type,
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            options=options
        )


