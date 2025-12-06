"""
RustScan Scanner
================

Scanner rápido de puertos usando RustScan.
"""

import logging
import subprocess
import os
import shutil
from typing import Dict, Any

from utils.validators import CommandSanitizer
from utils.workspace_logger import log_to_workspace
from ..base import BaseScanningService
from ..executors.scan_executor import ScanningExecutor

logger = logging.getLogger(__name__)


class RustScanScanner(BaseScanningService):
    """Scanner rápido de puertos con RustScan."""
    
    def __init__(self, scan_repository=None):
        """Inicializa el scanner de RustScan."""
        super().__init__(scan_repository)
        self.executor = ScanningExecutor(scan_repository)
    
    def _find_rustscan(self) -> str:
        """Busca RustScan en ubicaciones comunes."""
        rustscan_path = shutil.which('rustscan')
        if rustscan_path:
            return rustscan_path
        
        # Intentar ejecutar directamente
        try:
            result = subprocess.run(
                ['rustscan', '--help'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 or 'RustScan' in result.stdout or 'RustScan' in result.stderr:
                return 'rustscan'
        except Exception:
            pass
        
        # Buscar en ubicaciones comunes
        common_paths = [
            '/usr/local/bin/rustscan',
            '/usr/bin/rustscan',
            os.path.expanduser('~/.cargo/bin/rustscan'),
            os.path.expanduser('~/.local/bin/rustscan'),
        ]
        
        for path in common_paths:
            try:
                result = subprocess.run(
                    [path, '--help'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0 or 'RustScan' in result.stdout or 'RustScan' in result.stderr:
                    return path
            except Exception:
                continue
        
        return 'rustscan'  # Usar directamente si no se encuentra
    
    def start_scan(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        batch_size: int = 4000,
        timeout: int = 1500,
        ulimit: int = 5000
    ) -> Dict[str, Any]:
        """
        Inicia RustScan (escaneo ultra-rápido).
        
        Args:
            target: Target (IP o hostname)
            workspace_id: ID del workspace
            user_id: ID del usuario
            batch_size: Tamaño del batch
            timeout: Timeout en ms
            ulimit: Límite de file descriptors
        
        Returns:
            Dict con información del scan iniciado
        """
        CommandSanitizer.validate_target(target)
        
        scan = self._create_scan(
            scan_type='port_scan',
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='rustscan',
            options={
                'batch_size': batch_size,
                'timeout': timeout,
                'ulimit': ulimit
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'scans')
            output_file = str(workspace_output_dir / f'rustscan_{scan.id}.txt')
            
            rustscan_executable = self._find_rustscan()
            
            command = [
                rustscan_executable,
                '-a', target,
                '-b', str(batch_size),
                '-t', str(timeout),
                '--ulimit', str(ulimit),
                '--greppable'
            ]
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            log_to_workspace(
                workspace_id=workspace_id,
                source='RUSTSCAN',
                level='INFO',
                message=f"Starting RustScan {scan.id}",
                metadata={'scan_id': scan.id, 'target': target}
            )
            
            self.executor.execute_async(
                scan_id=scan.id,
                command=sanitized_cmd,
                output_file=output_file,
                tool='rustscan',
                workspace_id=workspace_id
            )
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'rustscan',
                'target': target
            }
            
        except Exception as e:
            log_to_workspace(
                workspace_id=workspace_id,
                source='RUSTSCAN',
                level='ERROR',
                message=f"Error starting RustScan: {str(e)}",
                metadata={'target': target, 'error': str(e)}
            )
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def preview_scan(
        self,
        target: str,
        workspace_id: int,
        batch_size: int = 4000,
        timeout: int = 1500,
        ulimit: int = 5000
    ) -> Dict[str, Any]:
        """Preview del comando RustScan."""
        CommandSanitizer.validate_target(target)
        
        output_file = f'/workspaces/workspace_{workspace_id}/scans/rustscan_{{scan_id}}.txt'
        command = [
            'rustscan',
            '-a', target,
            '--batch-size', str(batch_size),
            '--timeout', str(timeout),
            '--ulimit', str(ulimit),
            '--', '-sV', '-oN', output_file
        ]
        command_str = ' '.join([str(c) for c in command])
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'rustscan',
                'target': target,
                'batch_size': batch_size,
                'timeout': timeout,
                'ulimit': ulimit
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }

