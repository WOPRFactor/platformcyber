"""
AzureHound Scanner
=================

Azure AD enumeration con AzureHound.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from ..base import BaseCloudService
from ..executors.scan_executor import CloudScanExecutor

logger = logging.getLogger(__name__)


class AzureHoundScanner(BaseCloudService):
    """Scanner AzureHound para enumeración de Azure AD."""

    def __init__(self, scan_repository=None):
        super().__init__(scan_repository)
        self.executor = CloudScanExecutor(self.scan_repo)

    def start_collection(
        self,
        tenant_id: str,
        workspace_id: int,
        user_id: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta AzureHound para enumerar Azure AD.
        
        Args:
            tenant_id: ID del tenant de Azure
            workspace_id: ID del workspace
            user_id: ID del usuario
            username: Usuario de Azure AD
            password: Password
            access_token: Token de acceso (alternativa a user/pass)
        """
        scan = self._create_scan(
            target=f'azure:{tenant_id}',
            workspace_id=workspace_id,
            user_id=user_id,
            tool='azurehound',
            options={
                'provider': 'azure',
                'tenant_id': tenant_id
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'azurehound_{scan.id}.json'

            command = [
                'azurehound',
                '-t', tenant_id,
                '-o', str(output_file)
            ]

            if access_token:
                command.extend(['--access-token', access_token])
            elif username and password:
                command.extend(['-u', username, '-p', password])
            else:
                # Usar device code auth
                command.append('--use-device-code')

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting AzureHound collection {scan.id}")

            self.executor.execute_scan_in_thread(
                scan.id, sanitized_cmd, output_file, 'azurehound', timeout=1800
            )
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'azurehound',
                'provider': 'azure',
                'tenant_id': tenant_id
            }

        except Exception as e:
            logger.error(f"Error starting AzureHound: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

