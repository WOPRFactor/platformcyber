"""
Kubescape Scanner
=================

Kubernetes security platform con Kubescape.
"""

import logging
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from utils.parsers.container_parser import KubescapeParser
from ..base import BaseContainerService

logger = logging.getLogger(__name__)


class KubescapeScanner(BaseContainerService):
    """Scanner Kubescape para security scanning de K8s."""

    def __init__(self, scan_repository=None):
        super().__init__(scan_repository)
        self.kubescape_parser = KubescapeParser()

    def run_scan(
        self,
        workspace_id: int,
        user_id: int,
        framework: str = 'nsa',
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta Kubescape para security scanning de K8s.
        
        Args:
            workspace_id: ID del workspace
            user_id: ID del usuario
            framework: Framework a usar (nsa, mitre, armobest)
            namespace: Namespace específico (opcional)
        """
        target = namespace or 'all-namespaces'

        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='kubescape',
            options={
                'framework': framework,
                'namespace': namespace
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'kubescape_{scan.id}.json'

            command = [
                'kubescape', 'scan', 'framework', framework,
                '--format', 'json',
                '--output', str(output_file)
            ]

            if namespace:
                command.extend(['--namespace', namespace])

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting Kubescape {scan.id}")

            # Ejecutar sync
            result = subprocess.run(
                sanitized_cmd,
                capture_output=True,
                text=True,
                timeout=600,
                env=CommandSanitizer.get_safe_env()
            )

            if result.returncode == 0 or output_file.exists():
                self.scan_repo.update_status(scan, 'completed')
                self.scan_repo.update_progress(scan, 100, 'Kubescape completed')

                with open(output_file, 'r') as f:
                    results = self.kubescape_parser.parse_results(f.read())

                return {
                    'scan_id': scan.id,
                    'status': 'completed',
                    'tool': 'kubescape',
                    'framework': framework,
                    'results': results
                }
            else:
                self.scan_repo.update_status(scan, 'failed', result.stderr)
                raise Exception(result.stderr)

        except Exception as e:
            logger.error(f"Error running Kubescape: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

