"""
Syft Scanner
===========

SBOM (Software Bill of Materials) generator con Syft.
"""

import logging
import subprocess
from typing import Dict, Any
from pathlib import Path

from utils.validators import CommandSanitizer
from utils.parsers.container_parser import SyftParser
from ..base import BaseContainerService

logger = logging.getLogger(__name__)


class SyftScanner(BaseContainerService):
    """Scanner Syft para generar SBOM."""

    def __init__(self, scan_repository=None):
        super().__init__(scan_repository)
        self.syft_parser = SyftParser()

    def generate_sbom(
        self,
        image: str,
        workspace_id: int,
        user_id: int,
        output_format: str = 'spdx-json'
    ) -> Dict[str, Any]:
        """
        Genera SBOM (Software Bill of Materials) con Syft.
        
        Args:
            image: Nombre de la imagen
            workspace_id: ID del workspace
            user_id: ID del usuario
            output_format: Formato de salida (spdx-json, cyclonedx-json, syft-json)
        """
        scan = self._create_scan(
            target=image,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='syft',
            options={
                'action': 'sbom',
                'format': output_format
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'syft_{scan.id}.json'

            command = [
                'syft',
                image,
                '--output', f'{output_format}={output_file}'
            ]

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting Syft SBOM generation {scan.id}")

            # Ejecutar sync (rápido)
            result = subprocess.run(
                sanitized_cmd,
                capture_output=True,
                text=True,
                timeout=300,
                env=CommandSanitizer.get_safe_env()
            )

            if result.returncode == 0:
                self.scan_repo.update_status(scan, 'completed')
                self.scan_repo.update_progress(scan, 100, 'SBOM generated')

                with open(output_file, 'r') as f:
                    results = self.syft_parser.parse_sbom(f.read())

                return {
                    'scan_id': scan.id,
                    'status': 'completed',
                    'tool': 'syft',
                    'target': image,
                    'sbom_file': str(output_file),
                    'results': results
                }
            else:
                self.scan_repo.update_status(scan, 'failed', result.stderr)
                raise Exception(result.stderr)

        except Exception as e:
            logger.error(f"Error generating SBOM: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

