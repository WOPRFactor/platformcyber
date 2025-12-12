"""
Trivy Scanner
=============

Container vulnerability scanner con Trivy.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from ..base import BaseContainerService
from ..executors.scan_executor import ContainerScanExecutor

logger = logging.getLogger(__name__)


class TrivyScanner(BaseContainerService):
    """Scanner Trivy para imágenes Docker."""

    def __init__(self, scan_repository=None):
        super().__init__(scan_repository)
        self.executor = ContainerScanExecutor(self.scan_repo)

    def scan_image(
        self,
        image: str,
        workspace_id: int,
        user_id: int,
        severity: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Escanea imagen Docker con Trivy.
        
        Args:
            image: Nombre de la imagen (ej: nginx:latest)
            workspace_id: ID del workspace
            user_id: ID del usuario
            severity: Severidades a reportar (CRITICAL, HIGH, MEDIUM, LOW)
        """
        scan = self._create_scan(
            target=image,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='trivy',
            options={
                'scan_type': 'image',
                'severity': severity or ['CRITICAL', 'HIGH']
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'trivy_{scan.id}.json'

            command = [
                'trivy', 'image',
                '--format', 'json',
                '--output', str(output_file)
            ]

            if severity:
                command.extend(['--severity', ','.join(severity)])

            command.append(image)

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting Trivy image scan {scan.id}")

            self.executor.execute_scan_in_thread(
                scan.id, sanitized_cmd, output_file, 'trivy', timeout=600
            )
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'trivy',
                'target': image
            }

        except Exception as e:
            logger.error(f"Error starting Trivy: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

