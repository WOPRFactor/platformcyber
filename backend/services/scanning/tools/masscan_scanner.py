"""
Masscan Scanner
===============

Scanner masivo de puertos usando Masscan.
"""

import logging
from typing import Dict, Any

from utils.validators import CommandSanitizer
from utils.commands import SafeMasscan
from utils.workspace_logger import log_to_workspace
from ..base import BaseScanningService
from ..executors.scan_executor import ScanningExecutor

logger = logging.getLogger(__name__)


class MasscanScanner(BaseScanningService):
    """Scanner masivo de puertos con Masscan."""
    
    def __init__(self, scan_repository=None):
        """Inicializa el scanner de Masscan."""
        super().__init__(scan_repository)
        self.executor = ScanningExecutor(scan_repository)
    
    def start_scan(
        self,
        target: str,
        ports: str,
        workspace_id: int,
        user_id: int,
        rate: int = 1000,
        environment: str = 'internal'
    ) -> Dict[str, Any]:
        """
        Inicia Masscan (scan masivo).
        
        Args:
            target: Target (IP, CIDR)
            ports: Puertos (ej: "1-65535" o "80,443,8080")
            workspace_id: ID del workspace
            user_id: ID del usuario
            rate: Rate de paquetes/segundo
            environment: internal/external/stealth
        
        Returns:
            Dict con información del scan iniciado
        """
        CommandSanitizer.validate_target(target)
        
        scan = self._create_scan(
            scan_type='port_scan',
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='masscan',
            options={
                'ports': ports,
                'rate': rate,
                'environment': environment
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'scans')
            output_file = str(workspace_output_dir / f'masscan_{scan.id}.json')
            
            command = SafeMasscan.build_scan(target, ports, environment, output_file)
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            log_to_workspace(
                workspace_id=workspace_id,
                source='MASSCAN',
                level='INFO',
                message=f"Starting Masscan {scan.id} with rate {rate}",
                metadata={'scan_id': scan.id, 'target': target, 'rate': rate}
            )
            
            self.executor.execute_async(
                scan_id=scan.id,
                command=sanitized_cmd,
                output_file=output_file,
                tool='masscan',
                workspace_id=workspace_id
            )
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'masscan',
                'target': target,
                'rate': rate
            }
            
        except Exception as e:
            log_to_workspace(
                workspace_id=workspace_id,
                source='MASSCAN',
                level='ERROR',
                message=f"Error starting Masscan: {str(e)}",
                metadata={'target': target, 'error': str(e)}
            )
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def preview_scan(
        self,
        target: str,
        ports: str,
        workspace_id: int,
        rate: int = 1000,
        environment: str = 'internal'
    ) -> Dict[str, Any]:
        """Preview del comando Masscan."""
        CommandSanitizer.validate_target(target)
        
        output_file = f'/workspaces/workspace_{workspace_id}/scans/masscan_{{scan_id}}.json'
        command = SafeMasscan.build_scan(target, ports, environment, output_file)
        command_str = ' '.join([str(c) for c in command])
        
        warnings = []
        if rate > 10000:
            warnings.append('Rate muy alto puede causar problemas de red')
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'masscan',
                'target': target,
                'ports': ports,
                'rate': rate,
                'environment': environment
            },
            'estimated_timeout': 1800,
            'output_file': output_file,
            'warnings': warnings,
            'suggestions': []
        }

