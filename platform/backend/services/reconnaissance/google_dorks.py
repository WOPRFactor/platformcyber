"""
Google Dorks Module
===================

Módulo para búsqueda con Google Dorks.
Herramientas: Manual, GooFuzz, Pagodo, dorkScanner
"""

import subprocess
import logging
import threading
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import DomainValidator, CommandSanitizer
from utils.workspace_logger import log_to_workspace
from .base import BaseReconnaissanceService

logger = logging.getLogger(__name__)


class GoogleDorksService(BaseReconnaissanceService):
    """Servicio para Google Dorks."""
    
    def start_google_dorks(
        self,
        domain: str,
        workspace_id: int,
        user_id: int,
        dork_query: Optional[str] = None,
        tool: str = 'manual'
    ) -> Dict[str, Any]:
        """
        Ejecuta Google Dorks manuales o automatizados.
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            dork_query: Query de dork personalizado (para modo manual)
            tool: 'manual' | 'goofuzz' | 'pagodo' | 'dorkscanner'
        
        Returns:
            Dict con información del escaneo iniciado
        """
        DomainValidator.validate(domain)
        CommandSanitizer.validate_target(domain)
        
        scan = self.scan_repo.create_scan(
            scan_type='google_dorks',
            target=domain,
            workspace_id=workspace_id,
            user_id=user_id,
            status='running'
        )
        
        workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
        output_file = workspace_output_dir / f"google_dorks_{scan.id}.txt"
        
        try:
            def execute_scan():
                try:
                    if tool == 'manual':
                        query = dork_query or f"site:{domain}"
                        
                        with open(output_file, 'w') as f:
                            f.write(f"Google Dork Query: {query}\n")
                            f.write(f"Domain: {domain}\n")
                            f.write(f"Tool: {tool}\n\n")
                            f.write("NOTA: Este es un dork manual. Ejecuta la búsqueda en Google:\n")
                            f.write(f"https://www.google.com/search?q={query.replace(' ', '+')}\n")
                        
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source='reconnaissance',
                            level='info',
                            message=f"Google Dork manual generado: {query}",
                            task_id=None
                        )
                        
                    elif tool == 'goofuzz':
                        extensions = ['pdf', 'doc', 'xls', 'sql', 'log', 'env']
                        cmd = ['goofuzz', '-t', domain, '-e', ','.join(extensions)]
                        
                        with open(output_file, 'w') as f:
                            result = subprocess.run(
                                cmd,
                                capture_output=True,
                                text=True,
                                timeout=300
                            )
                            f.write(result.stdout)
                            if result.stderr:
                                f.write(f"\n\nSTDERR:\n{result.stderr}")
                        
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source='reconnaissance',
                            level='info',
                            message=f"GooFuzz completado para {domain}",
                            task_id=None
                        )
                        
                    elif tool == 'pagodo':
                        from utils.workspace_filesystem import PROJECT_TMP_DIR
                        dorks_file = PROJECT_TMP_DIR / 'pagodo_dorks.txt'
                        if not dorks_file.exists():
                            default_dorks = [
                                f"site:{domain} filetype:pdf",
                                f"site:{domain} filetype:doc",
                                f"site:{domain} filetype:xls",
                                f"site:{domain} inurl:admin",
                                f"site:{domain} inurl:login",
                                f"site:{domain} 'password'"
                            ]
                            with open(dorks_file, 'w') as f:
                                f.write('\n'.join(default_dorks))
                        
                        cmd = ['pagodo', '-d', domain, '-g', str(dorks_file)]
                        
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
                            message=f"Pagodo completado para {domain}",
                            task_id=None
                        )
                        
                    elif tool == 'dorkscanner':
                        cmd = ['python3', 'dorkScanner.py', '-d', domain]
                        
                        with open(output_file, 'w') as f:
                            result = subprocess.run(
                                cmd,
                                capture_output=True,
                                text=True,
                                timeout=600,
                                cwd=str(PROJECT_TMP_DIR)
                            )
                            f.write(result.stdout)
                            if result.stderr:
                                f.write(f"\n\nSTDERR:\n{result.stderr}")
                        
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source='reconnaissance',
                            level='info',
                            message=f"dorkScanner completado para {domain}",
                            task_id=None
                        )
                    
                    self.scan_repo.update_status(scan, 'completed')
                    
                except subprocess.TimeoutExpired:
                    logger.error(f"Google Dorks timeout for {domain}")
                    self.scan_repo.update_status(scan, 'failed', 'Timeout')
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source='reconnaissance',
                        level='error',
                        message=f"Google Dorks timeout para {domain}",
                        task_id=None
                    )
                except Exception as e:
                    logger.error(f"Error in Google Dorks scan: {e}")
                    self.scan_repo.update_status(scan, 'failed', str(e))
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source='reconnaissance',
                        level='error',
                        message=f"Error en Google Dorks: {str(e)}",
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
            logger.error(f"Error starting Google Dorks: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def preview_google_dorks(
        self,
        domain: str,
        workspace_id: int,
        dork_query: Optional[str] = None,
        tool: str = 'manual'
    ) -> Dict[str, Any]:
        """Preview del comando Google Dorks."""
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        output_file = f'/workspaces/workspace_{workspace_id}/recon/google_dorks_{{scan_id}}.txt'
        
        if tool == 'manual':
            query = dork_query or f"site:{domain}"
            command_str = f"Google Dork Query: {query}\nURL: https://www.google.com/search?q={query.replace(' ', '+')}"
            command = ['echo', command_str]
        elif tool == 'goofuzz':
            command = ['goofuzz', '-t', domain, '-e', 'pdf,doc,xls,sql,log,env']
        elif tool == 'pagodo':
            from utils.workspace_filesystem import PROJECT_TMP_DIR
            command = ['pagodo', '-d', domain, '-g', str(PROJECT_TMP_DIR / 'pagodo_dorks.txt')]
        elif tool == 'dorkscanner':
            command = ['python3', 'dorkScanner.py', '-d', domain]
        else:
            raise ValueError(f'Unsupported tool: {tool}')
        
        command_str = ' '.join([str(c) for c in command])
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': tool,
                'domain': domain,
                'dork_query': dork_query
            },
            'estimated_timeout': 600 if tool == 'manual' else 1800,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
