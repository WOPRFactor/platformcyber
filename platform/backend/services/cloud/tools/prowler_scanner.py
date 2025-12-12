"""
Prowler Scanner
==============

AWS, Azure, GCP security audit con Prowler.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from ..base import BaseCloudService
from ..executors.scan_executor import CloudScanExecutor

logger = logging.getLogger(__name__)


class ProwlerScanner(BaseCloudService):
    """Scanner Prowler para auditoría de seguridad cloud."""

    def __init__(self, scan_repository=None):
        super().__init__(scan_repository)
        self.executor = CloudScanExecutor(self.scan_repo)

    def start_scan(
        self,
        provider: str,
        workspace_id: int,
        user_id: int,
        profile: Optional[str] = None,
        severity: Optional[List[str]] = None,
        compliance: Optional[str] = None,
        services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta Prowler para auditoría de seguridad.
        
        Args:
            provider: Proveedor (aws, azure, gcp)
            workspace_id: ID del workspace
            user_id: ID del usuario
            profile: Perfil de credenciales
            severity: Severidades a incluir (critical, high, medium, low)
            compliance: Framework de compliance (cis, hipaa, gdpr, etc.)
            services: Servicios específicos
        """
        scan = self._create_scan(
            target=f'{provider}:{profile or "default"}',
            workspace_id=workspace_id,
            user_id=user_id,
            tool='prowler',
            options={
                'provider': provider,
                'profile': profile,
                'severity': severity,
                'compliance': compliance
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_dir = workspace_output_dir / f'prowler_{scan.id}'
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / 'prowler_output.json'

            command = [
                'prowler',
                provider,
                '--output-directory', str(output_dir),
                '--output-formats', 'json',
                '--no-banner'
            ]

            if profile:
                if provider == 'aws':
                    command.extend(['--profile', profile])
                elif provider == 'azure':
                    command.extend(['--sp-env-auth'])

            if severity:
                command.extend(['--severity', ','.join(severity)])

            if compliance:
                command.extend(['--compliance', compliance])

            if services:
                command.extend(['--services', ','.join(services)])

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting Prowler scan {scan.id} for {provider}")

            self.executor.execute_scan_in_thread(
                scan.id, sanitized_cmd, output_file, 'prowler', timeout=3600
            )
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'prowler',
                'provider': provider
            }

        except Exception as e:
            logger.error(f"Error starting Prowler: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

