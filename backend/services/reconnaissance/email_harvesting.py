"""
Email Harvesting Module
=======================

Módulo para búsqueda de emails y enumeración de personas.
Herramientas: theHarvester, Hunter.io, LinkedIn Enumeration
"""

import subprocess
import json
import logging
import threading
import os
from typing import Dict, Any, Optional

from utils.validators import CommandSanitizer, DomainValidator
from utils.workspace_logger import log_to_workspace
from .base import BaseReconnaissanceService

logger = logging.getLogger(__name__)


class EmailHarvestingService(BaseReconnaissanceService):
    """Servicio para búsqueda de emails y enumeración de personas."""
    
    def start_email_harvest(
        self,
        domain: str,
        workspace_id: int,
        user_id: int,
        sources: str = 'bing,duckduckgo,hunter',
        limit: int = 500
    ) -> Dict[str, Any]:
        """
        Busca emails con theHarvester.
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            sources: Fuentes separadas por coma
            limit: Límite de resultados
        """
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        scan = self.scan_repo.create(
            scan_type='reconnaissance',
            target=domain,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'theHarvester',
                'recon_type': 'email_harvest',
                'sources': sources,
                'limit': limit
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
            output_file = str(workspace_output_dir / f'harvester_{scan.id}')
            command = [
                'theHarvester',
                '-d', domain,
                '-b', sources,
                '-l', str(limit),
                '-f', output_file
            ]
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting email harvest {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file + '.json', 'email')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'theHarvester',
                'target': domain
            }
            
        except Exception as e:
            logger.error(f"Error starting email harvest: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def preview_email_harvest(
        self,
        domain: str,
        workspace_id: int,
        sources: str = 'bing,duckduckgo,hunter',
        limit: int = 500
    ) -> Dict[str, Any]:
        """Preview del comando theHarvester."""
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        output_file = f'/workspaces/workspace_{workspace_id}/recon/harvester_{{scan_id}}'
        command = [
            'theHarvester',
            '-d', domain,
            '-b', sources,
            '-l', str(limit),
            '-f', output_file
        ]
        command_str = ' '.join([str(c) for c in command])
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'theHarvester',
                'domain': domain,
                'sources': sources,
                'limit': limit
            },
            'estimated_timeout': 600,
            'output_file': f'{output_file}.json',
            'warnings': [],
            'suggestions': []
        }
    
    def preview_hunter_io_search(
        self,
        domain: str,
        workspace_id: int,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Preview de la búsqueda Hunter.io (sin ejecutar).
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            api_key: API key de Hunter.io (opcional)
        
        Returns:
            Dict con información de la llamada API que se ejecutaría
        """
        DomainValidator.validate(domain)
        
        api_key_final = api_key or os.getenv('HUNTER_IO_API_KEY') or '[API_KEY_FROM_ENV]'
        url = "https://api.hunter.io/v2/domain-search"
        params = {
            'domain': domain,
            'api_key': api_key_final if api_key_final != '[API_KEY_FROM_ENV]' else '[API_KEY]'
        }
        
        # Construir URL con parámetros para mostrar
        import urllib.parse
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"
        
        output_file = f'/workspaces/workspace_{workspace_id}/recon/hunter_io_{{scan_id}}.json'
        
        return {
            'command': ['curl', '-s', full_url],
            'command_string': f'curl -s "{url}?domain={domain}&api_key=[API_KEY]"',
            'parameters': {
                'domain': domain,
                'api_key': '[CONFIGURED]' if api_key_final != '[API_KEY_FROM_ENV]' else '[NOT_SET]'
            },
            'estimated_timeout': 30,
            'output_file': output_file,
            'warnings': ['Requiere API key de Hunter.io configurada'] if not api_key_final or api_key_final == '[API_KEY_FROM_ENV]' else [],
            'suggestions': []
        }
    
    def start_hunter_io_search(
        self,
        domain: str,
        workspace_id: int,
        user_id: int,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Busca emails corporativos usando Hunter.io API.
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            api_key: API key de Hunter.io (opcional, puede estar en env)
        
        Returns:
            Dict con información del escaneo iniciado
        """
        DomainValidator.validate(domain)
        CommandSanitizer.validate_target(domain)
        
        scan = self.scan_repo.create_scan(
            scan_type='hunter_io',
            target=domain,
            workspace_id=workspace_id,
            user_id=user_id,
            status='running'
        )
        
        workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
        output_file = workspace_output_dir / f"hunter_io_{scan.id}.json"
        
        try:
            def execute_scan():
                try:
                    import requests
                    
                    api_key_final = api_key or os.getenv('HUNTER_IO_API_KEY')
                    
                    if not api_key_final:
                        raise ValueError("Hunter.io API key no proporcionada. Configura HUNTER_IO_API_KEY en variables de entorno o pásala como parámetro.")
                    
                    url = f"https://api.hunter.io/v2/domain-search"
                    params = {
                        'domain': domain,
                        'api_key': api_key_final
                    }
                    
                    response = requests.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    with open(output_file, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    emails_found = data.get('data', {}).get('emails', [])
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source='reconnaissance',
                        level='info',
                        message=f"Hunter.io: {len(emails_found)} emails encontrados para {domain}",
                        task_id=None
                    )
                    
                    self.scan_repo.update_status(scan, 'completed')
                    
                except Exception as e:
                    logger.error(f"Hunter.io API error: {e}")
                    self.scan_repo.update_status(scan, 'failed', f"API Error: {str(e)}")
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source='reconnaissance',
                        level='error',
                        message=f"Error en Hunter.io API: {str(e)}",
                        task_id=None
                    )
            
            thread = threading.Thread(target=execute_scan)
            thread.daemon = True
            thread.start()
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'hunter_io',
                'domain': domain
            }
            
        except Exception as e:
            logger.error(f"Error starting Hunter.io: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def preview_linkedin_enum(
        self,
        domain: str,
        workspace_id: int,
        company_name: Optional[str] = None,
        tool: str = 'crosslinked'
    ) -> Dict[str, Any]:
        """
        Preview del comando LinkedIn enum (sin ejecutar).
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            company_name: Nombre de la compañía (opcional)
            tool: 'crosslinked' | 'linkedin2username'
        
        Returns:
            Dict con información del comando que se ejecutaría
        """
        DomainValidator.validate(domain)
        
        if not company_name:
            company_name = domain.split('.')[0].title()
        
        output_file = f'/workspaces/workspace_{workspace_id}/recon/linkedin_enum_{{scan_id}}.txt'
        
        if tool == 'crosslinked':
            email_pattern = f"{{first}}.{{last}}@{domain}"
            command = ['crosslinked', '-f', email_pattern, company_name]
        elif tool == 'linkedin2username':
            command = ['linkedin2username', '-u', f"user@{domain}", '-c', company_name]
        else:
            raise ValueError(f'Invalid tool: {tool}. Must be "crosslinked" or "linkedin2username"')
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': tool,
                'domain': domain,
                'company_name': company_name
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def start_linkedin_enum(
        self,
        domain: str,
        workspace_id: int,
        user_id: int,
        company_name: Optional[str] = None,
        tool: str = 'crosslinked'
    ) -> Dict[str, Any]:
        """
        Enumera empleados usando LinkedIn.
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            company_name: Nombre de la compañía (opcional)
            tool: 'crosslinked' | 'linkedin2username'
        
        Returns:
            Dict con información del escaneo iniciado
        """
        DomainValidator.validate(domain)
        CommandSanitizer.validate_target(domain)
        
        scan = self.scan_repo.create_scan(
            scan_type='linkedin_enum',
            target=domain,
            workspace_id=workspace_id,
            user_id=user_id,
            status='running'
        )
        
        workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
        output_file = workspace_output_dir / f"linkedin_enum_{scan.id}.txt"
        
        try:
            def execute_scan():
                try:
                    if tool == 'crosslinked':
                        if not company_name:
                            company_name = domain.split('.')[0].title()
                        
                        email_pattern = f"{{first}}.{{last}}@{domain}"
                        cmd = ['crosslinked', '-f', email_pattern, company_name]
                        
                        with open(output_file, 'w') as f:
                            result = subprocess.run(
                                cmd,
                                capture_output=True,
                                text=True,
                                timeout=600
                            )
                            f.write(result.stdout)
                            if result.stderr:
                                f.write(f"\n\nSTDERR:\n{result.stderr}")
                        
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source='reconnaissance',
                            level='info',
                            message=f"CrossLinked completado para {domain}",
                            task_id=None
                        )
                        
                    elif tool == 'linkedin2username':
                        if not company_name:
                            company_name = domain.split('.')[0].title()
                        
                        cmd = ['linkedin2username', '-u', f"user@{domain}", '-c', company_name]
                        
                        with open(output_file, 'w') as f:
                            result = subprocess.run(
                                cmd,
                                capture_output=True,
                                text=True,
                                timeout=600
                            )
                            f.write(result.stdout)
                            if result.stderr:
                                f.write(f"\n\nSTDERR:\n{result.stderr}")
                        
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source='reconnaissance',
                            level='info',
                            message=f"linkedin2username completado para {domain}",
                            task_id=None
                        )
                    
                    self.scan_repo.update_status(scan, 'completed')
                    
                except subprocess.TimeoutExpired:
                    logger.error(f"LinkedIn Enum timeout for {domain}")
                    self.scan_repo.update_status(scan, 'failed', 'Timeout')
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source='reconnaissance',
                        level='error',
                        message=f"LinkedIn Enum timeout para {domain}",
                        task_id=None
                    )
                except Exception as e:
                    logger.error(f"Error in LinkedIn Enum scan: {e}")
                    self.scan_repo.update_status(scan, 'failed', str(e))
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source='reconnaissance',
                        level='error',
                        message=f"Error en LinkedIn Enum: {str(e)}",
                        task_id=None
                    )
            
            thread = threading.Thread(target=execute_scan)
            thread.daemon = True
            thread.start()
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': tool,
                'domain': domain
            }
            
        except Exception as e:
            logger.error(f"Error starting LinkedIn Enum: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise


