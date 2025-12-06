"""
Kube-bench Scanner
=================

CIS Kubernetes Benchmark con Kube-bench.
"""

import logging
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from utils.parsers.container_parser import KubeBenchParser
from ..base import BaseContainerService

logger = logging.getLogger(__name__)


class KubeBenchScanner(BaseContainerService):
    """Scanner Kube-bench para CIS Kubernetes Benchmark."""

    def __init__(self, scan_repository=None):
        super().__init__(scan_repository)
        self.kubebench_parser = KubeBenchParser()

    def run_scan(
        self,
        workspace_id: int,
        user_id: int,
        targets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta Kube-bench (CIS Kubernetes Benchmark).
        
        Args:
            workspace_id: ID del workspace
            user_id: ID del usuario
            targets: Targets específicos (master, node, etcd, etc.)
        """
        scan = self._create_scan(
            target='kubernetes-cluster',
            workspace_id=workspace_id,
            user_id=user_id,
            tool='kube-bench',
            options={'targets': targets or ['master', 'node']}
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'kubebench_{scan.id}.json'

            command = ['kube-bench', 'run', '--json', '--outputfile', str(output_file)]

            if targets:
                command.extend(['--targets', ','.join(targets)])

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting Kube-bench {scan.id}")

            # Ejecutar sync
            result = subprocess.run(
                sanitized_cmd,
                capture_output=True,
                text=True,
                timeout=300,
                env=CommandSanitizer.get_safe_env()
            )

            # Kube-bench siempre retorna exit code != 0 si encuentra issues
            # Así que no validamos returncode

            if output_file.exists():
                self.scan_repo.update_status(scan, 'completed')
                self.scan_repo.update_progress(scan, 100, 'Kube-bench completed')

                with open(output_file, 'r') as f:
                    results = self.kubebench_parser.parse_results(f.read())

                return {
                    'scan_id': scan.id,
                    'status': 'completed',
                    'tool': 'kube-bench',
                    'results': results
                }
            else:
                self.scan_repo.update_status(scan, 'failed', result.stderr)
                raise Exception('Kube-bench output not found')

        except Exception as e:
            logger.error(f"Error running Kube-bench: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

