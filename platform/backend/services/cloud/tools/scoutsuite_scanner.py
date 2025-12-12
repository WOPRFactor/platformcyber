"""
ScoutSuite Scanner
==================

Multi-cloud security audit con ScoutSuite.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from ..base import BaseCloudService
from ..executors.scan_executor import CloudScanExecutor

logger = logging.getLogger(__name__)


class ScoutSuiteScanner(BaseCloudService):
    """Scanner ScoutSuite para auditoría multi-cloud."""

    def __init__(self, scan_repository=None):
        super().__init__(scan_repository)
        self.executor = CloudScanExecutor(self.scan_repo)

    def start_scan(
        self,
        provider: str,
        workspace_id: int,
        user_id: int,
        profile: Optional[str] = None,
        regions: Optional[List[str]] = None,
        services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta ScoutSuite para auditoría de seguridad.
        
        Args:
            provider: Proveedor cloud (aws, azure, gcp, alibaba, oci)
            workspace_id: ID del workspace
            user_id: ID del usuario
            profile: Perfil de credenciales
            regions: Regiones a escanear
            services: Servicios específicos a auditar
        """
        scan = self._create_scan(
            target=f'{provider}:{profile or "default"}',
            workspace_id=workspace_id,
            user_id=user_id,
            tool='scoutsuite',
            options={
                'provider': provider,
                'profile': profile,
                'regions': regions,
                'services': services
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_dir = workspace_output_dir / f'scoutsuite_{scan.id}'
            output_dir.mkdir(exist_ok=True)

            command = [
                'scout',
                provider,
                '--report-dir', str(output_dir),
                '--no-browser'
            ]

            if profile:
                command.extend(['--profile', profile])

            if regions:
                command.extend(['--regions', ','.join(regions)])

            if services:
                command.extend(['--services', ','.join(services)])

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting ScoutSuite scan {scan.id} for {provider}")

            # ScoutSuite genera un directorio, usar el directorio como output
            self.executor.execute_scan_in_thread(
                scan.id, sanitized_cmd, output_dir / 'scoutsuite_report', 'scoutsuite', timeout=3600
            )
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'scoutsuite',
                'provider': provider
            }

        except Exception as e:
            logger.error(f"Error starting ScoutSuite: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

