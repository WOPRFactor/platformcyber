"""
Mobile Security Tasks
=====================

Tareas asíncronas para análisis de seguridad móvil.
"""

import logging
import subprocess
from datetime import datetime
from celery import Task
from celery_app import celery
from utils.validators import CommandSanitizer
from repositories import ScanRepository

logger = logging.getLogger(__name__)


class MobileTask(Task):
    """Base class para tareas de mobile security."""
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 2}
    retry_backoff = True


@celery.task(
    bind=True,
    base=MobileTask,
    name='tasks.mobile.mobsf_analysis',
    time_limit=1800,  # 30 minutos
    soft_time_limit=1700
)
def mobsf_analysis_task(self, scan_id: int, apk_path: str, options: dict):
    """
    Ejecuta análisis de MobSF en background.
    
    Args:
        scan_id: ID del scan
        apk_path: Path al APK
        options: Opciones de análisis
    """
    scan_repo = ScanRepository()
    
    try:
        scan = scan_repo.find_by_id(scan_id)
        scan_repo.update_status(scan, 'running')
        
        self.update_state(
            state='PROGRESS',
            meta={'scan_id': scan_id, 'progress': 0, 'status': 'Starting MobSF analysis...'}
        )
        
        analysis_type = options.get('analysis_type', 'static')
        from utils.workspace_filesystem import PROJECT_TMP_DIR
        scans_dir = PROJECT_TMP_DIR / 'scans'
        scans_dir.mkdir(parents=True, exist_ok=True)
        output_file = str(scans_dir / f'mobsf_{scan_id}.json')
        
        # MobSF command (simulado, en producción usarías la API)
        command = ['mobsf', 'analyze', apk_path, '--output', output_file]
        
        if analysis_type == 'dynamic':
            command.append('--dynamic')
        
        sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
        
        logger.info(f"Executing MobSF analysis task {scan_id}")
        
        self.update_state(
            state='PROGRESS',
            meta={'scan_id': scan_id, 'progress': 50, 'status': 'Analyzing APK...'}
        )
        
        result = subprocess.run(
            sanitized_cmd,
            capture_output=True,
            text=True,
            timeout=1700,
            env=CommandSanitizer.get_safe_env()
        )
        
        scan_repo.update_status(scan, 'completed')
        scan_repo.update_progress(scan, 100, 'MobSF analysis completed')
        
        return {
            'scan_id': scan_id,
            'status': 'completed',
            'output_file': output_file,
            'completed_at': datetime.utcnow().isoformat()
        }
            
    except Exception as e:
        logger.error(f"MobSF task {scan_id} failed: {e}", exc_info=True)
        scan = scan_repo.find_by_id(scan_id)
        scan_repo.update_status(scan, 'failed', str(e))
        raise



