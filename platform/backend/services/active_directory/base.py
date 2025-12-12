"""
Active Directory Base Service
==============================

Clase base para servicios de Active Directory.
"""

import logging
from typing import Dict, Any
from pathlib import Path

from repositories import ScanRepository
from utils.workspace_filesystem import PROJECT_TMP_DIR

logger = logging.getLogger(__name__)


class BaseADService:
    """Clase base para servicios de Active Directory."""

    def __init__(self, scan_repository: ScanRepository = None):
        self.scan_repo = scan_repository or ScanRepository()
        self.output_dir = PROJECT_TMP_DIR / 'ad_scans'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_workspace_output_dir(self, scan_id: int) -> Path:
        """Obtiene directorio de output del workspace para un scan."""
        from utils.workspace_filesystem import get_workspace_output_dir_from_scan
        return get_workspace_output_dir_from_scan(scan_id, 'ad_scans')

