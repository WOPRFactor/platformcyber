"""
Naabu Scanner
=============

Scanner rápido de descubrimiento de puertos usando Naabu.
"""

import logging
import json
from typing import Dict, Any, Optional

from utils.validators import CommandSanitizer
from utils.workspace_logger import log_to_workspace
from ..base import BaseScanningService
from ..executors.scan_executor import ScanningExecutor

logger = logging.getLogger(__name__)


class NaabuScanner(BaseScanningService):
    """Scanner rápido de descubrimiento de puertos con Naabu."""
    
    def __init__(self, scan_repository=None):
        """Inicializa el scanner de Naabu."""
        super().__init__(scan_repository)
        self.executor = ScanningExecutor(scan_repository)
    
    def start_scan(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        top_ports: Optional[int] = None,
        rate: int = 1000,
        verify: bool = True
    ) -> Dict[str, Any]:
        """
        Inicia Naabu (port discovery rápido).
        
        Args:
            target: Target
            workspace_id: ID del workspace
            user_id: ID del usuario
            top_ports: Top N puertos (100, 1000, etc)
            rate: Rate de paquetes/segundo
            verify: Verificar puertos abiertos
        
        Returns:
            Dict con información del scan iniciado
        """
        CommandSanitizer.validate_target(target)
        
        scan = self._create_scan(
            scan_type='port_scan',
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='naabu',
            options={
                'top_ports': top_ports,
                'rate': rate,
                'verify': verify
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'scans')
            output_file = str(workspace_output_dir / f'naabu_{scan.id}.txt')
            
            command = [
                'naabu',
                '-host', target,
                '-rate', str(rate),
                '-o', output_file,
                '-json'
            ]
            
            if top_ports:
                command.extend(['-top-ports', str(top_ports)])
            
            if verify:
                command.append('-verify')
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            log_to_workspace(
                workspace_id=workspace_id,
                source='NAABU',
                level='INFO',
                message=f"Starting Naabu {scan.id}",
                metadata={'scan_id': scan.id, 'target': target}
            )
            
            self.executor.execute_async(
                scan_id=scan.id,
                command=sanitized_cmd,
                output_file=output_file,
                tool='naabu',
                workspace_id=workspace_id
            )
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'naabu',
                'target': target
            }
            
        except Exception as e:
            log_to_workspace(
                workspace_id=workspace_id,
                source='NAABU',
                level='ERROR',
                message=f"Error starting Naabu: {str(e)}",
                metadata={'target': target, 'error': str(e)}
            )
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def preview_scan(
        self,
        target: str,
        workspace_id: int,
        top_ports: Optional[int] = None,
        rate: int = 1000,
        verify: bool = True
    ) -> Dict[str, Any]:
        """Preview del comando Naabu."""
        CommandSanitizer.validate_target(target)
        
        output_file = f'/workspaces/workspace_{workspace_id}/scans/naabu_{{scan_id}}.txt'
        command = [
            'naabu',
            '-host', target,
            '-rate', str(rate),
            '-o', output_file,
            '-json'
        ]
        
        if top_ports:
            command.extend(['-top-ports', str(top_ports)])
        
        if verify:
            command.append('-verify')
        
        command_str = ' '.join([str(c) for c in command])
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'naabu',
                'target': target,
                'top_ports': top_ports,
                'rate': rate,
                'verify': verify
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }

