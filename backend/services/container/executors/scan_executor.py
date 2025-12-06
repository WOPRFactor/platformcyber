"""
Container Scan Executor
=======================

Ejecutor para comandos de container security scanning.
"""

import subprocess
import logging
import threading
from pathlib import Path
from typing import List

from repositories import ScanRepository
from utils.validators import CommandSanitizer
from utils.workspace_logger import log_to_workspace
from celery_app import get_flask_app

logger = logging.getLogger(__name__)


class ContainerScanExecutor:
    """
    Clase para ejecutar comandos de container security scanning en un hilo separado
    y manejar el logging y actualización de estado.
    """

    def __init__(self, scan_repository: ScanRepository):
        self.scan_repo = scan_repository

    def execute_scan_in_thread(
        self,
        scan_id: int,
        command: List[str],
        output_file: Path,
        tool: str,
        timeout: int = 600
    ) -> None:
        """Inicia la ejecución de un comando de escaneo en un hilo separado."""
        thread = threading.Thread(
            target=self._execute_scan_task,
            args=(scan_id, command, output_file, tool, timeout)
        )
        thread.daemon = True
        thread.start()

    def _execute_scan_task(
        self,
        scan_id: int,
        command: List[str],
        output_file: Path,
        tool: str,
        timeout: int
    ) -> None:
        """Tarea de ejecución de escaneo que se ejecuta en un hilo."""
        app = get_flask_app()
        with app.app_context():
            try:
                scan = self.scan_repo.find_by_id(scan_id)
                if not scan:
                    logger.error(f"Scan {scan_id} not found in _execute_scan_task")
                    return

                logger.info(f"Executing {tool} {scan_id}: {' '.join(command)}")

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=CommandSanitizer.get_safe_env()
                )

                # Guardar output si no existe
                if not output_file.exists() and result.stdout:
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, 'w') as f:
                        f.write(result.stdout)

                # Algunos tools retornan != 0 cuando encuentran vulnerabilidades
                # Validamos si el archivo de salida existe
                if result.returncode == 0 or output_file.exists():
                    self.scan_repo.update_status(scan, 'completed')
                    self.scan_repo.update_progress(scan, 100, result.stdout[:1000] if result.stdout else 'Completed')
                    logger.info(f"{tool} {scan_id} completed")
                    
                    # Log de éxito
                    log_to_workspace(
                        workspace_id=scan.workspace_id,
                        source=tool.upper(),
                        level='INFO',
                        message=f"{tool} completado exitosamente",
                        metadata={'scan_id': scan_id, 'status': 'completed'}
                    )
                else:
                    error_msg = result.stderr or "Unknown error"
                    self.scan_repo.update_status(scan, 'failed', error_msg)
                    logger.error(f"{tool} {scan_id} failed: {error_msg}")
                    
                    # Log de error
                    log_to_workspace(
                        workspace_id=scan.workspace_id,
                        source=tool.upper(),
                        level='ERROR',
                        message=f"{tool} falló: {error_msg}",
                        metadata={'scan_id': scan_id, 'status': 'failed', 'error': error_msg}
                    )

            except subprocess.TimeoutExpired:
                scan = self.scan_repo.find_by_id(scan_id)
                if scan:
                    self.scan_repo.update_status(scan, 'failed', f'Timeout ({timeout}s)')
                    # Log de timeout
                    log_to_workspace(
                        workspace_id=scan.workspace_id,
                        source=tool.upper(),
                        level='ERROR',
                        message=f"{tool} timeout después de {timeout}s",
                        metadata={'scan_id': scan_id, 'status': 'failed', 'timeout': timeout}
                    )
                logger.error(f"{tool} {scan_id} timeout")

            except Exception as e:
                scan = self.scan_repo.find_by_id(scan_id)
                if scan:
                    self.scan_repo.update_status(scan, 'failed', str(e))
                    # Log de excepción
                    log_to_workspace(
                        workspace_id=scan.workspace_id,
                        source=tool.upper(),
                        level='ERROR',
                        message=f"{tool} error: {str(e)}",
                        metadata={'scan_id': scan_id, 'status': 'failed', 'error': str(e)}
                    )
                logger.error(f"{tool} {scan_id} error: {e}", exc_info=True)

