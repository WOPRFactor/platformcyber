"""
Nmap Scanner
============

Scanner de puertos usando Nmap con múltiples tipos de scan.
"""

import logging
from typing import Dict, Any, Optional, List

from utils.validators import CommandSanitizer
from utils.commands import SafeNmap
from utils.workspace_logger import log_to_workspace
from ..base import BaseScanningService
from ..executors.scan_executor import ScanningExecutor

logger = logging.getLogger(__name__)


class NmapScanner(BaseScanningService):
    """Scanner de puertos con Nmap."""
    
    def __init__(self, scan_repository=None):
        """Inicializa el scanner de Nmap."""
        super().__init__(scan_repository)
        self.executor = ScanningExecutor(scan_repository)
    
    def start_scan(
        self,
        target: str,
        scan_type: str,
        workspace_id: int,
        user_id: int,
        ports: Optional[str] = None,
        scripts: Optional[List[str]] = None,
        os_detection: bool = False,
        version_detection: bool = False
    ) -> Dict[str, Any]:
        """
        Inicia un escaneo Nmap completo.
        
        Args:
            target: Target (IP, CIDR, hostname)
            scan_type: Tipo (discovery, stealth, comprehensive, quick, vuln, udp, service, os, custom)
            workspace_id: ID del workspace
            user_id: ID del usuario
            ports: Puertos específicos
            scripts: Scripts NSE a ejecutar
            os_detection: Activar detección de OS
            version_detection: Activar detección de versiones
        
        Returns:
            Dict con información del scan iniciado
        """
        CommandSanitizer.validate_target(target)
        
        scan = self._create_scan(
            scan_type='port_scan',
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='nmap',
            options={
                'scan_type': scan_type,
                'ports': ports,
                'scripts': scripts,
                'os_detection': os_detection,
                'version_detection': version_detection
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'scans')
            output_file = str(workspace_output_dir / f'nmap_{scan.id}')
            
            # Construir comando según tipo
            command = self._build_command(scan_type, target, output_file, ports, scripts, os_detection, version_detection)
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            log_to_workspace(
                workspace_id=workspace_id,
                source='NMAP',
                level='INFO',
                message=f"Starting Nmap {scan_type} scan {scan.id}",
                metadata={'scan_id': scan.id, 'target': target, 'scan_type': scan_type}
            )
            
            self.executor.execute_async(
                scan_id=scan.id,
                command=sanitized_cmd,
                output_file=f'{output_file}.xml',
                tool='nmap',
                workspace_id=workspace_id
            )
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'nmap',
                'scan_type': scan_type,
                'target': target
            }
            
        except Exception as e:
            log_to_workspace(
                workspace_id=workspace_id,
                source='NMAP',
                level='ERROR',
                message=f"Error starting Nmap scan: {str(e)}",
                metadata={'target': target, 'error': str(e)}
            )
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def _build_command(
        self,
        scan_type: str,
        target: str,
        output_file: str,
        ports: Optional[str],
        scripts: Optional[List[str]],
        os_detection: bool,
        version_detection: bool
    ) -> List[str]:
        """Construye el comando Nmap según el tipo de scan."""
        if scan_type == 'discovery':
            return SafeNmap.build_discovery_scan(target, output_file)
        elif scan_type == 'quick':
            return [
                'nmap', '-T4', '--top-ports', '100',
                '-oX', f'{output_file}.xml', '-oN', f'{output_file}.txt', target
            ]
        elif scan_type == 'stealth':
            return SafeNmap.build_stealth_scan(target, ports or 'top-1000', output_file)
        elif scan_type == 'comprehensive':
            return [
                'nmap', '-sS', '-sV', '-O', '-T4', '--osscan-guess',
                '-p', ports or '1-65535',
                '-oX', f'{output_file}.xml', '-oN', f'{output_file}.txt', target
            ]
        elif scan_type == 'service':
            return [
                'nmap', '-sV', '-O', '-T4', '--top-ports', '1000',
                '-oX', f'{output_file}.xml', '-oN', f'{output_file}.txt', target
            ]
        elif scan_type == 'os':
            return [
                'nmap', '-O', '--osscan-guess', '-T4', '--top-ports', '1000',
                '-oX', f'{output_file}.xml', '-oN', f'{output_file}.txt', target
            ]
        elif scan_type == 'vuln':
            return SafeNmap.build_vuln_scan(target, ports, output_file)
        elif scan_type == 'udp':
            return SafeNmap.build_udp_scan(target, output_file)
        elif scan_type == 'custom':
            command = ['nmap']
            if version_detection:
                command.append('-sV')
            if os_detection:
                command.append('-O')
            if scripts:
                command.extend(['--script', ','.join(scripts)])
            if ports:
                command.extend(['-p', ports])
            command.extend(['-oX', f'{output_file}.xml', '-oN', f'{output_file}.txt', target])
            return command
        else:
            raise ValueError(f'Invalid scan_type: {scan_type}')
    
    def preview_scan(
        self,
        target: str,
        scan_type: str,
        workspace_id: int,
        ports: Optional[str] = None,
        scripts: Optional[List[str]] = None,
        os_detection: bool = False,
        version_detection: bool = False
    ) -> Dict[str, Any]:
        """Preview del comando Nmap (sin ejecutar)."""
        CommandSanitizer.validate_target(target)
        
        output_file = f'/workspaces/workspace_{workspace_id}/scans/nmap_{{scan_id}}'
        command = self._build_command(scan_type, target, output_file, ports, scripts, os_detection, version_detection)
        command_str = ' '.join([str(c) for c in command])
        
        timeout_map = {
            'discovery': 300, 'quick': 120, 'stealth': 600, 'comprehensive': 3600,
            'service': 1800, 'os': 1200, 'vuln': 2400, 'udp': 1800, 'custom': 1800
        }
        
        warnings = []
        suggestions = []
        
        if scan_type == 'comprehensive' and not ports:
            warnings.append('Escaneo completo sin límite de puertos puede tardar mucho tiempo')
            suggestions.append('Considera especificar un rango de puertos específico')
        
        if scan_type == 'vuln':
            suggestions.append('Este escaneo puede ser detectado por sistemas de seguridad')
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'nmap',
                'target': target,
                'scan_type': scan_type,
                'ports': ports,
                'scripts': scripts,
                'os_detection': os_detection,
                'version_detection': version_detection
            },
            'estimated_timeout': timeout_map.get(scan_type, 1800),
            'output_file': f'{output_file}.xml',
            'warnings': warnings,
            'suggestions': suggestions
        }


