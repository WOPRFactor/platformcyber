"""
Mobile Security Service
=======================

Servicio completo para pentesting de aplicaciones móviles (Android/iOS).

Herramientas integradas:
- MobSF (Mobile Security Framework)
- Frida (Dynamic Instrumentation)
- APKTool (APK Decompilation)
- Objection (Runtime Mobile Exploration)
"""

import subprocess
import logging
import json
import threading
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from utils.validators import CommandSanitizer
from utils.parsers.mobile_parser import (
    MobSFParser, FridaParser, APKToolParser, ObjectionParser
)
from repositories import ScanRepository

logger = logging.getLogger(__name__)


class MobileService:
    """Servicio completo para mobile pentesting."""
    
    def __init__(self, scan_repository: ScanRepository = None):
        """Inicializa el servicio."""
        self.scan_repo = scan_repository or ScanRepository()
        from utils.workspace_filesystem import PROJECT_TMP_DIR
        self.output_dir = PROJECT_TMP_DIR / 'mobile_security'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Parsers
        self.mobsf_parser = MobSFParser()
        self.frida_parser = FridaParser()
        self.apktool_parser = APKToolParser()
        self.objection_parser = ObjectionParser()
    
    # ============================================
    # MOBSF (Mobile Security Framework)
    # ============================================
    
    def start_mobsf_analysis(
        self,
        apk_path: str,
        workspace_id: int,
        user_id: int,
        analysis_type: str = 'static'
    ) -> Dict[str, Any]:
        """
        Ejecuta análisis con MobSF.
        
        Args:
            apk_path: Path al APK/IPA a analizar
            workspace_id: ID del workspace
            user_id: ID del usuario
            analysis_type: Tipo de análisis ('static' o 'dynamic')
        """
        if not Path(apk_path).exists():
            raise ValueError(f'File not found: {apk_path}')
        
        scan = self.scan_repo.create(
            scan_type='mobile_security',
            target=Path(apk_path).name,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'mobsf',
                'analysis_type': analysis_type,
                'apk_path': apk_path
            }
        )
        
        try:
            output_file = str(self.output_dir / f'mobsf_{scan.id}.json')
            
            # MobSF suele usarse vía API REST, pero aquí simulamos análisis
            # En producción, se haría una llamada a la API de MobSF
            command = [
                'mobsf',
                'analyze',
                apk_path,
                '--output', output_file,
                '--type', analysis_type
            ]
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting MobSF {analysis_type} analysis {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'mobsf')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'mobsf',
                'target': Path(apk_path).name,
                'analysis_type': analysis_type
            }
            
        except Exception as e:
            logger.error(f"Error starting MobSF: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # APKTOOL (APK Decompilation)
    # ============================================
    
    def decompile_apk(
        self,
        apk_path: str,
        workspace_id: int,
        user_id: int,
        decode_resources: bool = True
    ) -> Dict[str, Any]:
        """
        Decompila un APK con APKTool.
        
        Args:
            apk_path: Path al APK
            workspace_id: ID del workspace
            user_id: ID del usuario
            decode_resources: Decodificar recursos (XML, etc.)
        """
        if not Path(apk_path).exists():
            raise ValueError(f'File not found: {apk_path}')
        
        scan = self.scan_repo.create(
            scan_type='mobile_security',
            target=Path(apk_path).name,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'apktool',
                'action': 'decompile',
                'decode_resources': decode_resources
            }
        )
        
        try:
            # Directorio de salida
            output_dir = self.output_dir / f'apktool_{scan.id}'
            output_dir.mkdir(exist_ok=True)
            
            command = ['apktool', 'd', apk_path, '-o', str(output_dir), '-f']
            
            if not decode_resources:
                command.append('-r')  # No decodificar recursos
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting APKTool decompile {scan.id}")
            
            result = subprocess.run(
                sanitized_cmd,
                capture_output=True,
                text=True,
                timeout=300,
                env=CommandSanitizer.get_safe_env()
            )
            
            if result.returncode == 0:
                self.scan_repo.update_status(scan, 'completed')
                self.scan_repo.update_progress(scan, 100, 'APK decompiled')
                
                # Parsear resultados
                results = self.apktool_parser.parse_decompiled_structure(str(output_dir))
                
                return {
                    'scan_id': scan.id,
                    'status': 'completed',
                    'tool': 'apktool',
                    'output_dir': str(output_dir),
                    'results': results
                }
            else:
                self.scan_repo.update_status(scan, 'failed', result.stderr)
                raise Exception(result.stderr)
                
        except Exception as e:
            logger.error(f"Error decompiling APK: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # FRIDA (Dynamic Instrumentation)
    # ============================================
    
    def start_frida_trace(
        self,
        package_name: str,
        workspace_id: int,
        user_id: int,
        trace_functions: Optional[List[str]] = None,
        device_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Inicia tracing con Frida.
        
        Args:
            package_name: Package de la app (ej: com.example.app)
            workspace_id: ID del workspace
            user_id: ID del usuario
            trace_functions: Funciones a tracear (opcional)
            device_id: ID del dispositivo (opcional, default: USB device)
        """
        scan = self.scan_repo.create(
            scan_type='mobile_security',
            target=package_name,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'frida',
                'action': 'trace',
                'trace_functions': trace_functions or []
            }
        )
        
        try:
            output_file = str(self.output_dir / f'frida_{scan.id}.log')
            
            # Frida trace
            command = ['frida-trace']
            
            if device_id:
                command.extend(['-D', device_id])
            else:
                command.append('-U')  # USB device
            
            if trace_functions:
                for func in trace_functions:
                    command.extend(['-i', func])
            else:
                # Trace default: Java methods
                command.extend(['-i', 'Java.*'])
            
            command.extend(['-o', output_file, package_name])
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting Frida trace {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'frida')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'frida',
                'target': package_name,
                'message': 'Frida trace running. Use stop_scan to terminate.'
            }
            
        except Exception as e:
            logger.error(f"Error starting Frida: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # OBJECTION (Runtime Mobile Exploration)
    # ============================================
    
    def start_objection_explore(
        self,
        package_name: str,
        workspace_id: int,
        user_id: int,
        commands: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta comandos de Objection.
        
        Args:
            package_name: Package de la app
            workspace_id: ID del workspace
            user_id: ID del usuario
            commands: Lista de comandos Objection (opcional)
        """
        scan = self.scan_repo.create(
            scan_type='mobile_security',
            target=package_name,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'objection',
                'commands': commands or []
            }
        )
        
        try:
            output_file = str(self.output_dir / f'objection_{scan.id}.txt')
            
            # Comando base
            base_cmd = ['objection', '-g', package_name, 'explore']
            
            results = {}
            
            if commands:
                # Ejecutar cada comando
                for cmd in commands:
                    logger.info(f"Running objection command: {cmd}")
                    
                    full_cmd = base_cmd + ['-c', cmd]
                    sanitized_cmd = CommandSanitizer.sanitize_command(full_cmd[0], full_cmd[1:])
                    
                    result = subprocess.run(
                        sanitized_cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        env=CommandSanitizer.get_safe_env()
                    )
                    
                    results[cmd] = {
                        'output': result.stdout,
                        'error': result.stderr,
                        'success': result.returncode == 0
                    }
            else:
                # Exploración básica
                commands = [
                    'env',  # Variables de entorno
                    'android hooking list classes',  # Listar clases
                    'android intent launch_activity'  # Activities
                ]
                
                for cmd in commands:
                    full_cmd = base_cmd + ['-c', cmd]
                    sanitized_cmd = CommandSanitizer.sanitize_command(full_cmd[0], full_cmd[1:])
                    
                    result = subprocess.run(
                        sanitized_cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        env=CommandSanitizer.get_safe_env()
                    )
                    
                    results[cmd] = {
                        'output': result.stdout,
                        'error': result.stderr,
                        'success': result.returncode == 0
                    }
            
            # Guardar resultados
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.scan_repo.update_status(scan, 'completed')
            self.scan_repo.update_progress(scan, 100, 'Objection exploration completed')
            
            return {
                'scan_id': scan.id,
                'status': 'completed',
                'tool': 'objection',
                'target': package_name,
                'results': self.objection_parser.parse_explore_output(json.dumps(results))
            }
            
        except Exception as e:
            logger.error(f"Error running Objection: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # OBTENER RESULTADOS
    # ============================================
    
    def get_scan_results(self, scan_id: int) -> Dict[str, Any]:
        """Obtiene y parsea resultados de mobile security scan."""
        scan = self.scan_repo.find_by_id(scan_id)
        
        if not scan:
            raise ValueError(f'Scan {scan_id} not found')
        
        if scan.status != 'completed':
            return {
                'scan_id': scan_id,
                'status': scan.status,
                'message': 'Scan not completed yet'
            }
        
        tool = scan.options.get('tool')
        
        try:
            if tool == 'mobsf':
                output_file = self.output_dir / f'mobsf_{scan_id}.json'
                with open(output_file, 'r') as f:
                    results = self.mobsf_parser.parse_static_analysis(f.read())
            
            elif tool == 'apktool':
                output_dir = self.output_dir / f'apktool_{scan_id}'
                results = self.apktool_parser.parse_decompiled_structure(str(output_dir))
            
            elif tool == 'frida':
                output_file = self.output_dir / f'frida_{scan_id}.log'
                with open(output_file, 'r') as f:
                    results = self.frida_parser.parse_trace_log(f.read())
            
            elif tool == 'objection':
                output_file = self.output_dir / f'objection_{scan_id}.txt'
                with open(output_file, 'r') as f:
                    results = self.objection_parser.parse_explore_output(f.read())
            
            else:
                results = {'error': f'Unknown tool: {tool}'}
            
            return {
                'scan_id': scan_id,
                'status': 'completed',
                'tool': tool,
                'results': results,
                'scan_info': {
                    'target': scan.target,
                    'started_at': scan.started_at.isoformat() if scan.started_at else None,
                    'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing mobile security results {scan_id}: {e}")
            return {
                'scan_id': scan_id,
                'error': f'Failed to parse results: {str(e)}'
            }
    
    # ============================================
    # HELPERS PRIVADOS
    # ============================================
    
    def _execute_scan(
        self,
        scan_id: int,
        command: list,
        output_file: str,
        tool: str
    ) -> None:
        """Ejecuta mobile security scan en thread separado."""
        try:
            logger.info(f"Executing {tool} {scan_id}: {' '.join(command)}")
            
            # Timeouts
            timeout_map = {
                'mobsf': 1800,    # 30 min (análisis pesado)
                'apktool': 300,   # 5 min
                'frida': 1800,    # 30 min
                'objection': 300  # 5 min
            }
            timeout = timeout_map.get(tool, 600)
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=CommandSanitizer.get_safe_env()
            )
            
            # Guardar output si no existe
            if not Path(output_file).exists() and result.stdout:
                with open(output_file, 'w') as f:
                    f.write(result.stdout)
            
            scan = self.scan_repo.find_by_id(scan_id)
            
            if result.returncode == 0:
                self.scan_repo.update_status(scan, 'completed')
                self.scan_repo.update_progress(scan, 100, result.stdout[:1000])
                logger.info(f"{tool} {scan_id} completed")
            else:
                error_msg = result.stderr or "Unknown error"
                self.scan_repo.update_status(scan, 'failed', error_msg)
                logger.error(f"{tool} {scan_id} failed: {error_msg}")
                
        except subprocess.TimeoutExpired:
            scan = self.scan_repo.find_by_id(scan_id)
            self.scan_repo.update_status(scan, 'failed', f'Timeout ({timeout}s)')
            logger.error(f"{tool} {scan_id} timeout")
            
        except Exception as e:
            scan = self.scan_repo.find_by_id(scan_id)
            self.scan_repo.update_status(scan, 'failed', str(e))
            logger.error(f"{tool} {scan_id} error: {e}", exc_info=True)



