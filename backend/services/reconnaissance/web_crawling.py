"""
Web Crawling Module
===================

Módulo para crawling web y descubrimiento de URLs.
Herramientas: Katana, GoSpider, Hakrawler
"""

import logging
import threading
from typing import Dict, Any

from utils.validators import CommandSanitizer, DomainValidator
from .base import BaseReconnaissanceService

logger = logging.getLogger(__name__)


class WebCrawlingService(BaseReconnaissanceService):
    """Servicio para crawling web."""
    
    def start_web_crawl(
        self,
        url: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'katana',
        depth: int = 3,
        scope: str = 'same-domain'
    ) -> Dict[str, Any]:
        """
        Inicia crawling web.
        
        Args:
            url: URL objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            tool: Herramienta (katana, gospider, hakrawler)
            depth: Profundidad del crawl
            scope: Alcance (same-domain, subdomain, all)
        """
        if not DomainValidator.validate_url(url):
            raise ValueError(f'Invalid URL: {url}')
        
        scan = self.scan_repo.create(
            scan_type='reconnaissance',
            target=url,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': tool,
                'recon_type': 'web_crawl',
                'depth': depth,
                'scope': scope
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
            output_file = str(workspace_output_dir / f'{tool}_{scan.id}.txt')
            command = self._build_crawl_command(tool, url, depth, scope, output_file)
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting web crawl {scan.id} with {tool}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'crawl')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': tool,
                'target': url,
                'depth': depth
            }
            
        except Exception as e:
            logger.error(f"Error starting web crawl: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def _build_crawl_command(
        self,
        tool: str,
        url: str,
        depth: int,
        scope: str,
        output_file: str
    ) -> list:
        """Construye comando de crawling según herramienta."""
        if tool == 'katana':
            cmd = [
                'katana', '-u', url, '-d', str(depth),
                '-jc', '-kf', 'all', '-o', output_file
            ]
            # Katana usa -fs (field-scope) para limitar el scope
            # rdn = root domain name (mismo dominio), fqdn = fully qualified domain name
            if scope == 'same-domain':
                cmd.extend(['-fs', 'rdn'])  # Limitar al mismo dominio raíz
            elif scope == 'subdomain':
                cmd.extend(['-fs', 'fqdn'])  # Incluir subdominios
            # 'all' no necesita flag adicional, katana por defecto puede crawlear todo
            return cmd
        elif tool == 'gospider':
            return [
                'gospider', '-s', url, '-d', str(depth),
                '-c', '10', '-o', str(self.output_dir)
            ]
        elif tool == 'hakrawler':
            # hakrawler: -url para URL, -depth para profundidad, -plain para output simple
            # Alternativa: hakrawler -d <depth> -u (lee URL de stdin, pero no podemos usar pipes)
            return ['hakrawler', '-url', url, '-depth', str(depth), '-plain']
        else:
            raise ValueError(f'Unsupported tool: {tool}')
    
    def preview_web_crawl(
        self,
        url: str,
        workspace_id: int,
        tool: str = 'katana',
        depth: int = 3,
        scope: str = 'same-domain'
    ) -> Dict[str, Any]:
        """Preview del comando de web crawling."""
        # Agregar protocolo si no lo tiene
        original_url = url
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
            logger.info(f"Web Crawl Preview: Agregado protocolo HTTPS a URL: {original_url} -> {url}")
        
        if not DomainValidator.validate_url(url):
            # Si HTTPS falla, intentar HTTP
            if url.startswith('https://'):
                url = url.replace('https://', 'http://')
                logger.info(f"Web Crawl Preview: Cambiado a HTTP: {url}")
            if not DomainValidator.validate_url(url):
                logger.error(f"Web Crawl Preview: URL inválida después de agregar protocolo: {url} (original: {original_url})")
                raise ValueError(f'Invalid URL: {original_url}. Intenté agregar protocolo pero sigue siendo inválido.')
        
        output_file = f'/workspaces/workspace_{workspace_id}/recon/{tool}_{{scan_id}}.txt'
        command = self._build_crawl_command(tool, url, depth, scope, output_file)
        command_str = ' '.join([str(c) for c in command])
        
        timeout_map = {
            'katana': 1800,
            'gospider': 1200,
            'hakrawler': 600
        }
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': tool,
                'url': url,
                'depth': depth,
                'scope': scope
            },
            'estimated_timeout': timeout_map.get(tool, 1200),
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
