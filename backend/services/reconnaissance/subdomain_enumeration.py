"""
Subdomain Enumeration Module
=============================

Módulo para enumeración de subdominios.
Herramientas: Subfinder, Amass, Assetfinder, Sublist3r, Findomain, crt.sh
"""

import subprocess
import json
import urllib.parse
import logging
import threading
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import CommandSanitizer, DomainValidator
from utils.workspace_logger import log_to_workspace
from .base import BaseReconnaissanceService

logger = logging.getLogger(__name__)


class SubdomainEnumerationService(BaseReconnaissanceService):
    """Servicio para enumeración de subdominios."""
    
    def start_subdomain_enum(
        self,
        domain: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'subfinder',
        passive_only: bool = True
    ) -> Dict[str, Any]:
        """
        Inicia enumeración de subdominios.
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            tool: Herramienta (subfinder, amass, assetfinder, sublist3r)
            passive_only: Solo técnicas pasivas
        
        Returns:
            Dict con información del escaneo
        """
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        # Verificar si amass puede ejecutarse (libpostal disponible)
        if tool == 'amass':
            if not self._check_amass_available():
                logger.warning(f"Amass no está disponible (libpostal no configurado), usando subfinder como alternativa")
                log_to_workspace(
                    workspace_id=workspace_id,
                    source='RECONNAISSANCE',
                    level='WARNING',
                    message=f"Amass no disponible (libpostal no configurado), usando subfinder",
                    metadata={'original_tool': 'amass', 'fallback_tool': 'subfinder', 'domain': domain}
                )
                tool = 'subfinder'  # Fallback automático a subfinder
        
        scan = self.scan_repo.create(
            scan_type='reconnaissance',
            target=domain,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': tool,
                'recon_type': 'subdomain_enum',
                'passive_only': passive_only,
                'original_tool': 'amass' if tool == 'subfinder' and 'amass' in str(locals().get('tool', '')) else None
            }
        )
        
        try:
            # Usar directorio del workspace en lugar de self.output_dir
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
            output_file = str(workspace_output_dir / f'{tool}_{scan.id}.txt')
            command = self._build_subdomain_command(tool, domain, output_file, passive_only)
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting subdomain enum {scan.id} with {tool}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'subdomain')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': tool,
                'target': domain,
                'passive_only': passive_only
            }
            
        except Exception as e:
            logger.error(f"Error starting subdomain enum: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def preview_subdomain_enum(
        self,
        domain: str,
        workspace_id: int,
        tool: str = 'subfinder',
        passive_only: bool = True
    ) -> Dict[str, Any]:
        """
        Preview del comando de enumeración de subdominios (sin ejecutar).
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            tool: Herramienta (subfinder, amass, assetfinder, sublist3r)
            passive_only: Solo técnicas pasivas
        
        Returns:
            Dict con información del comando que se ejecutaría
        """
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        # Simular output_file (no se crea realmente)
        # Usar un path genérico para preview (el real se generará al ejecutar)
        from utils.workspace_filesystem import get_workspace_output_dir
        # Para preview, usamos un nombre genérico ya que no tenemos el workspace cargado
        # El path real se generará cuando se ejecute con el scan_id
        output_file = f'/workspaces/workspace_{workspace_id}/recon/{tool}_{{scan_id}}.txt'
        
        command = self._build_subdomain_command(tool, domain, output_file, passive_only)
        command_str = ' '.join([str(c) for c in command])
        
        # Timeout estimado por herramienta
        timeout_map = {
            'subfinder': 300,
            'amass': 1800,
            'assetfinder': 300,
            'sublist3r': 600
        }
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': tool,
                'domain': domain,
                'passive_only': passive_only
            },
            'estimated_timeout': timeout_map.get(tool, 600),
            'output_file': output_file.replace('_PREVIEW.txt', f'_{{scan_id}}.txt'),
            'warnings': [],
            'suggestions': []
        }
    
    def _check_amass_available(self) -> bool:
        """
        Verifica si amass está disponible y puede ejecutarse.
        Amass requiere libpostal configurado, si no está disponible se queda colgado.
        
        Returns:
            True si amass puede ejecutarse, False si no
        """
        import subprocess
        import shutil
        
        # Verificar que amass existe
        amass_binary = '/usr/lib/amass/amass' if Path('/usr/lib/amass/amass').exists() else 'amass'
        if not shutil.which(amass_binary) and not Path('/usr/lib/amass/amass').exists():
            logger.warning("Amass binary not found")
            return False
        
        # Verificar que libpostal tiene datos descargados
        # Si no tiene datos, amass se quedará colgado
        libpostal_data_paths = [
            Path('/usr/share/libpostal'),
            Path('/usr/local/share/libpostal'),
            Path.home() / '.local/share/libpostal'
        ]
        
        libpostal_has_data = False
        for path in libpostal_data_paths:
            if path.exists():
                # Verificar si tiene archivos de datos (no solo el directorio vacío)
                data_files = list(path.glob('*'))
                if data_files and len(data_files) > 1:  # Más que solo un archivo de versión
                    libpostal_has_data = True
                    break
        
        if not libpostal_has_data:
            logger.warning("Libpostal data not downloaded - amass will hang. Use subfinder instead.")
            logger.info("To fix amass: sudo mkdir -p /usr/share/libpostal && sudo /usr/bin/libpostal_data download all /usr/share/libpostal")
            return False
        
        # Test rápido: intentar ejecutar amass con timeout muy corto
        # Si se queda colgado (por libpostal), no está disponible
        try:
            test_result = subprocess.run(
                [amass_binary, 'enum', '-d', 'test-invalid-domain-12345.example.com', '-passive'],
                capture_output=True,
                timeout=10,  # 10 segundos para detectar si se cuelga
                stdin=subprocess.DEVNULL,
                text=True
            )
            # Si termina (incluso con error), está disponible
            return True
        except subprocess.TimeoutExpired:
            # Si se queda colgado, no está disponible
            logger.warning("Amass hangs on startup (libpostal issue) - not available")
            return False
        except Exception as e:
            logger.warning(f"Error checking amass availability: {e}")
            # En caso de duda, asumir que no está disponible
            return False
    
    def _build_subdomain_command(
        self,
        tool: str,
        domain: str,
        output_file: str,
        passive_only: bool
    ) -> list:
        """Construye comando según herramienta."""
        if tool == 'subfinder':
            return [
                'subfinder', '-d', domain, '-all', '-recursive',
                '-o', output_file, '-silent'
            ]
        elif tool == 'amass':
            # Usar el binario directo para evitar el wrapper que requiere sudo
            amass_binary = '/usr/lib/amass/amass' if Path('/usr/lib/amass/amass').exists() else 'amass'
            cmd = [amass_binary, 'enum', '-d', domain, '-o', output_file]
            if passive_only:
                cmd.append('-passive')
            else:
                cmd.extend(['-brute', '-w', '/usr/share/wordlists/amass/subdomains.txt'])
            return cmd
        elif tool == 'assetfinder':
            return ['assetfinder', '--subs-only', domain]
        elif tool == 'sublist3r':
            cmd = ['sublist3r', '-d', domain, '-o', output_file]
            if not passive_only:
                cmd.append('-b')
            return cmd
        else:
            raise ValueError(f'Unsupported tool: {tool}')
    
    def start_findomain_enum(
        self,
        domain: str,
        workspace_id: int,
        user_id: int,
        resolvers_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enumeración de subdominios con Findomain.
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            resolvers_file: Archivo de resolvers DNS (opcional)
        
        Returns:
            Dict con información del escaneo
        """
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        scan = self.scan_repo.create(
            scan_type='reconnaissance',
            target=domain,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'findomain',
                'recon_type': 'subdomain_enum'
            }
        )
        
        try:
            # Usar directorio del workspace en lugar de self.output_dir
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
            output_file = str(workspace_output_dir / f'findomain_{scan.id}.txt')
            # Usar -u (unique-output) en lugar de -o para especificar exactamente dónde guardar
            command = ['findomain', '-t', domain, '-u', output_file]
            
            if resolvers_file:
                command.extend(['--resolvers', resolvers_file])
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            log_to_workspace(
                workspace_id=workspace_id,
                source='FINDOMAIN',
                level='INFO',
                message=f"Iniciando Findomain para {domain}",
                metadata={'scan_id': scan.id, 'domain': domain}
            )
            
            logger.info(f"Starting Findomain enum {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'findomain')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'findomain',
                'domain': domain
            }
            
        except Exception as e:
            logger.error(f"Error starting Findomain enum: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def start_crtsh_lookup(
        self,
        domain: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Busca subdominios usando Certificate Transparency (crt.sh).
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
        
        Returns:
            Dict con información del escaneo
        """
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        scan = self.scan_repo.create(
            scan_type='reconnaissance',
            target=domain,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'crtsh',
                'recon_type': 'subdomain_enum'
            }
        )
        
        try:
            # Usar directorio del workspace en lugar de self.output_dir
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
            output_file = str(workspace_output_dir / f'crtsh_{scan.id}.txt')
            encoded_domain = urllib.parse.quote(f'%.{domain}')
            url = f'https://crt.sh/?q={encoded_domain}&output=json'
            
            command = ['curl', '-s', url]
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            log_to_workspace(
                workspace_id=workspace_id,
                source='CRTSH',
                level='INFO',
                message=f"Iniciando búsqueda Certificate Transparency para {domain}",
                metadata={'scan_id': scan.id, 'domain': domain}
            )
            
            logger.info(f"Starting crt.sh lookup {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_crtsh_scan,
                args=(scan.id, sanitized_cmd, output_file, domain, workspace_id)
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'crtsh',
                'domain': domain
            }
            
        except Exception as e:
            logger.error(f"Error starting crt.sh lookup: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def _execute_crtsh_scan(
        self,
        scan_id: int,
        command: list,
        output_file: str,
        domain: str,
        workspace_id: int
    ) -> None:
        """Ejecuta scan de crt.sh y parsea JSON."""
        from celery_app import get_flask_app
        
        app = get_flask_app()
        
        with app.app_context():
            try:
                scan = self.scan_repo.find_by_id(scan_id)
                
                # Actualizar progreso al inicio
                self.scan_repo.update_progress(scan, 25, "Consultando crt.sh...")
                
                if workspace_id:
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source='CRTSH',
                        level='INFO',
                        message=f"Consultando Certificate Transparency para {domain}",
                        metadata={'scan_id': scan_id, 'progress': 25}
                    )
                
                # Actualizar progreso antes de ejecutar
                self.scan_repo.update_progress(scan, 50, "Ejecutando consulta a crt.sh...")
                
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    env=CommandSanitizer.get_safe_env()
                )
                
                # Actualizar progreso después de obtener respuesta
                scan = self.scan_repo.find_by_id(scan_id)
                self.scan_repo.update_progress(scan, 75, "Procesando resultados de crt.sh...")
                
                if result.returncode == 0:
                    try:
                        data = json.loads(result.stdout)
                        subdomains = set()
                        for entry in data:
                            if 'name_value' in entry:
                                names = entry['name_value'].split('\n')
                                for name in names:
                                    name = name.strip()
                                    if name and domain in name:
                                        subdomains.add(name)
                        
                        with open(output_file, 'w') as f:
                            for subdomain in sorted(subdomains):
                                f.write(f"{subdomain}\n")
                        
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source='CRTSH',
                            level='INFO',
                            message=f"crt.sh completado: {len(subdomains)} subdominios encontrados",
                            metadata={'scan_id': scan_id, 'subdomains_count': len(subdomains)}
                        )
                        
                        scan = self.scan_repo.find_by_id(scan_id)
                        self.scan_repo.update_progress(scan, 100, f"crt.sh completado: {len(subdomains)} subdominios encontrados")
                        self.scan_repo.update_status(scan, 'completed')
                        logger.info(f"crt.sh scan {scan_id} completed")
                        
                    except json.JSONDecodeError:
                        with open(output_file, 'w') as f:
                            f.write(result.stdout)
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source='CRTSH',
                            level='WARNING',
                            message="crt.sh: respuesta no es JSON válido, guardando raw output",
                            metadata={'scan_id': scan_id}
                        )
                        
                        scan = self.scan_repo.find_by_id(scan_id)
                        self.scan_repo.update_progress(scan, 100, "crt.sh completado (respuesta no JSON)")
                        self.scan_repo.update_status(scan, 'completed')
                        logger.info(f"crt.sh scan {scan_id} completed (non-JSON response)")
                else:
                    error_msg = result.stderr or "Unknown error"
                    scan = self.scan_repo.find_by_id(scan_id)
                    self.scan_repo.update_progress(scan, 0, f"crt.sh falló: {error_msg}")
                    self.scan_repo.update_status(scan, 'failed', error_msg)
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source='CRTSH',
                        level='ERROR',
                        message=f"crt.sh falló: {error_msg}",
                        metadata={'scan_id': scan_id, 'error': error_msg}
                    )
                    logger.error(f"crt.sh scan {scan_id} failed: {error_msg}")
                    
            except Exception as e:
                scan = self.scan_repo.find_by_id(scan_id)
                self.scan_repo.update_progress(scan, 0, f"Error en crt.sh: {str(e)}")
                self.scan_repo.update_status(scan, 'failed', str(e))
                log_to_workspace(
                    workspace_id=workspace_id,
                    source='CRTSH',
                    level='ERROR',
                    message=f"Error en crt.sh: {str(e)}",
                    metadata={'scan_id': scan_id, 'error': str(e)}
                )
                logger.error(f"crt.sh scan {scan_id} error: {e}", exc_info=True)
    
    def preview_findomain_enum(
        self,
        domain: str,
        workspace_id: int,
        resolvers_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando Findomain (sin ejecutar)."""
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        output_file = f'/workspaces/workspace_{workspace_id}/recon/findomain_{{scan_id}}.txt'
        command = ['findomain', '-t', domain, '-u', output_file]
        
        if resolvers_file:
            command.extend(['--resolvers', resolvers_file])
        
        command_str = ' '.join([str(c) for c in command])
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'findomain',
                'domain': domain,
                'resolvers_file': resolvers_file
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_crtsh_lookup(
        self,
        domain: str,
        workspace_id: int
    ) -> Dict[str, Any]:
        """Preview del comando crt.sh (sin ejecutar)."""
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        output_file = f'/workspaces/workspace_{workspace_id}/recon/crtsh_{{scan_id}}.txt'
        encoded_domain = urllib.parse.quote(f'%.{domain}')
        url = f'https://crt.sh/?q={encoded_domain}&output=json'
        command = ['curl', '-s', url]
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'crtsh',
                'domain': domain
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }


