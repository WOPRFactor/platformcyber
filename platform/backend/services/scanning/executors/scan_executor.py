"""
Scan Executor for Scanning Service
==================================

Ejecutor de scans de red en background.
Reutiliza la lógica del ejecutor de vulnerability.
"""

import logging
from typing import List
from pathlib import Path
import subprocess
import time
import os
import shutil

from utils.validators import CommandSanitizer
from utils.workspace_logger import log_to_workspace
from repositories import ScanRepository
from utils.parsers.nmap_parser import NmapParser, RustScanParser, MasscanParser

logger = logging.getLogger(__name__)


class ScanningExecutor:
    """Ejecutor de scans de red en background."""
    
    def __init__(self, scan_repository: ScanRepository = None):
        """Inicializa el ejecutor."""
        self.scan_repo = scan_repository or ScanRepository()
        
        # Parsers por herramienta
        self.parsers = {
            'nmap': NmapParser(),
            'rustscan': RustScanParser(),
            'masscan': MasscanParser()
        }
        
        # Timeouts por herramienta
        self.timeout_map = {
            'nmap': 3600,      # 1 hora
            'rustscan': 600,   # 10 minutos
            'masscan': 1800,   # 30 minutos
            'naabu': 600       # 10 minutos
        }
    
    def execute_scan(
        self,
        scan_id: int,
        command: List[str],
        output_file: str,
        tool: str,
        workspace_id: int
    ) -> None:
        """
        Ejecuta un scan en background y procesa los resultados.
        
        Args:
            scan_id: ID del scan
            command: Comando a ejecutar
            output_file: Archivo de salida
            tool: Nombre de la herramienta
            workspace_id: ID del workspace
        """
        from celery_app import get_flask_app
        
        app = get_flask_app()
        
        with app.app_context():
            try:
                scan = self.scan_repo.find_by_id(scan_id)
                if not scan:
                    logger.error(f"Scan {scan_id} not found")
                    return
                
                workspace_id = scan.workspace_id
                
                # Verificar que la herramienta existe
                tool_name = command[0] if command else None
                if tool_name:
                    tool_path = self._find_tool_path(tool_name, tool)
                    if not tool_path:
                        error_msg = self._get_tool_error_message(tool_name)
                        self.scan_repo.update_status(scan, 'failed', error_msg)
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source=tool.upper(),
                            level='ERROR',
                            message=error_msg,
                            metadata={'scan_id': scan_id, 'tool': tool_name}
                        )
                        return
                
                log_to_workspace(
                    workspace_id=workspace_id,
                    source=tool.upper(),
                    level='INFO',
                    message=f"Executing {tool} scan {scan_id}",
                    metadata={'scan_id': scan_id, 'command': ' '.join(command)}
                )
                
                timeout = self.timeout_map.get(tool, 1800)
                env = CommandSanitizer.get_safe_env()
                
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env
                )
                
                # Guardar PID
                if scan.options:
                    scan.options['pid'] = process.pid
                    from repositories import ScanRepository
                    ScanRepository().update_options(scan, scan.options)
                
                start_time = time.time()
                last_update = start_time
                
                # Actualizar progreso durante la ejecución
                while process.poll() is None:
                    elapsed = time.time() - start_time
                    
                    if time.time() - last_update >= 10:
                        progress = min(5 + int((elapsed / timeout) * 80), 85)
                        elapsed_min = int(elapsed / 60)
                        elapsed_sec = int(elapsed % 60)
                        status_msg = f"Ejecutando {tool}... ({elapsed_min}m {elapsed_sec}s)"
                        
                        scan = self.scan_repo.find_by_id(scan_id)
                        if scan:
                            self.scan_repo.update_progress(scan, progress, status_msg)
                        last_update = time.time()
                    
                    if elapsed > timeout:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                        raise subprocess.TimeoutExpired(command, timeout)
                    
                    time.sleep(2)
                
                stdout, stderr = process.communicate()
                
                # Guardar stdout si no hay archivo de salida
                output_path = Path(output_file)
                if not output_path.exists() and stdout:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, 'w') as f:
                        f.write(stdout)
                
                # Esperar para herramientas que escriben directamente a archivo
                if tool in ['nmap', 'rustscan', 'masscan']:
                    time.sleep(1)
                
                # Parsear resultados si hay parser disponible
                if tool in self.parsers and output_path.exists():
                    try:
                        parser = self.parsers[tool]
                        if tool == 'nmap':
                            results = parser.parse_xml(str(output_path))
                        else:
                            with open(output_path, 'r') as f:
                                output = f.read()
                            results = parser.parse_output(output)
                        
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source=tool.upper(),
                            level='INFO',
                            message=f"Scan {scan_id} completed. Parsed results successfully",
                            metadata={'scan_id': scan_id}
                        )
                    except Exception as parse_error:
                        logger.error(f"Error parsing {tool} results: {parse_error}")
                
                if process.returncode == 0:
                    self.scan_repo.update_status(scan, 'completed')
                    self.scan_repo.update_progress(scan, 100, f"{tool} completado")
                else:
                    error_msg = stderr or stdout or 'Unknown error'
                    logger.error(f"{tool} scan {scan_id} failed: {error_msg}")
                    self.scan_repo.update_status(scan, 'failed', error_msg)
                    
            except subprocess.TimeoutExpired:
                scan = self.scan_repo.find_by_id(scan_id)
                if scan:
                    self.scan_repo.update_status(scan, 'failed', f'Timeout ({timeout}s)')
                    log_to_workspace(
                        workspace_id=scan.workspace_id,
                        source=tool.upper(),
                        level='ERROR',
                        message=f"{tool} scan {scan_id} timeout after {timeout}s",
                        metadata={'scan_id': scan_id, 'timeout': timeout}
                    )
            except Exception as e:
                logger.error(f"Error executing {tool} scan {scan_id}: {e}")
                scan = self.scan_repo.find_by_id(scan_id)
                if scan:
                    self.scan_repo.update_status(scan, 'failed', str(e))
                    log_to_workspace(
                        workspace_id=scan.workspace_id,
                        source=tool.upper(),
                        level='ERROR',
                        message=f"Error executing scan: {str(e)}",
                        metadata={'scan_id': scan_id, 'error': str(e)}
                    )
    
    def _find_tool_path(self, tool_name: str, tool: str) -> str:
        """Busca la ruta de una herramienta."""
        if tool_name.startswith('/'):
            try:
                result = subprocess.run(
                    [tool_name, '--help'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0 or tool.upper() in result.stdout or tool.upper() in result.stderr:
                    return tool_name
            except Exception:
                if os.path.isfile(tool_name) or os.access(tool_name, os.F_OK):
                    return tool_name
        
        tool_path = shutil.which(tool_name)
        if tool_path:
            return tool_path
        
        # Intentar ejecutar directamente
        try:
            result = subprocess.run(
                [tool_name, '--help'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 or tool.upper() in result.stdout or tool.upper() in result.stderr:
                return tool_name
        except Exception:
            pass
        
        return None
    
    def _get_tool_error_message(self, tool_name: str) -> str:
        """Obtiene mensaje de error específico por herramienta."""
        error_msg = f"Herramienta '{tool_name}' no encontrada en el PATH."
        if 'rustscan' in tool_name.lower():
            error_msg += " Instala RustScan con: cargo install rustscan"
        elif 'masscan' in tool_name.lower():
            error_msg += " Instala Masscan con: apt install masscan"
        elif 'naabu' in tool_name.lower():
            error_msg += " Instala Naabu con: go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"
        return error_msg
    
    def execute_async(
        self,
        scan_id: int,
        command: List[str],
        output_file: str,
        tool: str,
        workspace_id: int
    ) -> None:
        """
        Ejecuta un scan de forma asíncrona en un thread separado.
        
        Args:
            scan_id: ID del scan
            command: Comando a ejecutar
            output_file: Archivo de salida
            tool: Nombre de la herramienta
            workspace_id: ID del workspace
        """
        import threading
        thread = threading.Thread(
            target=self.execute_scan,
            args=(scan_id, command, output_file, tool, workspace_id)
        )
        thread.daemon = True
        thread.start()


