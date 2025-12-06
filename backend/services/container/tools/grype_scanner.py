"""
Grype Scanner
=============

Vulnerability scanner para imágenes de contenedores con Grype.
"""

import logging
from typing import Dict, Any
from pathlib import Path

from utils.validators import CommandSanitizer
from ..base import BaseContainerService
from ..executors.scan_executor import ContainerScanExecutor

logger = logging.getLogger(__name__)


class GrypeScanner(BaseContainerService):
    """Scanner Grype para imágenes Docker."""

    def __init__(self, scan_repository=None):
        super().__init__(scan_repository)
        self.executor = ContainerScanExecutor(self.scan_repo)

    def scan_image(
        self,
        image: str,
        workspace_id: int,
        user_id: int,
        scope: str = 'all-layers'
    ) -> Dict[str, Any]:
        """
        Escanea imagen con Grype.
        
        Args:
            image: Nombre de la imagen
            workspace_id: ID del workspace
            user_id: ID del usuario
            scope: Scope del scan ('all-layers' o 'squashed')
        """
        scan = self._create_scan(
            target=image,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='grype',
            options={'scope': scope}
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'grype_{scan.id}.json'

            command = [
                'grype',
                image,
                '--output', 'json',
                '--file', str(output_file),
                '--scope', scope
            ]

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting Grype scan {scan.id}")

            self.executor.execute_scan_in_thread(
                scan.id, sanitized_cmd, output_file, 'grype', timeout=600
            )
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'grype',
                'target': image
            }

        except Exception as e:
            logger.error(f"Error starting Grype: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

