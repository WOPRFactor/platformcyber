"""
Scanning Tasks
==============

Tareas asíncronas para operaciones de scanning.
"""

import logging
import subprocess
from datetime import datetime
from celery import Task
from celery_app import celery
from utils.validators import CommandSanitizer
from repositories import ScanRepository

# WebSocket integration
from websockets.events import (
    emit_scan_progress,
    emit_notification,
    emit_scan_completed
)

logger = logging.getLogger(__name__)


class ScanTask(Task):
    """Base class para tareas de scanning con manejo de errores y WebSocket support."""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    
    def emit_ws_progress(self, scan_id: int, workspace_id: int, progress: int, message: str, data: dict = None):
        """Helper para emitir progreso vía WebSocket."""
        try:
            emit_scan_progress(
                scan_id=str(scan_id),
                workspace_id=workspace_id,
                progress=progress,
                status='running' if progress < 100 else 'completed',
                message=message,
                data=data
            )
        except Exception as e:
            logger.warning(f"Failed to emit WebSocket progress: {e}")


@celery.task(
    bind=True,
    base=ScanTask,
    name='tasks.scanning.nmap_scan',
    time_limit=1800,  # 30 minutos
    soft_time_limit=1700
)
def nmap_scan_task(self, scan_id: int, target: str, options: dict):
    """
    Ejecuta scan de Nmap en background.
    
    Args:
        scan_id: ID del scan en la base de datos
        target: Target a escanear
        options: Opciones del scan (debe incluir 'workspace_id')
    
    Returns:
        dict: Resultado del scan
    """
    from celery_app import get_flask_app
    
    app = get_flask_app()
    
    with app.app_context():
        scan_repo = ScanRepository()
        workspace_id = options.get('workspace_id', 1)  # Default workspace
        
        try:
            # Actualizar estado: running
            scan = scan_repo.find_by_id(scan_id)
            scan_repo.update_status(scan, 'running')
            
            # Actualizar progreso inicial
            self.update_state(
                state='PROGRESS',
                meta={
                    'scan_id': scan_id,
                    'progress': 0,
                    'status': 'Starting Nmap scan...'
                }
            )
            
            # Emitir vía WebSocket
            self.emit_ws_progress(scan_id, workspace_id, 0, 'Starting Nmap scan...', {'target': target})
            
            # Construir comando
            command = ['nmap']
            
            # Agregar opciones
            if options.get('scan_type') == 'quick':
                command.extend(['-T4', '-F'])
            elif options.get('scan_type') == 'intense':
                command.extend(['-T4', '-A', '-v'])
            elif options.get('scan_type') == 'stealth':
                command.extend(['-sS', '-T2'])
            else:
                command.extend(['-T4'])
            
            # Puertos
            if options.get('ports'):
                command.extend(['-p', options['ports']])
            
            # Output
            output_file = f'/tmp/scans/nmap_{scan_id}.xml'
            command.extend(['-oX', output_file])
            
            # Target
            command.append(target)
            
            # Sanitizar
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Executing Nmap task {scan_id}: {' '.join(sanitized_cmd)}")
            
            # Ejecutar
            self.update_state(
                state='PROGRESS',
                meta={
                    'scan_id': scan_id,
                    'progress': 25,
                    'status': 'Scanning in progress...'
                }
            )
            self.emit_ws_progress(scan_id, workspace_id, 25, 'Nmap scanning in progress...')
            
            start_time = datetime.utcnow()
            
            result = subprocess.run(
                sanitized_cmd,
                capture_output=True,
                text=True,
                timeout=1700,
                env=CommandSanitizer.get_safe_env()
            )
            
            # Actualizar progreso
            self.update_state(
                state='PROGRESS',
                meta={
                    'scan_id': scan_id,
                    'progress': 75,
                    'status': 'Parsing results...'
                }
            )
            self.emit_ws_progress(scan_id, workspace_id, 75, 'Parsing Nmap results...')
            
            # Verificar resultado
            if result.returncode == 0:
                scan_repo.update_status(scan, 'completed')
                scan_repo.update_progress(scan, 100, 'Scan completed')
                
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                # Emitir scan completado
                self.emit_ws_progress(scan_id, workspace_id, 100, 'Nmap scan completed')
                emit_scan_completed(
                    scan_id=str(scan_id),
                    workspace_id=workspace_id,
                    tool='nmap',
                    duration=duration,
                    findings_count=0,  # TODO: parsear output para contar findings
                    results={'output_file': output_file}
                )
                
                return {
                    'scan_id': scan_id,
                    'status': 'completed',
                    'output_file': output_file,
                    'stdout': result.stdout[:1000],
                    'duration': duration,
                    'completed_at': datetime.utcnow().isoformat()
                }
            else:
                error_msg = result.stderr or 'Unknown error'
                scan_repo.update_status(scan, 'failed', error_msg)
                
                # Emitir error vía WebSocket
                emit_notification(
                    workspace_id=workspace_id,
                    title='Nmap Scan Failed',
                    message=f'Scan {scan_id} failed: {error_msg}',
                    level='error'
                )
                
                raise Exception(f'Nmap failed: {error_msg}')
                
        except subprocess.TimeoutExpired:
            scan = scan_repo.find_by_id(scan_id)
            scan_repo.update_status(scan, 'failed', 'Scan timeout')
            raise
        
        except Exception as e:
            logger.error(f"Nmap task {scan_id} failed: {e}", exc_info=True)
            scan = scan_repo.find_by_id(scan_id)
            scan_repo.update_status(scan, 'failed', str(e))
            raise


@celery.task(
    bind=True,
    base=ScanTask,
    name='tasks.scanning.masscan_scan',
    time_limit=1200,  # 20 minutos
    soft_time_limit=1100
)
def masscan_scan_task(self, scan_id: int, target: str, options: dict):
    """
    Ejecuta scan de Masscan en background.
    
    Args:
        scan_id: ID del scan
        target: Target a escanear
        options: Opciones del scan
    """
    scan_repo = ScanRepository()
    
    try:
        scan = scan_repo.find_by_id(scan_id)
        scan_repo.update_status(scan, 'running')
        
        self.update_state(
            state='PROGRESS',
            meta={'scan_id': scan_id, 'progress': 0, 'status': 'Starting Masscan...'}
        )
        
        # Construir comando
        command = ['masscan', target]
        
        if options.get('ports'):
            command.extend(['-p', options['ports']])
        else:
            command.extend(['-p', '1-65535'])
        
        if options.get('rate'):
            command.extend(['--rate', str(options['rate'])])
        else:
            command.extend(['--rate', '1000'])
        
        output_file = f'/tmp/scans/masscan_{scan_id}.json'
        command.extend(['-oJ', output_file])
        
        sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
        
        logger.info(f"Executing Masscan task {scan_id}")
        
        self.update_state(
            state='PROGRESS',
            meta={'scan_id': scan_id, 'progress': 25, 'status': 'Scanning...'}
        )
        
        result = subprocess.run(
            sanitized_cmd,
            capture_output=True,
            text=True,
            timeout=1100,
            env=CommandSanitizer.get_safe_env()
        )
        
        if result.returncode == 0:
            scan_repo.update_status(scan, 'completed')
            scan_repo.update_progress(scan, 100, 'Masscan completed')
            
            return {
                'scan_id': scan_id,
                'status': 'completed',
                'output_file': output_file,
                'completed_at': datetime.utcnow().isoformat()
            }
        else:
            error_msg = result.stderr or 'Unknown error'
            scan_repo.update_status(scan, 'failed', error_msg)
            raise Exception(f'Masscan failed: {error_msg}')
            
    except Exception as e:
        logger.error(f"Masscan task {scan_id} failed: {e}", exc_info=True)
        scan = scan_repo.find_by_id(scan_id)
        scan_repo.update_status(scan, 'failed', str(e))
        raise


@celery.task(
    bind=True,
    base=ScanTask,
    name='tasks.scanning.nuclei_scan',
    time_limit=1800,
    soft_time_limit=1700
)
def nuclei_scan_task(self, scan_id: int, target: str, options: dict):
    """
    Ejecuta scan de Nuclei en background.
    
    Args:
        scan_id: ID del scan
        target: Target a escanear
        options: Opciones del scan
    """
    scan_repo = ScanRepository()
    
    try:
        scan = scan_repo.find_by_id(scan_id)
        scan_repo.update_status(scan, 'running')
        
        self.update_state(
            state='PROGRESS',
            meta={'scan_id': scan_id, 'progress': 0, 'status': 'Starting Nuclei...'}
        )
        
        # Construir comando
        command = ['nuclei', '-u', target]
        
        if options.get('templates'):
            command.extend(['-t', options['templates']])
        
        if options.get('severity'):
            command.extend(['-severity', ','.join(options['severity'])])
        
        output_file = f'/tmp/scans/nuclei_{scan_id}.json'
        command.extend(['-json', '-o', output_file])
        
        sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
        
        logger.info(f"Executing Nuclei task {scan_id}")
        
        self.update_state(
            state='PROGRESS',
            meta={'scan_id': scan_id, 'progress': 25, 'status': 'Scanning...'}
        )
        
        result = subprocess.run(
            sanitized_cmd,
            capture_output=True,
            text=True,
            timeout=1700,
            env=CommandSanitizer.get_safe_env()
        )
        
        # Nuclei retorna 0 incluso con vulns, así que no validamos returncode
        scan_repo.update_status(scan, 'completed')
        scan_repo.update_progress(scan, 100, 'Nuclei completed')
        
        return {
            'scan_id': scan_id,
            'status': 'completed',
            'output_file': output_file,
            'completed_at': datetime.utcnow().isoformat()
        }
            
    except Exception as e:
        logger.error(f"Nuclei task {scan_id} failed: {e}", exc_info=True)
        scan = scan_repo.find_by_id(scan_id)
        scan_repo.update_status(scan, 'failed', str(e))
        raise



