"""
Reconnaissance Command Executor
================================

Lógica para ejecutar comandos de reconocimiento con manejo de progreso y filtrado.
"""

import subprocess
import logging
import time
import shutil
from typing import List
from pathlib import Path

from utils.validators import CommandSanitizer
from utils.workspace_logger import log_to_workspace
from .filters import (
    filter_dnsenum_warnings,
    filter_whois_informational_messages,
    filter_theharvester_banner
)

logger = logging.getLogger(__name__)


class ReconnaissanceExecutor:
    """Ejecutor de comandos de reconocimiento"""
    
    def __init__(self, scan_repo):
        """Inicializar ejecutor"""
        self.scan_repo = scan_repo
    
    def execute_scan(
        self,
        scan_id: int,
        command: List[str],
        output_file: str,
        scan_type: str
    ) -> None:
        """
        Ejecuta scan en thread separado.
        
        Args:
            scan_id: ID del escaneo
            command: Comando a ejecutar
            output_file: Archivo de salida
            scan_type: Tipo de scan para logging
        """
        from celery_app import get_flask_app
        
        app = get_flask_app()
        
        with app.app_context():
            try:
                scan = self.scan_repo.find_by_id(scan_id)
                workspace_id = scan.workspace_id if scan else None
                
                command_str = ' '.join([c for c in command if c not in ['>', '2>&1']])
                logger.info(f"Executing {scan_type} scan {scan_id}: {command_str}")
                
                tool_name = command[0] if command else None
                if tool_name:
                    tool_path = shutil.which(tool_name)
                    if not tool_path:
                        install_messages = {
                            'katana': 'Instalar: go install github.com/projectdiscovery/katana/cmd/katana@latest',
                            'gospider': 'Instalar: go install github.com/jaeles-project/gospider@latest',
                            'hakrawler': 'Instalar: sudo apt install hakrawler o go install github.com/hakluke/hakrawler@latest',
                            'waybackurls': 'Instalar: go install github.com/tomnomnom/waybackurls@latest'
                        }
                        install_hint = install_messages.get(tool_name, '')
                        error_msg = f"Herramienta '{tool_name}' no encontrada en el PATH. {install_hint if install_hint else 'Por favor, instálala o verifica que esté disponible.'}"
                        self.scan_repo.update_status(scan, 'failed', error_msg)
                        logger.error(f"Recon scan {scan_id} error: {error_msg}")
                        if workspace_id:
                            log_to_workspace(
                                workspace_id=workspace_id,
                                source=scan_type.upper(),
                                level='ERROR',
                                message=f"Error en {scan_type}: {error_msg}",
                                metadata={'scan_id': scan_id, 'error': error_msg, 'tool': tool_name}
                            )
                        return
                
                if workspace_id:
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source=scan_type.upper(),
                        level='INFO',
                        message=f"Iniciando {scan_type}: {command_str}",
                        metadata={'command': command_str, 'scan_id': scan_id}
                    )
                
                self.scan_repo.update_progress(scan, 25, f"Ejecutando {scan_type}...")
                
                if workspace_id:
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source=scan_type.upper(),
                        level='INFO',
                        message=f"Ejecutando comando: {command_str}",
                        metadata={'scan_id': scan_id, 'progress': 25}
                    )
                
                self.scan_repo.update_progress(scan, 50, f"Ejecutando comando: {command_str[:50]}...")
                
                tool_name = command[0] if command else ""
                is_long_running = 'amass' in tool_name.lower() or 'theHarvester' in tool_name or 'dnsenum' in tool_name.lower() or 'fierce' in tool_name.lower()
                
                if is_long_running:
                    result = self._execute_long_running_command(
                        scan_id, command, output_file, scan_type, tool_name, workspace_id
                    )
                else:
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        timeout=1800,
                        env=CommandSanitizer.get_safe_env()
                    )
                
                scan = self.scan_repo.find_by_id(scan_id)
                self.scan_repo.update_progress(scan, 75, "Procesando resultados...")
                
                if workspace_id:
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source=scan_type.upper(),
                        level='INFO',
                        message=f"Procesando resultados del comando...",
                        metadata={'scan_id': scan_id, 'progress': 75}
                    )
                
                # Algunas herramientas (como amass con -o) escriben directamente al archivo
                # Verificar si el archivo existe primero, si no, usar stdout
                if Path(output_file).exists():
                    # Archivo ya existe (escrito directamente por la herramienta)
                    logger.info(f"Output file already exists for scan {scan_id}: {output_file}")
                elif result.stdout:
                    # Guardar stdout si el archivo no existe
                    output_content = result.stdout
                    if '***' in output_content or ('*' in output_content and ('theHarvester' in tool_name or 'harvester' in tool_name.lower())):
                        output_content = filter_theharvester_banner(output_content)
                    with open(output_file, 'w') as f:
                        f.write(output_content)
                    logger.info(f"Saved stdout to output file for scan {scan_id}: {output_file}")
                else:
                    # No hay archivo ni stdout - puede ser un error o la herramienta no produjo output
                    logger.warning(f"No output file or stdout for scan {scan_id} (tool: {tool_name})")
                
                self._process_result(scan_id, command, output_file, scan_type, result, workspace_id)
                
            except subprocess.TimeoutExpired:
                scan = self.scan_repo.find_by_id(scan_id)
                workspace_id = scan.workspace_id if scan else None
                self.scan_repo.update_status(scan, 'failed', 'Timeout exceeded (30 min)')
                logger.error(f"Recon scan {scan_id} timeout")
                
                if workspace_id:
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source=scan_type.upper(),
                        level='ERROR',
                        message=f"{scan_type} timeout (30 minutos)",
                        metadata={'scan_id': scan_id}
                    )
                
            except FileNotFoundError as e:
                scan = self.scan_repo.find_by_id(scan_id)
                workspace_id = scan.workspace_id if scan else None
                tool_name = command[0] if command else 'unknown'
                error_msg = f"Herramienta '{tool_name}' no encontrada. Por favor, instálala o verifica que esté en el PATH."
                self.scan_repo.update_status(scan, 'failed', error_msg)
                logger.error(f"Recon scan {scan_id} error: {error_msg} (Original: {e})", exc_info=True)
                
                if workspace_id:
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source=scan_type.upper(),
                        level='ERROR',
                        message=f"Error en {scan_type}: {error_msg}",
                        metadata={'scan_id': scan_id, 'error': error_msg, 'tool': tool_name}
                    )
            except Exception as e:
                scan = self.scan_repo.find_by_id(scan_id)
                workspace_id = scan.workspace_id if scan else None
                self.scan_repo.update_status(scan, 'failed', str(e))
                logger.error(f"Recon scan {scan_id} error: {e}", exc_info=True)
                
                if workspace_id:
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source=scan_type.upper(),
                        level='ERROR',
                        message=f"Error en {scan_type}: {str(e)}",
                        metadata={'scan_id': scan_id, 'error': str(e)}
                    )
    
    def _execute_long_running_command(
        self,
        scan_id: int,
        command: List[str],
        output_file: str,
        scan_type: str,
        tool_name: str,
        workspace_id: int
    ):
        """Ejecuta comandos de larga duración con monitoreo de progreso"""
        import time
        
        if 'dnsenum' in tool_name.lower() or 'fierce' in tool_name.lower():
            TIMEOUT_SECONDS = 1200
        else:
            TIMEOUT_SECONDS = 1800
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,  # Evitar que comandos interactivos esperen input
            text=True,
            env=CommandSanitizer.get_safe_env()
        )
        
        scan = self.scan_repo.find_by_id(scan_id)
        if scan:
            try:
                self.scan_repo.update_options(scan, {
                    'pid': process.pid,
                    'command': ' '.join(command),
                    'tool': tool_name
                })
                logger.info(f"✅ Saved PID {process.pid} for scan {scan_id} (tool: {tool_name})")
            except Exception as e:
                logger.error(f"❌ Error saving PID for scan {scan_id}: {e}", exc_info=True)
        
        start_time = time.time()
        last_update = start_time
        timeout_exceeded = False
        
        # Para amass, usar timeout más corto si se queda colgado por libpostal
        amass_hang_timeout = 90  # 90 segundos para detectar si está colgado
        
        while process.poll() is None:
            elapsed = time.time() - start_time
            
            # Detectar si amass se queda colgado (especialmente por error de libpostal)
            if 'amass' in tool_name.lower() and elapsed > amass_hang_timeout:
                # Verificar si el proceso está realmente activo o colgado
                # Si lleva más de 90 segundos sin terminar, probablemente está colgado
                logger.warning(f"Amass scan {scan_id} lleva {elapsed:.0f}s sin completar, verificando si está colgado...")
                
                # Intentar leer stderr para ver si hay error de libpostal
                # Si el proceso está colgado, terminarlo
                logger.error(f"Amass scan {scan_id} parece estar colgado (probablemente por error de libpostal), terminando...")
                timeout_exceeded = True
                try:
                    process.terminate()
                    try:
                        stdout, stderr = process.communicate(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        stdout, stderr = process.communicate()
                except Exception as e:
                    logger.error(f"Error terminando proceso amass {scan_id}: {e}")
                    try:
                        process.kill()
                    except:
                        pass
                
                scan = self.scan_repo.find_by_id(scan_id)
                if scan:
                    error_msg = "Amass se quedó colgado (probablemente por error de libpostal). Intenta usar subfinder en su lugar o instala libpostal."
                    self.scan_repo.update_status(scan, 'failed', error_msg)
                    self.scan_repo.update_progress(scan, 0, error_msg)
                    
                    if workspace_id:
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source=scan_type.upper(),
                            level='ERROR',
                            message=f"{scan_type} falló: {error_msg}",
                            metadata={'scan_id': scan_id, 'error': error_msg, 'tool': tool_name}
                        )
                
                result = type('Result', (), {
                    'returncode': -1,
                    'stdout': stdout if 'stdout' in locals() else '',
                    'stderr': stderr if 'stderr' in locals() else error_msg
                })()
                break
            
            if elapsed > TIMEOUT_SECONDS:
                timeout_exceeded = True
                logger.warning(f"Scan {scan_id} excedió timeout de {TIMEOUT_SECONDS}s, terminando proceso...")
                
                try:
                    process.terminate()
                    try:
                        stdout, stderr = process.communicate(timeout=5)
                    except subprocess.TimeoutExpired:
                        logger.warning(f"Proceso {scan_id} no terminó, forzando kill...")
                        process.kill()
                        stdout, stderr = process.communicate()
                except Exception as e:
                    logger.error(f"Error terminando proceso {scan_id}: {e}")
                    try:
                        process.kill()
                    except:
                        pass
                
                scan = self.scan_repo.find_by_id(scan_id)
                if scan:
                    self.scan_repo.update_status(scan, 'failed', f'Timeout exceeded ({TIMEOUT_SECONDS // 60} min)')
                    self.scan_repo.update_progress(scan, 0, f"Timeout: el comando excedió {TIMEOUT_SECONDS // 60} minutos")
                    
                    if workspace_id:
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source=scan_type.upper(),
                            level='ERROR',
                            message=f"{scan_type} timeout ({TIMEOUT_SECONDS // 60} minutos)",
                            metadata={'scan_id': scan_id, 'timeout': TIMEOUT_SECONDS}
                        )
                
                result = type('Result', (), {
                    'returncode': -1,
                    'stdout': stdout if 'stdout' in locals() else '',
                    'stderr': stderr if 'stderr' in locals() else f'Timeout exceeded ({TIMEOUT_SECONDS // 60} minutes)'
                })()
                break
            
            if 'dnsenum' in tool_name.lower() or 'fierce' in tool_name.lower():
                if elapsed <= 600:
                    progress = min(50 + int((elapsed / 600) * 35), 85)
                else:
                    extra_time = elapsed - 600
                    progress = min(85 + int((extra_time / 1200) * 10), 95)
            else:
                progress = min(50 + int((elapsed / TIMEOUT_SECONDS) * 20), 70)
            
            if time.time() - last_update >= 10:
                scan = self.scan_repo.find_by_id(scan_id)
                if scan:
                    elapsed_min = int(elapsed / 60)
                    elapsed_sec = int(elapsed % 60)
                    if 'dnsenum' in tool_name.lower() or 'fierce' in tool_name.lower():
                        if elapsed <= 600:
                            remaining_min = int((600 - elapsed) / 60)
                            remaining_sec = int((600 - elapsed) % 60)
                            status_msg = f"Ejecutando {scan_type}... ({elapsed_min}m {elapsed_sec}s / ~{remaining_min}m {remaining_sec}s restantes)"
                        else:
                            status_msg = f"Ejecutando {scan_type}... ({elapsed_min}m {elapsed_sec}s - puede tardar más tiempo)"
                    else:
                        remaining_min = int((TIMEOUT_SECONDS - elapsed) / 60)
                        remaining_sec = int((TIMEOUT_SECONDS - elapsed) % 60)
                        status_msg = f"Ejecutando {scan_type}... ({elapsed_min}m {elapsed_sec}s / ~{remaining_min}m {remaining_sec}s restantes)"
                    
                    self.scan_repo.update_progress(scan, progress, status_msg)
                    last_update = time.time()
            time.sleep(2)
        
        if not timeout_exceeded:
            # Esperar a que el proceso termine completamente
            try:
                stdout, stderr = process.communicate(timeout=10)  # Timeout de seguridad para communicate
            except subprocess.TimeoutExpired:
                # Si communicate también se cuelga, forzar terminación
                logger.warning(f"Process {scan_id} communicate() timeout, forcing termination...")
                process.kill()
                stdout, stderr = process.communicate()
            
            result = type('Result', (), {
                'returncode': process.returncode,
                'stdout': stdout,
                'stderr': stderr
            })()
            
            # Verificar que el archivo de salida existe (para herramientas que escriben directamente)
            if Path(output_file).exists():
                logger.info(f"Output file exists for scan {scan_id}: {output_file}")
            elif not stdout and not stderr:
                # Proceso terminó pero no hay output - puede ser un problema
                logger.warning(f"Process {scan_id} completed but no output file or stdout/stderr (tool: {tool_name})")
            
            return result
        
        return result
    
    def _process_result(
        self,
        scan_id: int,
        command: List[str],
        output_file: str,
        scan_type: str,
        result,
        workspace_id: int
    ):
        """Procesa el resultado de la ejecución del comando"""
        scan = self.scan_repo.find_by_id(scan_id)
        tool_name = command[0] if command else ""
        is_whois = 'whois' in tool_name.lower()
        is_dnsenum = 'dnsenum' in tool_name.lower()
        
        if is_whois and result.stdout:
            _, whois_is_informational = filter_whois_informational_messages(result.stdout)
            if whois_is_informational and result.returncode != 0:
                logger.info(f"WHOIS scan {scan_id} returned informational message (not an error)")
                self.scan_repo.update_status(scan, 'completed')
                progress_output = result.stdout[:1000] if result.stdout else "Consulta WHOIS completada (información disponible en sitio web del registro)"
                self.scan_repo.update_progress(scan, 100, progress_output)
                
                if workspace_id:
                    log_to_workspace(
                        workspace_id=workspace_id,
                        source=scan_type.upper(),
                        level='INFO',
                        message=f"{scan_type} completado (mensaje informativo: este TLD no tiene servidor whois público)",
                        metadata={'scan_id': scan_id, 'output_file': output_file, 'informational': True}
                    )
                return
        
        # Verificar errores de libpostal en amass (puede aparecer en stderr pero el proceso puede continuar)
        is_amass = 'amass' in tool_name.lower()
        libpostal_error = False
        if is_amass and result.stderr:
            if 'libpostal' in result.stderr.lower() or 'transliteration' in result.stderr.lower():
                libpostal_error = True
                logger.warning(f"Amass scan {scan_id} tiene error de libpostal (puede continuar): {result.stderr[:200]}")
        
        if result.returncode == 0:
            self.scan_repo.update_status(scan, 'completed')
            progress_output = result.stdout[:1000] if result.stdout else ""
            if progress_output and ('***' in progress_output or ('*' in progress_output and ('theHarvester' in tool_name or 'harvester' in tool_name.lower()))):
                progress_output = filter_theharvester_banner(progress_output).strip()
            
            # Si hay error de libpostal pero el proceso terminó exitosamente, agregar nota
            if libpostal_error:
                progress_output = f"Completado (advertencia: error de libpostal ignorado)\n{progress_output}" if progress_output else "Completado (advertencia: error de libpostal ignorado)"
            
            self.scan_repo.update_progress(scan, 100, progress_output)
            logger.info(f"Recon scan {scan_id} completed successfully")
            
            if workspace_id:
                log_message = f"{scan_type} completado exitosamente"
                if libpostal_error:
                    log_message += " (advertencia: error de libpostal ignorado)"
                log_to_workspace(
                    workspace_id=workspace_id,
                    source=scan_type.upper(),
                    level='INFO',
                    message=log_message,
                    metadata={'scan_id': scan_id, 'output_file': output_file, 'libpostal_warning': libpostal_error}
                )
        else:
            self._handle_error(scan_id, command, output_file, scan_type, result, workspace_id, tool_name, is_whois, is_dnsenum)
    
    def _handle_error(
        self,
        scan_id: int,
        command: List[str],
        output_file: str,
        scan_type: str,
        result,
        workspace_id: int,
        tool_name: str,
        is_whois: bool,
        is_dnsenum: bool
    ):
        """Maneja errores de ejecución con filtrado apropiado"""
        scan = self.scan_repo.find_by_id(scan_id)
        tool_name_lower = tool_name.lower()
        error_parts = []
        has_real_error = False
        
        if result.stderr:
            filtered_stderr = result.stderr.strip()
            
            if '***' in filtered_stderr or '*' in filtered_stderr or 'theharvester' in tool_name_lower or 'harvester' in tool_name_lower:
                filtered_stderr = filter_theharvester_banner(filtered_stderr).strip()
            
            if is_dnsenum:
                filtered_stderr = filter_dnsenum_warnings(filtered_stderr).strip()
            
            if is_whois:
                filtered_stderr, is_informational = filter_whois_informational_messages(filtered_stderr)
                if not is_informational:
                    stderr_content = filtered_stderr[:500].strip()
                    if stderr_content and stderr_content.replace(' ', '').replace('\t', '').replace('\n', ''):
                        error_parts.append(f"stderr: {stderr_content}")
                        has_real_error = True
            else:
                stderr_content = filtered_stderr[:500].strip()
                if stderr_content and stderr_content.replace(' ', '').replace('\t', '').replace('\n', ''):
                    error_parts.append(f"stderr: {stderr_content}")
                    has_real_error = True
        
        if result.stdout:
            filtered_stdout = result.stdout.strip()
            
            if '***' in filtered_stdout or '*' in filtered_stdout or 'theharvester' in tool_name_lower or 'harvester' in tool_name_lower:
                filtered_stdout = filter_theharvester_banner(filtered_stdout).strip()
            
            if is_dnsenum:
                filtered_stdout = filter_dnsenum_warnings(filtered_stdout).strip()
            
            if is_whois:
                filtered_stdout, is_informational = filter_whois_informational_messages(filtered_stdout)
                if is_informational and not has_real_error:
                    logger.info(f"WHOIS scan {scan_id} has informational message, treating as success")
                    self.scan_repo.update_status(scan, 'completed')
                    progress_output = filtered_stdout[:1000] if filtered_stdout else "Consulta WHOIS completada"
                    self.scan_repo.update_progress(scan, 100, progress_output)
                    
                    if workspace_id:
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source=scan_type.upper(),
                            level='INFO',
                            message=f"{scan_type} completado (mensaje informativo)",
                            metadata={'scan_id': scan_id, 'output_file': output_file, 'informational': True}
                        )
                    return
            
            if is_dnsenum:
                has_useful_info = any(keyword in filtered_stdout.lower() for keyword in [
                    "host's addresses", "name servers", "wildcards", "brute force",
                    "subdomains", "a record", "mx record", "ns record"
                ])
                
                if has_useful_info and not has_real_error:
                    logger.info(f"dnsenum scan {scan_id} completed with returncode {result.returncode} but has useful output")
                    self.scan_repo.update_status(scan, 'completed')
                    progress_output = filtered_stdout[:1000] if filtered_stdout else ""
                    self.scan_repo.update_progress(scan, 100, progress_output)
                    
                    if workspace_id:
                        log_to_workspace(
                            workspace_id=workspace_id,
                            source=scan_type.upper(),
                            level='INFO',
                            message=f"{scan_type} completado (returncode {result.returncode}, pero con output útil)",
                            metadata={'scan_id': scan_id, 'output_file': output_file, 'returncode': result.returncode}
                        )
                    return
            
            stdout_content = filtered_stdout[:500].strip()
            if stdout_content and stdout_content.replace(' ', '').replace('\t', '').replace('\n', ''):
                if not is_dnsenum or has_real_error:
                    error_parts.append(f"stdout: {stdout_content}")
        
        if not error_parts:
            error_msg = f"La herramienta '{tool_name}' falló con código de salida {result.returncode}. No se generó salida de error."
        else:
            error_msg = " | ".join(error_parts)
        
        self.scan_repo.update_status(scan, 'failed', error_msg)
        logger.error(f"Recon scan {scan_id} failed (returncode={result.returncode}): {error_msg}")
        
        if workspace_id:
            log_to_workspace(
                workspace_id=workspace_id,
                source=scan_type.upper(),
                level='ERROR',
                message=f"{scan_type} falló: {error_msg[:200]}",
                metadata={
                    'scan_id': scan_id, 
                    'error': error_msg,
                    'returncode': result.returncode,
                    'has_stderr': bool(result.stderr),
                    'has_stdout': bool(result.stdout)
                }
            )


