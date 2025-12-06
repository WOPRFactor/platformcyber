"""
Secrets Detection Module
========================

Módulo para detección de secrets en repositorios.
Herramientas: GitLeaks, TruffleHog
"""

import logging
import threading
from typing import Dict, Any

from utils.validators import CommandSanitizer, DomainValidator
from .base import BaseReconnaissanceService

logger = logging.getLogger(__name__)


class SecretsDetectionService(BaseReconnaissanceService):
    """Servicio para detección de secrets."""
    
    def start_secrets_scan(
        self,
        repo_url: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'gitleaks'
    ) -> Dict[str, Any]:
        """
        Busca secrets/credentials en repositorios.
        
        Args:
            repo_url: URL del repositorio
            workspace_id: ID del workspace
            user_id: ID del usuario
            tool: Herramienta (gitleaks, trufflehog)
        """
        scan = self.scan_repo.create(
            scan_type='reconnaissance',
            target=repo_url,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': tool,
                'recon_type': 'secrets'
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
            output_file = str(workspace_output_dir / f'{tool}_{scan.id}.json')
            command = self._build_secrets_command(tool, repo_url, output_file)
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting secrets scan {scan.id} with {tool}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'secrets')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': tool,
                'target': repo_url
            }
            
        except Exception as e:
            logger.error(f"Error starting secrets scan: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def _build_secrets_command(
        self,
        tool: str,
        repo_url: str,
        output_file: str
    ) -> list:
        """Construye comando de secrets según herramienta."""
        if tool == 'gitleaks':
            return [
                'gitleaks', 'detect', '--repo-url', repo_url,
                '--report-format', 'json', '--report-path', output_file,
                '--no-git'
            ]
        elif tool == 'trufflehog':
            return [
                'trufflehog', 'git', repo_url, '--json', '--only-verified'
            ]
        else:
            raise ValueError(f'Unsupported tool: {tool}')
    
    def preview_secrets_scan(
        self,
        repo_url: str,
        workspace_id: int,
        tool: str = 'gitleaks'
    ) -> Dict[str, Any]:
        """Preview del comando de secrets detection."""
        # Agregar protocolo si no lo tiene (repositorios Git requieren URL completa)
        original_url = repo_url
        if not repo_url.startswith(('http://', 'https://', 'git://', 'ssh://')):
            # Asumir HTTPS para repositorios Git
            repo_url = f'https://{repo_url}'
            logger.info(f"Secrets Scan Preview: Agregado protocolo HTTPS a repo URL: {original_url} -> {repo_url}")
        
        # Validar que sea una URL válida
        if not DomainValidator.validate_url(repo_url):
            # Si HTTPS falla, intentar HTTP
            if repo_url.startswith('https://'):
                repo_url = repo_url.replace('https://', 'http://')
                logger.info(f"Secrets Scan Preview: Cambiado a HTTP: {repo_url}")
            if not DomainValidator.validate_url(repo_url):
                logger.error(f"Secrets Scan Preview: URL inválida después de agregar protocolo: {repo_url} (original: {original_url})")
                raise ValueError(f'Invalid repository URL: {original_url}. Intenté agregar protocolo pero sigue siendo inválido.')
        
        output_file = f'/workspaces/workspace_{workspace_id}/recon/{tool}_{{scan_id}}.json'
        command = self._build_secrets_command(tool, repo_url, output_file)
        command_str = ' '.join([str(c) for c in command])
        
        timeout_map = {
            'gitleaks': 1800,
            'trufflehog': 2400
        }
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': tool,
                'repo_url': repo_url
            },
            'estimated_timeout': timeout_map.get(tool, 1800),
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
