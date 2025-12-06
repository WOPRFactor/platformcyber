"""
Complete Reconnaissance Module
==============================

Módulo para reconocimiento completo y WHOIS.
"""

import logging
import threading
from typing import Dict, Any

from utils.validators import CommandSanitizer, DomainValidator, IPValidator
from .base import BaseReconnaissanceService

logger = logging.getLogger(__name__)


class CompleteReconService(BaseReconnaissanceService):
    """Servicio para reconocimiento completo."""
    
    def start_whois_lookup(
        self,
        target: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Inicia consulta WHOIS.
        
        Args:
            target: Dominio o IP objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
        
        Returns:
            Dict con información del escaneo
        """
        if not DomainValidator.is_valid_domain(target) and not IPValidator.is_valid_ip(target):
            raise ValueError(f'Invalid target: {target}')
        
        scan = self.scan_repo.create(
            scan_type='reconnaissance',
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'whois',
                'recon_type': 'whois'
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
            output_file = str(workspace_output_dir / f'whois_{scan.id}.txt')
            command = ['whois', target]
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting WHOIS lookup {scan.id} for {target}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'whois')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'whois',
                'target': target
            }
            
        except Exception as e:
            logger.error(f"Error starting WHOIS lookup: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def preview_whois_lookup(
        self,
        target: str,
        workspace_id: int
    ) -> Dict[str, Any]:
        """
        Preview del comando WHOIS (sin ejecutar).
        
        Args:
            target: Dominio o IP objetivo
            workspace_id: ID del workspace
        
        Returns:
            Dict con información del comando que se ejecutaría
        """
        from utils.validators import DomainValidator, IPValidator
        
        if not DomainValidator.is_valid_domain(target) and not IPValidator.is_valid_ip(target):
            raise ValueError(f'Invalid target: {target}')
        
        output_file = f'/workspaces/workspace_{workspace_id}/recon/whois_{{scan_id}}.txt'
        command = ['whois', target]
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'whois',
                'target': target
            },
            'estimated_timeout': 60,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def start_complete_recon(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        include_advanced: bool = False,
        subdomain_service=None,
        dns_service=None,
        email_service=None,
        osint_service=None
    ) -> Dict[str, Any]:
        """
        Inicia reconocimiento completo (todas las fases básicas).
        
        Args:
            target: Dominio o IP objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            include_advanced: Incluir herramientas avanzadas (secrets, shodan)
            subdomain_service: Servicio de subdominios (inyectado)
            dns_service: Servicio DNS (inyectado)
            email_service: Servicio de emails (inyectado)
            osint_service: Servicio OSINT (inyectado)
        
        Returns:
            Dict con información de todos los escaneos iniciados
        """
        results = {
            'target': target,
            'workspace_id': workspace_id,
            'phases': {},
            'scan_ids': []
        }
        
        # Fase 1: WHOIS
        try:
            whois_result = self.start_whois_lookup(target, workspace_id, user_id)
            results['phases']['whois'] = {
                'scan_id': whois_result['scan_id'],
                'status': 'running',
                'tool': 'whois'
            }
            results['scan_ids'].append(whois_result['scan_id'])
        except Exception as e:
            logger.error(f"Error starting WHOIS in complete recon: {e}")
            results['phases']['whois'] = {'status': 'failed', 'error': str(e)}
        
        # Fase 2: DNS (solo si es dominio)
        if DomainValidator.is_valid_domain(target) and dns_service:
            try:
                dns_result = dns_service.start_dns_recon(target, workspace_id, user_id)
                results['phases']['dns'] = {
                    'scan_id': dns_result['scan_id'],
                    'status': 'running',
                    'tool': 'dnsrecon'
                }
                results['scan_ids'].append(dns_result['scan_id'])
            except Exception as e:
                logger.error(f"Error starting DNS in complete recon: {e}")
                results['phases']['dns'] = {'status': 'failed', 'error': str(e)}
        
        # Fase 3: Subdominios (solo si es dominio)
        if DomainValidator.is_valid_domain(target) and subdomain_service:
            try:
                subdomain_result = subdomain_service.start_subdomain_enum(
                    domain=target,
                    workspace_id=workspace_id,
                    user_id=user_id,
                    tool='subfinder',
                    passive_only=True
                )
                results['phases']['subdomains'] = {
                    'scan_id': subdomain_result['scan_id'],
                    'status': 'running',
                    'tool': 'subfinder'
                }
                results['scan_ids'].append(subdomain_result['scan_id'])
            except Exception as e:
                logger.error(f"Error starting subdomain enum in complete recon: {e}")
                results['phases']['subdomains'] = {'status': 'failed', 'error': str(e)}
        
        # Fase 4: Emails (solo si es dominio)
        if DomainValidator.is_valid_domain(target) and email_service:
            try:
                email_result = email_service.start_email_harvest(
                    domain=target,
                    workspace_id=workspace_id,
                    user_id=user_id
                )
                results['phases']['emails'] = {
                    'scan_id': email_result['scan_id'],
                    'status': 'running',
                    'tool': 'theHarvester'
                }
                results['scan_ids'].append(email_result['scan_id'])
            except Exception as e:
                logger.error(f"Error starting email harvest in complete recon: {e}")
                results['phases']['emails'] = {'status': 'failed', 'error': str(e)}
        
        # Fases avanzadas (opcional)
        if include_advanced and DomainValidator.is_valid_domain(target) and osint_service:
            try:
                wayback_result = osint_service.start_wayback_urls(target, workspace_id, user_id)
                results['phases']['wayback'] = {
                    'scan_id': wayback_result['scan_id'],
                    'status': 'running',
                    'tool': 'waybackurls'
                }
                results['scan_ids'].append(wayback_result['scan_id'])
            except Exception as e:
                logger.error(f"Error starting wayback in complete recon: {e}")
                results['phases']['wayback'] = {'status': 'failed', 'error': str(e)}
        
        results['total_phases'] = len(results['phases'])
        results['status'] = 'running'
        
        return results
