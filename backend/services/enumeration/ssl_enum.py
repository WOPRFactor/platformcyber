"""
SSL/TLS Enumeration Service
============================

Servicios para análisis SSL/TLS:
- sslscan (scanner SSL rápido)
- sslyze (análisis SSL/TLS avanzado)
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import CommandSanitizer, IPValidator, DomainValidator
from .base import BaseEnumerationService

logger = logging.getLogger(__name__)


class SSLEnumerationService(BaseEnumerationService):
    """Servicio para análisis SSL/TLS."""
    
    def start_sslscan(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        port: int = 443,
        show_certificate: bool = False
    ) -> Dict[str, Any]:
        """
        Análisis SSL con sslscan.
        
        Args:
            target: IP o dominio objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            port: Puerto SSL/TLS (default: 443)
            show_certificate: Mostrar certificado completo
        
        Returns:
            Dict con información del escaneo
        """
        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='sslscan',
            options={'port': port}
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = str(workspace_output_dir / f'sslscan_{scan.id}.txt')
            
            target_with_port = f'{target}:{port}'
            command = ['sslscan', target_with_port]
            
            if show_certificate:
                command.append('--show-certificate')
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting sslscan {scan.id}")
            
            self._start_scan_thread(scan.id, sanitized_cmd, output_file, 'sslscan', timeout=300)
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'sslscan',
                'target': target,
                'port': port
            }
            
        except Exception as e:
            logger.error(f"Error starting sslscan: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def start_sslyze(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        port: int = 443,
        regular: bool = True
    ) -> Dict[str, Any]:
        """
        Análisis SSL/TLS con sslyze.
        
        Args:
            target: IP o dominio objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            port: Puerto SSL/TLS (default: 443)
            regular: Usar modo regular (--regular)
        
        Returns:
            Dict con información del escaneo
        """
        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='sslyze',
            options={'port': port}
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = str(workspace_output_dir / f'sslyze_{scan.id}.txt')
            
            target_with_port = f'{target}:{port}'
            command = ['sslyze', target_with_port]
            
            if regular:
                command.append('--regular')
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting sslyze {scan.id}")
            
            self._start_scan_thread(scan.id, sanitized_cmd, output_file, 'sslyze', timeout=600)
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'sslyze',
                'target': target,
                'port': port
            }
            
        except Exception as e:
            logger.error(f"Error starting sslyze: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

    # ============================================
    # PREVIEW METHODS
    # ============================================

    def preview_sslscan(
        self,
        target: str,
        workspace_id: int,
        port: int = 443,
        show_certificate: bool = False
    ) -> Dict[str, Any]:
        """Preview del comando sslscan."""
        output_file = f'/workspaces/workspace_{workspace_id}/enumeration/sslscan_{{scan_id}}.txt'
        
        target_with_port = f'{target}:{port}'
        command = ['sslscan', target_with_port]
        
        if show_certificate:
            command.append('--show-certificate')

        command_str = ' '.join([str(c) for c in command])

        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'sslscan',
                'target': target,
                'port': port,
                'show_certificate': show_certificate
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }

    def preview_sslyze(
        self,
        target: str,
        workspace_id: int,
        port: int = 443,
        regular: bool = True
    ) -> Dict[str, Any]:
        """Preview del comando sslyze."""
        output_file = f'/workspaces/workspace_{workspace_id}/enumeration/sslyze_{{scan_id}}.txt'
        
        target_with_port = f'{target}:{port}'
        command = ['sslyze', target_with_port]
        
        if regular:
            command.append('--regular')

        command_str = ' '.join([str(c) for c in command])

        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'sslyze',
                'target': target,
                'port': port,
                'regular': regular
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }

