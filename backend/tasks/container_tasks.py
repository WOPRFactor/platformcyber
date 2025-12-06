"""
Container Security Tasks
========================

Tareas asíncronas para seguridad de contenedores.
"""

import logging
import subprocess
from datetime import datetime
from celery import Task
from celery_app import celery
from utils.validators import CommandSanitizer
from repositories import ScanRepository

logger = logging.getLogger(__name__)


class ContainerTask(Task):
    """Base class para tareas de container security."""
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 2}
    retry_backoff = True


@celery.task(
    bind=True,
    base=ContainerTask,
    name='tasks.container.trivy_scan',
    time_limit=900,  # 15 minutos
    soft_time_limit=800
)
def trivy_scan_task(self, scan_id: int, image: str, options: dict):
    """
    Ejecuta scan de Trivy en background.
    
    Args:
        scan_id: ID del scan
        image: Imagen Docker
        options: Opciones de Trivy
    """
    scan_repo = ScanRepository()
    
    try:
        scan = scan_repo.find_by_id(scan_id)
        scan_repo.update_status(scan, 'running')
        
        self.update_state(
            state='PROGRESS',
            meta={'scan_id': scan_id, 'progress': 0, 'status': 'Starting Trivy scan...'}
        )
        
        from utils.workspace_filesystem import PROJECT_TMP_DIR
        scans_dir = PROJECT_TMP_DIR / 'scans'
        scans_dir.mkdir(parents=True, exist_ok=True)
        output_file = str(scans_dir / f'trivy_{scan_id}.json')
        
        command = [
            'trivy', 'image',
            '--format', 'json',
            '--output', output_file
        ]
        
        if options.get('severity'):
            command.extend(['--severity', ','.join(options['severity'])])
        
        command.append(image)
        
        sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
        
        logger.info(f"Executing Trivy scan task {scan_id}")
        
        self.update_state(
            state='PROGRESS',
            meta={'scan_id': scan_id, 'progress': 50, 'status': 'Scanning image...'}
        )
        
        result = subprocess.run(
            sanitized_cmd,
            capture_output=True,
            text=True,
            timeout=800,
            env=CommandSanitizer.get_safe_env()
        )
        
        scan_repo.update_status(scan, 'completed')
        scan_repo.update_progress(scan, 100, 'Trivy scan completed')
        
        return {
            'scan_id': scan_id,
            'status': 'completed',
            'output_file': output_file,
            'completed_at': datetime.utcnow().isoformat()
        }
            
    except Exception as e:
        logger.error(f"Trivy task {scan_id} failed: {e}", exc_info=True)
        scan = scan_repo.find_by_id(scan_id)
        scan_repo.update_status(scan, 'failed', str(e))
        raise



