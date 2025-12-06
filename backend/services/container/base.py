"""
Base Container Service
======================

Clase base común para todos los servicios de container security.
Proporciona funcionalidad compartida: ejecución de scans, logging, etc.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from repositories import ScanRepository

logger = logging.getLogger(__name__)


class BaseContainerService:
    """Clase base para servicios de container security."""

    def __init__(self, scan_repository: ScanRepository = None):
        """Inicializa el servicio base."""
        self.scan_repo = scan_repository or ScanRepository()
        from utils.workspace_filesystem import PROJECT_TMP_DIR
        self.output_dir = PROJECT_TMP_DIR / 'container_security'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_workspace_output_dir(self, scan_id: int) -> Path:
        """Obtiene directorio de output del workspace para un scan."""
        from utils.workspace_filesystem import get_workspace_output_dir_from_scan
        return get_workspace_output_dir_from_scan(scan_id, 'container_security')

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
            scan_type='container_security',
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            options={'tool': tool, **options}
        )

