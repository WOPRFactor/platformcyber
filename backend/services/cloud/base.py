"""
Base Cloud Service
==================

Clase base común para todos los servicios de cloud pentesting.
Proporciona funcionalidad compartida: ejecución de scans, logging, etc.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from repositories import ScanRepository

logger = logging.getLogger(__name__)


class BaseCloudService:
    """Clase base para servicios de cloud pentesting."""

    def __init__(self, scan_repository: ScanRepository = None):
        """Inicializa el servicio base."""
        self.scan_repo = scan_repository or ScanRepository()
        from utils.workspace_filesystem import PROJECT_TMP_DIR
        self.output_dir = PROJECT_TMP_DIR / 'cloud_scans'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_workspace_output_dir(self, scan_id: int) -> Path:
        """Obtiene directorio de output del workspace para un scan."""
        from utils.workspace_filesystem import get_workspace_output_dir_from_scan
        return get_workspace_output_dir_from_scan(scan_id, 'cloud_scans')

    def _create_scan(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        tool: str,
        options: Dict[str, Any]
    ) -> Any:  # Retorna un objeto Scan de SQLAlchemy
        """Crea un registro de scan en la base de datos."""
        return self.scan_repo.create(
            scan_type='cloud_pentesting',
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            options={'tool': tool, **options}
        )

