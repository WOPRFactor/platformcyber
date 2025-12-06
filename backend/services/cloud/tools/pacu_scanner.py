"""
Pacu Scanner
===========

AWS pentesting framework con Pacu.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from ..base import BaseCloudService
from ..executors.scan_executor import CloudScanExecutor

logger = logging.getLogger(__name__)


class PacuScanner(BaseCloudService):
    """Scanner Pacu para AWS pentesting."""

    def __init__(self, scan_repository=None):
        super().__init__(scan_repository)
        self.executor = CloudScanExecutor(self.scan_repo)

    def start_module(
        self,
        module_name: str,
        workspace_id: int,
        user_id: int,
        aws_profile: Optional[str] = None,
        module_args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta un módulo de Pacu.
        
        Args:
            module_name: Nombre del módulo (ej: 'iam__enum_permissions')
            workspace_id: ID del workspace
            user_id: ID del usuario
            aws_profile: Perfil AWS a usar (opcional)
            module_args: Argumentos para el módulo
        """
        scan = self._create_scan(
            target=f'aws:{aws_profile or "default"}',
            workspace_id=workspace_id,
            user_id=user_id,
            tool='pacu',
            options={
                'provider': 'aws',
                'module': module_name,
                'profile': aws_profile
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'pacu_{scan.id}.txt'

            # Pacu usa un formato especial de comandos
            command = [
                'pacu',
                '--session', f'scan_{scan.id}',
                '--exec', f'run {module_name}'
            ]

            if aws_profile:
                command.extend(['--profile', aws_profile])

            if module_args:
                args_str = ' '.join([f'--{k} {v}' for k, v in module_args.items()])
                command[-1] += f' {args_str}'

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting Pacu module {module_name} - scan {scan.id}")

            self.executor.execute_scan_in_thread(
                scan.id, sanitized_cmd, output_file, 'pacu', timeout=1800
            )
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'pacu',
                'module': module_name,
                'provider': 'aws'
            }

        except Exception as e:
            logger.error(f"Error starting Pacu: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

