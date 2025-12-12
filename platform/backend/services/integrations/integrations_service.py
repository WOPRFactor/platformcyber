"""
Integrations Service
====================

Servicio principal para integraciones avanzadas.
"""

import logging
import subprocess
import shutil
from typing import Dict, Any, List, Optional
from pathlib import Path

from repositories import ScanRepository
from utils.validators import CommandSanitizer, DomainValidator
from utils.workspace_logger import log_to_workspace
from .base import BaseIntegrationService
from .executors.scan_executor import IntegrationScanExecutor

logger = logging.getLogger(__name__)


class IntegrationsService(BaseIntegrationService):
    """Servicio para integraciones avanzadas."""

    def __init__(self, scan_repository: ScanRepository = None):
        super().__init__(scan_repository)
        self.executor = IntegrationScanExecutor(self.scan_repo)

    # ============================================================================
    # METASPLOIT
    # ============================================================================

    def check_metasploit_status(self) -> Dict[str, Any]:
        """Verifica el estado de Metasploit."""
        try:
            # Verificar si msfconsole está disponible
            msfconsole_path = shutil.which('msfconsole')
            if not msfconsole_path:
                return {
                    'connected': False,
                    'error': 'Metasploit Framework not found. Install with: apt install metasploit-framework'
                }
            
            # Intentar verificar versión
            try:
                result = subprocess.run(
                    ['msfconsole', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                version = result.stdout.strip() if result.returncode == 0 else None
                
                return {
                    'connected': True,
                    'version': version or 'Unknown',
                    'path': msfconsole_path
                }
            except subprocess.TimeoutExpired:
                return {
                    'connected': False,
                    'error': 'Metasploit timeout - may be starting up'
                }
            except Exception as e:
                return {
                    'connected': False,
                    'error': f'Error checking Metasploit: {str(e)}'
                }
        except Exception as e:
            logger.error(f"Error checking Metasploit status: {e}")
            return {
                'connected': False,
                'error': str(e)
            }

    def list_metasploit_modules(self, module_type: Optional[str] = None) -> Dict[str, Any]:
        """Lista módulos de Metasploit."""
        try:
            if not shutil.which('msfconsole'):
                return {
                    'modules': [],
                    'error': 'Metasploit Framework not found'
                }
            
            # Construir comando para listar módulos
            if module_type:
                cmd = f"msfconsole -q -x 'search type:{module_type}; exit'"
            else:
                cmd = "msfconsole -q -x 'search; exit'"
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            modules = []
            if result.returncode == 0:
                # Parsear output básico
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('[-]') and not line.startswith('[*]'):
                        modules.append(line.strip())
            
            return {
                'modules': modules[:100],  # Limitar a 100
                'type': module_type,
                'total': len(modules)
            }
        except Exception as e:
            logger.error(f"Error listing Metasploit modules: {e}")
            return {
                'modules': [],
                'error': str(e)
            }

    def execute_metasploit_exploit(
        self,
        exploit: str,
        options: Dict[str, Any],
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Ejecuta un exploit de Metasploit."""
        try:
            scan = self.scan_repo.create(
                scan_type='integrations',
                target=options.get('RHOSTS', 'unknown'),
                workspace_id=workspace_id,
                user_id=user_id,
                options={
                    'tool': 'metasploit',
                    'exploit': exploit,
                    'options': options
                }
            )

            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'metasploit_{scan.id}.txt'

            # Construir script de Metasploit
            script_content = f"use {exploit}\n"
            for key, value in options.items():
                script_content += f"set {key} {value}\n"
            script_content += "run\n"
            script_content += "exit\n"

            script_file = workspace_output_dir / f'msf_script_{scan.id}.rc'
            with open(script_file, 'w') as f:
                f.write(script_content)

            command = [
                'msfconsole',
                '-q',
                '-r', str(script_file)
            ]

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            log_to_workspace(
                workspace_id=workspace_id,
                source='METASPLOIT',
                level='INFO',
                message=f"Iniciando exploit: {exploit}",
                metadata={'scan_id': scan.id, 'exploit': exploit}
            )

            self.executor.execute_scan_in_thread(scan.id, sanitized_cmd, output_file, 'metasploit', 3600)
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'exploit': exploit
            }
        except Exception as e:
            logger.error(f"Error executing Metasploit exploit: {e}")
            raise

    def get_metasploit_sessions(self) -> Dict[str, Any]:
        """Lista sesiones activas de Metasploit."""
        try:
            if not shutil.which('msfconsole'):
                return {'sessions': []}
            
            # Verificar sesiones con msfrpcd o directamente
            # Por ahora retornamos placeholder
            return {
                'sessions': [],
                'message': 'Session listing requires msfrpcd or direct console access'
            }
        except Exception as e:
            logger.error(f"Error getting Metasploit sessions: {e}")
            return {'sessions': [], 'error': str(e)}

    # ============================================================================
    # BURP SUITE
    # ============================================================================

    def check_burp_status(self) -> Dict[str, Any]:
        """Verifica el estado de Burp Suite."""
        try:
            # Verificar si burpsuite está disponible
            burp_path = shutil.which('burpsuite') or shutil.which('burpsuite_pro')
            if not burp_path:
                return {
                    'connected': False,
                    'error': 'Burp Suite not found. Install Burp Suite Professional.'
                }
            
            return {
                'connected': True,
                'path': burp_path,
                'message': 'Burp Suite found. API integration requires configuration.'
            }
        except Exception as e:
            logger.error(f"Error checking Burp status: {e}")
            return {
                'connected': False,
                'error': str(e)
            }

    def start_burp_scan(
        self,
        url: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Inicia un scan de Burp Suite."""
        try:
            DomainValidator.validate_url(url)
            
            scan = self.scan_repo.create(
                scan_type='integrations',
                target=url,
                workspace_id=workspace_id,
                user_id=user_id,
                options={
                    'tool': 'burp',
                    'url': url
                }
            )

            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'burp_scan_{scan.id}.json'

            # Burp Suite requiere API REST o extensión
            # Por ahora, placeholder para implementación futura
            log_to_workspace(
                workspace_id=workspace_id,
                source='BURP',
                level='INFO',
                message=f"Iniciando scan de Burp Suite para: {url}",
                metadata={'scan_id': scan.id, 'url': url}
            )

            return {
                'scan_id': scan.id,
                'status': 'pending',
                'message': 'Burp Suite scan requires API configuration',
                'url': url
            }
        except Exception as e:
            logger.error(f"Error starting Burp scan: {e}")
            raise

    # ============================================================================
    # NMAP ADVANCED
    # ============================================================================

    def advanced_nmap_scan(
        self,
        target: str,
        options: Dict[str, Any],
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Ejecuta un scan avanzado de Nmap."""
        try:
            scan = self.scan_repo.create(
                scan_type='integrations',
                target=target,
                workspace_id=workspace_id,
                user_id=user_id,
                options={
                    'tool': 'nmap',
                    'options': options
                }
            )

            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'nmap_advanced_{scan.id}.xml'

            # Construir comando Nmap
            command = ['nmap']
            
            # Mapear tipos de scan predefinidos
            scan_type = options.get('scan_type', 'comprehensive')
            scan_type_map = {
                'quick': ['-T4', '-F'],
                'service': ['-sV', '-T4'],
                'vulnerability': ['--script', 'vuln', '-T4'],
                'os_detection': ['-O', '-T4'],
                'comprehensive': ['-A', '-T4'],
                'stealth': ['-sS', '-T3'],
                'aggressive': ['-A', '-T4']
            }
            
            if scan_type in scan_type_map:
                command.extend(scan_type_map[scan_type])
            else:
                # Si no está en el mapa, usar como está
                if options.get('scan_type'):
                    command.extend(['-s' + options['scan_type']])
            
            # Agregar opciones adicionales
            if options.get('ports'):
                command.extend(['-p', options['ports']])
            if options.get('scripts'):
                command.extend(['--script', options['scripts']])
            if options.get('aggressive') and scan_type != 'aggressive':
                command.append('-A')
            if options.get('version_detection') and scan_type != 'service':
                command.append('-sV')
            if options.get('os_detection') and scan_type != 'os_detection':
                command.append('-O')
            
            command.extend(['-oX', str(output_file)])
            command.append(target)

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            log_to_workspace(
                workspace_id=workspace_id,
                source='NMAP',
                level='INFO',
                message=f"Iniciando scan avanzado de Nmap: {target}",
                metadata={'scan_id': scan.id, 'target': target}
            )

            self.executor.execute_scan_in_thread(scan.id, sanitized_cmd, output_file, 'nmap', 1800)
            self.scan_repo.update_status(scan, 'running')

            return {
                'session_id': scan.id,
                'status': 'running',
                'target': target
            }
        except Exception as e:
            logger.error(f"Error executing advanced Nmap scan: {e}")
            raise

    def get_nmap_results(self, session_id: int) -> Dict[str, Any]:
        """Obtiene resultados de un scan de Nmap."""
        try:
            scan = self.scan_repo.find_by_id(session_id)
            if not scan:
                raise ValueError(f'Scan {session_id} not found')
            
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'nmap_advanced_{session_id}.xml'
            
            if not output_file.exists():
                return {
                    'session_id': session_id,
                    'status': scan.status,
                    'message': 'Results not available yet'
                }
            
            # Leer y parsear XML básico
            with open(output_file, 'r') as f:
                xml_content = f.read()
            
            return {
                'session_id': session_id,
                'status': scan.status,
                'results': {
                    'xml': xml_content,
                    'file': str(output_file)
                }
            }
        except Exception as e:
            logger.error(f"Error getting Nmap results: {e}")
            raise

    # ============================================================================
    # SQLMAP
    # ============================================================================

    def sqlmap_scan(
        self,
        url: str,
        options: Dict[str, Any],
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Ejecuta un scan de SQLMap."""
        try:
            DomainValidator.validate_url(url)
            
            scan = self.scan_repo.create(
                scan_type='integrations',
                target=url,
                workspace_id=workspace_id,
                user_id=user_id,
                options={
                    'tool': 'sqlmap',
                    'url': url,
                    'options': options
                }
            )

            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'sqlmap_{scan.id}.txt'

            command = ['sqlmap', '-u', url]
            
            # Agregar opciones
            if options.get('data'):
                command.extend(['--data', options['data']])
            if options.get('cookie'):
                command.extend(['--cookie', options['cookie']])
            if options.get('level'):
                command.extend(['--level', str(options['level'])])
            if options.get('risk'):
                command.extend(['--risk', str(options['risk'])])
            if options.get('batch'):
                command.append('--batch')
            if options.get('dump'):
                command.append('--dump')
            
            command.extend(['--output-dir', str(workspace_output_dir)])

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            log_to_workspace(
                workspace_id=workspace_id,
                source='SQLMAP',
                level='INFO',
                message=f"Iniciando scan de SQLMap: {url}",
                metadata={'scan_id': scan.id, 'url': url}
            )

            self.executor.execute_scan_in_thread(scan.id, sanitized_cmd, output_file, 'sqlmap', 3600)
            self.scan_repo.update_status(scan, 'running')

            return {
                'session_id': scan.id,
                'status': 'running',
                'url': url
            }
        except Exception as e:
            logger.error(f"Error executing SQLMap scan: {e}")
            raise

    def get_sqlmap_results(self, session_id: int) -> Dict[str, Any]:
        """Obtiene resultados de un scan de SQLMap."""
        try:
            scan = self.scan_repo.find_by_id(session_id)
            if not scan:
                raise ValueError(f'Scan {session_id} not found')
            
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            
            # SQLMap guarda resultados en subdirectorios
            results = {}
            if workspace_output_dir.exists():
                for item in workspace_output_dir.iterdir():
                    if item.is_dir() and item.name.startswith('sqlmap'):
                        results[item.name] = str(item)
            
            return {
                'session_id': session_id,
                'status': scan.status,
                'results': results
            }
        except Exception as e:
            logger.error(f"Error getting SQLMap results: {e}")
            raise

    # ============================================================================
    # GOBUSTER
    # ============================================================================

    def gobuster_directory(
        self,
        url: str,
        wordlist: str,
        options: Dict[str, Any],
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Ejecuta directory busting con Gobuster."""
        try:
            DomainValidator.validate_url(url)
            
            scan = self.scan_repo.create(
                scan_type='integrations',
                target=url,
                workspace_id=workspace_id,
                user_id=user_id,
                options={
                    'tool': 'gobuster',
                    'url': url,
                    'wordlist': wordlist
                }
            )

            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'gobuster_{scan.id}.txt'

            command = ['gobuster', 'dir', '-u', url, '-w', wordlist]
            
            # Agregar opciones
            if options.get('extensions'):
                command.extend(['-x', options['extensions']])
            if options.get('status_codes'):
                command.extend(['-s', options['status_codes']])
            if options.get('threads'):
                command.extend(['-t', str(options['threads'])])
            
            command.extend(['-o', str(output_file)])

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            log_to_workspace(
                workspace_id=workspace_id,
                source='GOBUSTER',
                level='INFO',
                message=f"Iniciando directory busting: {url}",
                metadata={'scan_id': scan.id, 'url': url, 'wordlist': wordlist}
            )

            self.executor.execute_scan_in_thread(scan.id, sanitized_cmd, output_file, 'gobuster', 1800)
            self.scan_repo.update_status(scan, 'running')

            return {
                'session_id': scan.id,
                'status': 'running',
                'url': url
            }
        except Exception as e:
            logger.error(f"Error executing Gobuster: {e}")
            raise

    def get_gobuster_results(self, session_id: int) -> Dict[str, Any]:
        """Obtiene resultados de Gobuster."""
        try:
            scan = self.scan_repo.find_by_id(session_id)
            if not scan:
                raise ValueError(f'Scan {session_id} not found')
            
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'gobuster_{session_id}.txt'
            
            if not output_file.exists():
                return {
                    'session_id': session_id,
                    'status': scan.status,
                    'message': 'Results not available yet'
                }
            
            with open(output_file, 'r') as f:
                results = f.read()
            
            return {
                'session_id': session_id,
                'status': scan.status,
                'results': results
            }
        except Exception as e:
            logger.error(f"Error getting Gobuster results: {e}")
            raise

    # ============================================================================
    # SESSIONS
    # ============================================================================

    def get_integration_sessions(self, workspace_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Lista todas las sesiones de integraciones."""
        try:
            if workspace_id:
                scans = self.scan_repo.find_by_workspace(workspace_id, scan_type='integrations')
            else:
                # Si no hay workspace_id, obtener todos los scans de integraciones
                from models import Scan
                scans = Scan.query.filter_by(scan_type='integrations')\
                    .order_by(Scan.created_at.desc())\
                    .limit(100)\
                    .all()
            
            sessions = []
            for scan in scans:
                sessions.append({
                    'session_id': scan.id,
                    'tool': scan.options.get('tool', 'unknown') if scan.options else 'unknown',
                    'target': scan.target,
                    'status': scan.status,
                    'started_at': scan.started_at.isoformat() if scan.started_at else None,
                    'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
                })
            
            return sessions
        except Exception as e:
            logger.error(f"Error listing integration sessions: {e}")
            return []

    def get_session_details(self, session_id: int) -> Dict[str, Any]:
        """Obtiene detalles de una sesión de integración."""
        try:
            scan = self.scan_repo.find_by_id(session_id)
            if not scan:
                raise ValueError(f'Session {session_id} not found')
            
            return {
                'session_id': session_id,
                'tool': scan.options.get('tool', 'unknown') if scan.options else 'unknown',
                'target': scan.target,
                'status': scan.status,
                'options': scan.options,
                'started_at': scan.started_at.isoformat() if scan.started_at else None,
                'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
                'progress': scan.progress,
                'error': scan.error
            }
        except Exception as e:
            logger.error(f"Error getting session details: {e}")
            raise

    # ============================================================================
    # PREVIEW METHODS
    # ============================================================================

    def preview_metasploit_exploit(
        self,
        exploit: str,
        options: Dict[str, Any],
        workspace_id: int
    ) -> Dict[str, Any]:
        """Preview del comando Metasploit."""
        script_content = f"use {exploit}\n"
        for key, value in options.items():
            script_content += f"set {key} {value}\n"
        script_content += "run\n"
        script_content += "exit\n"

        command = [
            'msfconsole',
            '-q',
            '-r', f'/workspaces/workspace_{workspace_id}/integrations/msf_script_{{scan_id}}.rc'
        ]

        command_str = ' '.join(command)

        return {
            'command': command,
            'command_string': command_str,
            'script_content': script_content,
            'parameters': {
                'exploit': exploit,
                'options': options
            },
            'estimated_timeout': 3600,
            'output_file': f'/workspaces/workspace_{workspace_id}/integrations/metasploit_{{scan_id}}.txt',
            'warnings': [
                'Este exploit requiere configuración previa de Metasploit',
                'Asegúrate de tener las credenciales y permisos necesarios'
            ],
            'suggestions': [
                'Verifica que el exploit esté disponible: msfconsole -q -x "search {exploit}"',
                'Revisa los parámetros requeridos del exploit antes de ejecutar'
            ]
        }

    def preview_burp_scan(
        self,
        url: str,
        workspace_id: int
    ) -> Dict[str, Any]:
        """Preview del comando Burp Suite."""
        return {
            'command': ['burpsuite', '--scan', url],
            'command_string': f'burpsuite --scan {url}',
            'parameters': {
                'url': url
            },
            'estimated_timeout': 7200,
            'output_file': f'/workspaces/workspace_{workspace_id}/integrations/burp_scan_{{scan_id}}.json',
            'warnings': [
                'Burp Suite requiere configuración de API REST',
                'Asegúrate de tener Burp Suite Professional instalado y configurado'
            ],
            'suggestions': [
                'Configura la API REST de Burp Suite antes de ejecutar',
                'Verifica la conexión con: burpsuite --status'
            ]
        }

    def preview_nmap_scan(
        self,
        target: str,
        options: Dict[str, Any],
        workspace_id: int
    ) -> Dict[str, Any]:
        """Preview del comando Nmap avanzado."""
        command = ['nmap']
        
        # Mapear tipos de scan predefinidos
        scan_type = options.get('scan_type', 'comprehensive')
        scan_type_map = {
            'quick': ['-T4', '-F'],
            'service': ['-sV', '-T4'],
            'vulnerability': ['--script', 'vuln', '-T4'],
            'os_detection': ['-O', '-T4'],
            'comprehensive': ['-A', '-T4'],
            'stealth': ['-sS', '-T3'],
            'aggressive': ['-A', '-T4']
        }
        
        if scan_type in scan_type_map:
            command.extend(scan_type_map[scan_type])
        elif options.get('scan_type'):
            command.extend(['-s' + options['scan_type']])
        
        # Agregar opciones adicionales
        if options.get('ports'):
            command.extend(['-p', options['ports']])
        if options.get('scripts'):
            command.extend(['--script', options['scripts']])
        if options.get('aggressive') and scan_type != 'aggressive':
            command.append('-A')
        if options.get('version_detection') and scan_type != 'service':
            command.append('-sV')
        if options.get('os_detection') and scan_type != 'os_detection':
            command.append('-O')
        
        command.extend(['-oX', f'/workspaces/workspace_{workspace_id}/integrations/nmap_advanced_{{scan_id}}.xml'])
        command.append(target)

        command_str = ' '.join(command)

        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'target': target,
                'scan_type': scan_type,
                'options': options
            },
            'estimated_timeout': 1800,
            'output_file': f'/workspaces/workspace_{workspace_id}/integrations/nmap_advanced_{{scan_id}}.xml',
            'warnings': [],
            'suggestions': [
                'Asegúrate de tener permisos para ejecutar scans de red',
                'Los scans agresivos pueden ser detectados por sistemas de seguridad'
            ]
        }

    def preview_sqlmap_scan(
        self,
        url: str,
        options: Dict[str, Any],
        workspace_id: int
    ) -> Dict[str, Any]:
        """Preview del comando SQLMap."""
        command = ['sqlmap', '-u', url]
        
        if options.get('data'):
            command.extend(['--data', options['data']])
        if options.get('cookie'):
            command.extend(['--cookie', options['cookie']])
        if options.get('level'):
            command.extend(['--level', str(options['level'])])
        if options.get('risk'):
            command.extend(['--risk', str(options['risk'])])
        if options.get('batch'):
            command.append('--batch')
        if options.get('dump'):
            command.append('--dump')
        
        command.extend(['--output-dir', f'/workspaces/workspace_{workspace_id}/integrations'])

        command_str = ' '.join(command)

        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'url': url,
                'options': options
            },
            'estimated_timeout': 3600,
            'output_file': f'/workspaces/workspace_{workspace_id}/integrations/sqlmap_{{scan_id}}.txt',
            'warnings': [
                'SQLMap puede ser detectado por WAFs y sistemas de seguridad',
                'Usa con precaución en entornos de producción'
            ],
            'suggestions': [
                'Considera usar --batch para modo no interactivo',
                'Ajusta --level y --risk según la profundidad del scan deseada'
            ]
        }

    def preview_gobuster_directory(
        self,
        url: str,
        wordlist: str,
        options: Dict[str, Any],
        workspace_id: int
    ) -> Dict[str, Any]:
        """Preview del comando Gobuster."""
        command = ['gobuster', 'dir', '-u', url, '-w', wordlist]
        
        if options.get('extensions'):
            command.extend(['-x', options['extensions']])
        if options.get('status_codes'):
            command.extend(['-s', options['status_codes']])
        if options.get('threads'):
            command.extend(['-t', str(options['threads'])])
        
        command.extend(['-o', f'/workspaces/workspace_{workspace_id}/integrations/gobuster_{{scan_id}}.txt'])

        command_str = ' '.join(command)

        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'url': url,
                'wordlist': wordlist,
                'options': options
            },
            'estimated_timeout': 1800,
            'output_file': f'/workspaces/workspace_{workspace_id}/integrations/gobuster_{{scan_id}}.txt',
            'warnings': [
                'Directory busting puede generar mucho tráfico',
                'Asegúrate de tener permiso para realizar este tipo de scan'
            ],
            'suggestions': [
                'Usa wordlists apropiadas para el tamaño del target',
                'Ajusta el número de threads según la capacidad del servidor',
                'Considera usar filtros de status codes para reducir ruido'
            ]
        }

