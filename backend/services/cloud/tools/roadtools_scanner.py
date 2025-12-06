"""
ROADtools Scanner
================

Azure AD analysis con ROADtools.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from ..base import BaseCloudService
from ..executors.scan_executor import CloudScanExecutor

logger = logging.getLogger(__name__)


class ROADtoolsScanner(BaseCloudService):
    """Scanner ROADtools para análisis de Azure AD."""

    def __init__(self, scan_repository=None):
        super().__init__(scan_repository)
        self.executor = CloudScanExecutor(self.scan_repo)

    def start_gather(
        self,
        workspace_id: int,
        user_id: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        access_token: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta roadrecon para recopilar datos de Azure AD.
        
        Args:
            workspace_id: ID del workspace
            user_id: ID del usuario
            username: Usuario de Azure AD
            password: Password
            access_token: Token de acceso
            tenant_id: ID del tenant (opcional)
        """
        scan = self._create_scan(
            target=f'azure:{tenant_id or "default"}',
            workspace_id=workspace_id,
            user_id=user_id,
            tool='roadtools',
            options={
                'provider': 'azure',
                'action': 'gather'
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            db_path = workspace_output_dir / f'roadtools_{scan.id}.db'

            command = ['roadrecon', 'gather', '--database', str(db_path)]

            if access_token:
                command.extend(['--access-token', access_token])
            elif username and password:
                command.extend(['--username', username, '--password', password])
                if tenant_id:
                    command.extend(['--tenant-id', tenant_id])
            else:
                # Usar device code auth
                command.append('--device-code')

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting ROADtools gather {scan.id}")

            self.executor.execute_scan_in_thread(
                scan.id, sanitized_cmd, db_path, 'roadtools', timeout=1800
            )
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'roadtools',
                'provider': 'azure',
                'action': 'gather'
            }

        except Exception as e:
            logger.error(f"Error starting ROADtools: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

