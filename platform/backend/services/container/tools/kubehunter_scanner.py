"""
Kube-hunter Scanner
==================

Kubernetes penetration testing con Kube-hunter.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from ..base import BaseContainerService
from ..executors.scan_executor import ContainerScanExecutor

logger = logging.getLogger(__name__)


class KubeHunterScanner(BaseContainerService):
    """Scanner Kube-hunter para pentest de Kubernetes."""

    def __init__(self, scan_repository=None):
        super().__init__(scan_repository)
        self.executor = ContainerScanExecutor(self.scan_repo)

    def run_scan(
        self,
        workspace_id: int,
        user_id: int,
        mode: str = 'remote',
        remote_host: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta Kube-hunter para pentest de Kubernetes.
        
        Args:
            workspace_id: ID del workspace
            user_id: ID del usuario
            mode: Modo de ejecución ('remote', 'internal', 'network')
            remote_host: Host remoto (si mode=remote)
        """
        target = remote_host or 'kubernetes-cluster'

        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='kube-hunter',
            options={
                'mode': mode,
                'remote_host': remote_host
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'kubehunter_{scan.id}.json'

            command = ['kube-hunter', '--report', 'json']

            if mode == 'remote' and remote_host:
                command.extend(['--remote', remote_host])
            elif mode == 'internal':
                command.append('--pod')
            elif mode == 'network':
                command.append('--cidr')

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting Kube-hunter {scan.id}")

            self.executor.execute_scan_in_thread(
                scan.id, sanitized_cmd, output_file, 'kube-hunter', timeout=900
            )
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'kube-hunter',
                'target': target,
                'mode': mode
            }

        except Exception as e:
            logger.error(f"Error starting Kube-hunter: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

