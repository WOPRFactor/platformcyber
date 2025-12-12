"""
OSINT Tools Module
==================

Módulo para herramientas OSINT.
Herramientas: Shodan, Censys, Wayback URLs
"""

import os
import logging
import threading
from typing import Dict, Any, Optional

from utils.validators import CommandSanitizer
from utils.workspace_logger import log_to_workspace
from .base import BaseReconnaissanceService

logger = logging.getLogger(__name__)


class OSINTToolsService(BaseReconnaissanceService):
    """Servicio para herramientas OSINT."""
    
    def start_shodan_search(
        self,
        query: str,
        workspace_id: int,
        user_id: int,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Busca información en Shodan.
        
        Args:
            query: Query de búsqueda (IP, domain, org)
            workspace_id: ID del workspace
            user_id: ID del usuario
            api_key: API key de Shodan
        
        Note:
            Requiere shodan CLI instalado y configurado
        """
        scan = self.scan_repo.create(
            scan_type='reconnaissance',
            target=query,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'shodan',
                'recon_type': 'osint'
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
            output_file = str(workspace_output_dir / f'shodan_{scan.id}.json')
            
            # Obtener API key de parámetro, variable de entorno o configuración de shodan CLI
            api_key_final = api_key or os.getenv('SHODAN_API_KEY')
            
            command = [
                'shodan', 'search', '--fields',
                'ip_str,port,org,data,vulns', query
            ]
            
            if api_key_final:
                command.extend(['--api-key', api_key_final])
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting Shodan search {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'shodan')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'shodan',
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Error starting Shodan search: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def start_censys_search(
        self,
        query: str,
        workspace_id: int,
        user_id: int,
        index_type: str = 'hosts',
        api_id: Optional[str] = None,
        api_secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Busca información en Censys.
        
        Args:
            query: Query de búsqueda
            workspace_id: ID del workspace
            user_id: ID del usuario
            index_type: Tipo de índice ('hosts' o 'certificates')
            api_id: API ID de Censys (opcional, puede estar en env)
            api_secret: API Secret de Censys (opcional, puede estar en env)
        
        Returns:
            Dict con información del escaneo
        """
        scan = self.scan_repo.create(
            scan_type='reconnaissance',
            target=query,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'censys',
                'recon_type': 'osint',
                'index_type': index_type
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
            output_file = str(workspace_output_dir / f'censys_{scan.id}.json')
            
            api_id = api_id or os.getenv('CENSYS_API_ID')
            api_secret = api_secret or os.getenv('CENSYS_API_SECRET')
            
            if not api_id or not api_secret:
                raise ValueError('Censys API credentials required (CENSYS_API_ID and CENSYS_API_SECRET)')
            
            command = [
                'censys', 'search', query,
                '--index-type', index_type,
                '--api-id', api_id,
                '--api-secret', api_secret
            ]
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            log_to_workspace(
                workspace_id=workspace_id,
                source='CENSYS',
                level='INFO',
                message=f"Iniciando búsqueda Censys ({index_type}) para: {query}",
                metadata={'scan_id': scan.id, 'query': query, 'index_type': index_type}
            )
            
            logger.info(f"Starting Censys search {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'censys')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'censys',
                'query': query,
                'index_type': index_type
            }
            
        except Exception as e:
            logger.error(f"Error starting Censys search: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def start_wayback_urls(
        self,
        domain: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Obtiene URLs históricas de Wayback Machine.
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
        """
        from utils.validators import DomainValidator
        
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        scan = self.scan_repo.create(
            scan_type='reconnaissance',
            target=domain,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'waybackurls',
                'recon_type': 'historical'
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
            output_file = str(workspace_output_dir / f'wayback_{scan.id}.txt')
            command = ['waybackurls', domain]
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting Wayback URLs {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'wayback')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'waybackurls',
                'target': domain
            }
            
        except Exception as e:
            logger.error(f"Error starting Wayback URLs: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def preview_shodan_search(
        self,
        query: str,
        workspace_id: int,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando Shodan."""
        output_file = f'/workspaces/workspace_{workspace_id}/recon/shodan_{{scan_id}}.json'
        api_key_final = api_key or os.getenv('SHODAN_API_KEY')
        
        command = [
            'shodan', 'search', '--fields',
            'ip_str,port,org,data,vulns', query
        ]
        if api_key_final:
            command.extend(['--api-key', api_key_final])
        
        command_str = ' '.join([str(c) for c in command])
        
        warnings = []
        if not api_key_final:
            warnings.append('API key no configurada. El comando puede fallar.')
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'shodan',
                'query': query,
                'api_key': '***' if api_key_final else None
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': warnings,
            'suggestions': []
        }
    
    def preview_censys_search(
        self,
        query: str,
        workspace_id: int,
        index_type: str = 'hosts',
        api_id: Optional[str] = None,
        api_secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando Censys."""
        output_file = f'/workspaces/workspace_{workspace_id}/recon/censys_{{scan_id}}.json'
        api_id_final = api_id or os.getenv('CENSYS_API_ID')
        api_secret_final = api_secret or os.getenv('CENSYS_API_SECRET')
        
        command = [
            'censys', 'search', query,
            '--index-type', index_type
        ]
        if api_id_final:
            command.extend(['--api-id', api_id_final])
        if api_secret_final:
            command.extend(['--api-secret', api_secret_final])
        
        command_str = ' '.join([str(c) for c in command])
        
        warnings = []
        if not api_id_final or not api_secret_final:
            warnings.append('API credentials no configuradas. El comando puede fallar.')
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'censys',
                'query': query,
                'index_type': index_type,
                'api_id': '***' if api_id_final else None,
                'api_secret': '***' if api_secret_final else None
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': warnings,
            'suggestions': []
        }
    
    def preview_wayback_urls(
        self,
        domain: str,
        workspace_id: int
    ) -> Dict[str, Any]:
        """Preview del comando waybackurls."""
        import shutil
        from utils.validators import DomainValidator
        
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        output_file = f'/workspaces/workspace_{workspace_id}/recon/wayback_{{scan_id}}.txt'
        command = ['waybackurls', domain]
        command_str = ' '.join(command)
        
        warnings = []
        # Verificar si la herramienta está instalada
        if not shutil.which('waybackurls'):
            warnings.append('Herramienta "waybackurls" no encontrada en el PATH. Instalar: go install github.com/tomnomnom/waybackurls@latest')
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'waybackurls',
                'domain': domain
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': warnings,
            'suggestions': []
        }
