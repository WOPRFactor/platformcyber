"""
Base Enumeration Service
=========================

Clase base común para todos los servicios de enumeración.
Proporciona funcionalidad compartida: ejecución de scans, logging, etc.
"""

import subprocess
import logging
import threading
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from utils.workspace_logger import log_to_workspace
from repositories import ScanRepository

logger = logging.getLogger(__name__)


class BaseEnumerationService:
    """Clase base para servicios de enumeración."""
    
    def __init__(self, scan_repository: ScanRepository = None, output_dir: Path = None):
        """
        Inicializa el servicio base.
        
        Args:
            scan_repository: Repositorio de scans
            output_dir: Directorio de salida (default: {proyecto}/tmp/enumeration)
                      Nota: Se usa dinámicamente por workspace, este es solo fallback
        """
        self.scan_repo = scan_repository or ScanRepository()
        if output_dir is None:
            from utils.workspace_filesystem import PROJECT_TMP_DIR
            output_dir = PROJECT_TMP_DIR / 'enumeration'
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_workspace_output_dir(self, scan_id: int) -> Path:
        """
        Obtiene directorio de output del workspace para un scan.
        
        Args:
            scan_id: ID del scan
        
        Returns:
            Path al directorio de output del workspace
        """
        from utils.workspace_filesystem import get_workspace_output_dir_from_scan
        return get_workspace_output_dir_from_scan(scan_id, 'enumeration')
    
    def _execute_scan(
        self,
        scan_id: int,
        command: list,
        output_file: str,
        tool: str,
        timeout: Optional[int] = None
    ) -> None:
        """
        Ejecuta un scan en thread separado.
        
        Args:
            scan_id: ID del scan
            command: Comando a ejecutar (lista)
            output_file: Archivo de salida
            tool: Nombre de la herramienta
            timeout: Timeout en segundos (opcional)
        """
        # CRÍTICO: Crear contexto de Flask para el thread
        from celery_app import get_flask_app
        app = get_flask_app()
        
        with app.app_context():
            try:
                # Obtener scan para workspace_id
                scan = self.scan_repo.find_by_id(scan_id)
                workspace_id = scan.workspace_id if scan else None
                
                command_str = ' '.join([c for c in command if c not in ['>', '2>&1']])
                logger.info(f"Executing {tool} {scan_id}: {command_str}")
                
                # Log inicial
                if workspace_id:
                    # Usar 'SCANNING' como source para que aparezca en la consola de logs
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source='SCANNING',
                        level='INFO',
                        message=f"[{tool.upper()}] Iniciando: {command_str}",
                        metadata={'command': command_str, 'scan_id': scan_id, 'tool': tool}
                    )
                
                # Timeouts por defecto por herramienta
                timeout_map = {
                'enum4linux': 600,      # 10 min
                'enum4linux-ng': 600,   # 10 min
                'smbmap': 300,           # 5 min
                'smbclient': 300,        # 5 min
                'ssh-audit': 300,        # 5 min
                'smtp-user-enum': 600,   # 10 min
                'snmpwalk': 300,         # 5 min
                'onesixtyone': 600,      # 10 min
                'ldapsearch': 300,       # 5 min
                'sslscan': 300,          # 5 min
                'sslyze': 600,           # 10 min
                }
                timeout = timeout or timeout_map.get(tool, 600)
                
                # Filtrar redirecciones de la lista de comandos
                clean_command = [c for c in command if c not in ['>', '2>&1']]
                
                # Verificar que la herramienta existe antes de ejecutar
                import shutil
                tool_name = clean_command[0] if clean_command else None
                if tool_name and not shutil.which(tool_name):
                    error_msg = f"Herramienta '{tool_name}' no encontrada en el PATH"
                    if tool_name == 'enum4linux-ng':
                        error_msg += ". Instala con: pip install enum4linux-ng o usa enum4linux"
                    elif tool_name == 'enum4linux':
                        error_msg += ". Instala con: apt install enum4linux"
                    raise FileNotFoundError(error_msg)
                
                # El progreso inicial ya se estableció en _start_scan_thread
                # Solo actualizar si no está establecido (por seguridad)
                scan = self.scan_repo.find_by_id(scan_id)
                if scan and scan.progress == 0:
                    self.scan_repo.update_progress(scan, 5, f'Iniciando {tool}...')
                
                # Ejecutar comando con Popen para monitorear progreso
                import time
                # Usar el directorio del workspace como cwd, no el directorio temporal
                workspace_output_dir = self._get_workspace_output_dir(scan_id)
                workspace_output_dir.mkdir(parents=True, exist_ok=True)
                
                process = subprocess.Popen(
                    clean_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,  # Evitar que comandos interactivos esperen input
                    text=True,
                    cwd=str(workspace_output_dir),  # Ejecutar desde el directorio del workspace
                    env=CommandSanitizer.get_safe_env() if hasattr(CommandSanitizer, 'get_safe_env') else None
                )
                
                # Monitorear progreso mientras se ejecuta
                start_time = time.time()
                last_update = start_time
                
                while process.poll() is None:
                    elapsed = time.time() - start_time
                    
                    # Actualizar progreso cada 5 segundos (más frecuente para mejor feedback)
                    if time.time() - last_update >= 5:
                        # Calcular progreso basado en tiempo transcurrido (5% -> 85%)
                        # Asegurar que siempre haya progreso mínimo visible
                        if elapsed < 5:
                            progress = 5  # Mínimo 5% al inicio
                        else:
                            progress = min(5 + int((elapsed / timeout) * 80), 85)
                        
                        elapsed_min = int(elapsed / 60)
                        elapsed_sec = int(elapsed % 60)
                        status_msg = f"Ejecutando {tool}... ({elapsed_min}m {elapsed_sec}s)"
                        
                        scan = self.scan_repo.find_by_id(scan_id)
                        if scan:
                            self.scan_repo.update_progress(scan, progress, status_msg)
                            logger.debug(f"[{tool}] Scan {scan_id} progreso actualizado: {progress}% ({status_msg})")
                        last_update = time.time()
                    
                    # Verificar timeout
                    if elapsed > timeout:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                        raise subprocess.TimeoutExpired(clean_command, timeout)
                    
                    time.sleep(2)  # Verificar cada 2 segundos
                
                # Obtener resultado
                stdout, stderr = process.communicate()
                result = type('Result', (), {
                    'returncode': process.returncode,
                    'stdout': stdout,
                    'stderr': stderr or ''
                })()
                
                # Guardar output (smbclient puede escribir errores en stdout)
                with open(output_file, 'w') as f:
                    if result.stdout:
                        f.write(result.stdout)
                    if result.stderr:
                        if result.stdout:
                            f.write(f"\n=== STDERR ===\n")
                        f.write(result.stderr)
                
                # Agregar return code al archivo
                with open(output_file, 'a') as f:
                    f.write(f"\n=== RETURN CODE ===\n{result.returncode}\n")
                
                # Obtener scan y actualizar estado
                scan = self.scan_repo.find_by_id(scan_id)
                workspace_id = scan.workspace_id if scan else None
                
                if result.returncode == 0:
                    # Actualizar estado y guardar ruta del archivo de salida
                    scan = self.scan_repo.update_status(scan, 'completed')
                    self.scan_repo.update_progress(scan, 100, output_file)  # Guardar ruta del archivo en scan.output
                    logger.info(f"{tool} {scan_id} completed successfully, output saved to: {output_file}")
                    
                    # Log de éxito
                    if workspace_id:
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source='SCANNING',
                            level='INFO',
                            message=f"[{tool.upper()}] Completado exitosamente",
                            metadata={'scan_id': scan_id, 'output_file': output_file, 'tool': tool}
                        )
                else:
                    # Capturar error del stdout también (smbclient puede escribir errores en stdout)
                    error_output = result.stderr or result.stdout or ''
                    # Buscar mensajes de error comunes en el output
                    if 'NT_STATUS' in error_output or 'Connection' in error_output or 'failed' in error_output.lower():
                        error_msg = error_output.strip() if error_output.strip() else f"Exit code: {result.returncode}"
                    else:
                        error_msg = error_output.strip() if error_output.strip() else f"Exit code: {result.returncode}"
                    
                    self.scan_repo.update_status(scan, 'failed', error_msg)
                    logger.error(f"{tool} {scan_id} failed: {error_msg}")
                    
                    # Log de error
                    if workspace_id:
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source='SCANNING',
                            level='ERROR',
                            message=f"[{tool.upper()}] Falló: {error_msg}",
                            metadata={'scan_id': scan_id, 'error': error_msg, 'return_code': result.returncode, 'tool': tool}
                        )
                    
            except subprocess.TimeoutExpired:
                scan = self.scan_repo.find_by_id(scan_id)
                workspace_id = scan.workspace_id if scan else None
                error_msg = f"Timeout after {timeout} seconds"
                if scan:
                    self.scan_repo.update_status(scan, 'failed', error_msg)
                    self.scan_repo.update_progress(scan, 0, error_msg)
                logger.error(f"{tool} {scan_id} timeout: {error_msg}")
                
                if workspace_id:
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source='SCANNING',
                        level='ERROR',
                        message=f"[{tool.upper()}] Timeout después de {timeout} segundos",
                        metadata={'scan_id': scan_id, 'timeout': timeout, 'tool': tool}
                    )
            
            except Exception as e:
                scan = self.scan_repo.find_by_id(scan_id)
                workspace_id = scan.workspace_id if scan else None
                error_msg = str(e)
                
                # Asegurar que el proceso se termine si existe
                if 'process' in locals() and process and process.poll() is None:
                    try:
                        process.terminate()
                        process.wait(timeout=5)
                    except:
                        try:
                            process.kill()
                        except:
                            pass
                
                # Actualizar estado a failed
                if scan:
                    self.scan_repo.update_status(scan, 'failed', error_msg)
                    logger.error(f"Error executing {tool} {scan_id}: {error_msg}", exc_info=True)
                
                if workspace_id:
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source='SCANNING',
                        level='ERROR',
                        message=f"[{tool.upper()}] Error: {error_msg}",
                        metadata={'scan_id': scan_id, 'error': error_msg, 'tool': tool}
                    )
            
            finally:
                # GARANTIZAR que el estado se actualice incluso si hay errores no capturados
                try:
                    scan = self.scan_repo.find_by_id(scan_id)
                    if scan and scan.status == 'running':
                        # Si todavía está en running después de todo, verificar si el proceso terminó
                        if 'process' in locals() and process and process.poll() is not None:
                            # Proceso terminó pero no se actualizó el estado
                            returncode = process.returncode
                            if returncode == 0:
                                self.scan_repo.update_status(scan, 'completed')
                                self.scan_repo.update_progress(scan, 100, 'Completado')
                                logger.warning(f"Scan {scan_id} completado pero estado no actualizado - corregido")
                            else:
                                error_msg = f"Process exited with code {returncode}"
                                self.scan_repo.update_status(scan, 'failed', error_msg)
                                logger.warning(f"Scan {scan_id} falló pero estado no actualizado - corregido")
                except Exception as cleanup_error:
                    logger.error(f"Error en finally block para scan {scan_id}: {cleanup_error}", exc_info=True)
    
    def _create_scan(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        tool: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Crea un nuevo scan en la base de datos.
        
        Args:
            target: Target del scan
            workspace_id: ID del workspace
            user_id: ID del usuario
            tool: Nombre de la herramienta
            options: Opciones adicionales
            
        Returns:
            Scan object
        """
        return self.scan_repo.create(
            scan_type='enumeration',
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': tool,
                **(options or {})
            }
        )
    
    def _start_scan_thread(
        self,
        scan_id: int,
        command: list,
        output_file: str,
        tool: str,
        timeout: Optional[int] = None
    ) -> None:
        """
        Inicia un scan en un thread separado.
        
        Args:
            scan_id: ID del scan
            command: Comando a ejecutar
            output_file: Archivo de salida
            tool: Nombre de la herramienta
            timeout: Timeout en segundos
        """
        # Actualizar progreso inicial ANTES de iniciar el thread
        # Esto asegura que el progreso se guarde inmediatamente
        scan = self.scan_repo.find_by_id(scan_id)
        if scan:
            self.scan_repo.update_progress(scan, 5, f'Iniciando {tool}...')
            logger.info(f"Progreso inicial establecido para scan {scan_id}: 5%")
        
        logger.info(f"Starting thread for {tool} scan {scan_id}, command: {' '.join(command)}")
        thread = threading.Thread(
            target=self._execute_scan,
            args=(scan_id, command, output_file, tool, timeout)
        )
        thread.daemon = True
        thread.start()
        logger.info(f"Thread started for {tool} scan {scan_id}, thread ID: {thread.ident}")

