"""
Active Directory Tasks
======================

Tareas asíncronas para operaciones de Active Directory.
"""

import logging
import subprocess
from datetime import datetime
from celery import Task
from celery_app import celery
from utils.validators import CommandSanitizer
from repositories import ScanRepository

logger = logging.getLogger(__name__)


class ADTask(Task):
    """Base class para tareas de AD."""
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 2}
    retry_backoff = True


@celery.task(
    bind=True,
    base=ADTask,
    name='tasks.ad.bloodhound_collection',
    time_limit=1800,  # 30 minutos
    soft_time_limit=1700
)
def bloodhound_collection_task(self, scan_id: int, domain: str, options: dict):
    """
    Ejecuta BloodHound collection en background.
    
    Args:
        scan_id: ID del scan
        domain: Dominio AD
        options: Credenciales y opciones
    """
    scan_repo = ScanRepository()
    
    try:
        scan = scan_repo.find_by_id(scan_id)
        scan_repo.update_status(scan, 'running')
        
        self.update_state(
            state='PROGRESS',
            meta={'scan_id': scan_id, 'progress': 0, 'status': 'Starting BloodHound collection...'}
        )
        
        command = ['bloodhound-python']
        
        if options.get('username') and options.get('password'):
            command.extend([
                '-u', options['username'],
                '-p', options['password'],
                '-d', domain
            ])
        
        if options.get('domain_controller'):
            command.extend(['-dc', options['domain_controller']])
        
        command.extend(['-c', 'All'])
        
        from utils.workspace_filesystem import PROJECT_TMP_DIR
        scans_dir = PROJECT_TMP_DIR / 'scans'
        scans_dir.mkdir(parents=True, exist_ok=True)
        output_dir = str(scans_dir / f'bloodhound_{scan_id}')
        command.extend(['--zip', '-o', output_dir])
        
        sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
        
        logger.info(f"Executing BloodHound collection task {scan_id}")
        
        result = subprocess.run(
            sanitized_cmd,
            capture_output=True,
            text=True,
            timeout=1700,
            env=CommandSanitizer.get_safe_env()
        )
        
        if result.returncode == 0 or 'Done' in result.stdout:
            scan_repo.update_status(scan, 'completed')
            scan_repo.update_progress(scan, 100, 'BloodHound collection completed')
            
            return {
                'scan_id': scan_id,
                'status': 'completed',
                'output_dir': output_dir,
                'completed_at': datetime.utcnow().isoformat()
            }
        else:
            error_msg = result.stderr or 'Unknown error'
            scan_repo.update_status(scan, 'failed', error_msg)
            raise Exception(f'BloodHound failed: {error_msg}')
            
    except Exception as e:
        logger.error(f"BloodHound task {scan_id} failed: {e}", exc_info=True)
        scan = scan_repo.find_by_id(scan_id)
        scan_repo.update_status(scan, 'failed', str(e))
        raise


@celery.task(
    bind=True,
    base=ADTask,
    name='tasks.ad.crackmapexec_scan',
    time_limit=900,  # 15 minutos
    soft_time_limit=800
)
def crackmapexec_scan_task(self, scan_id: int, target: str, options: dict):
    """
    Ejecuta CrackMapExec en background.
    
    Args:
        scan_id: ID del scan
        target: Target (IP o rango)
        options: Credenciales y opciones
    """
    scan_repo = ScanRepository()
    
    try:
        scan = scan_repo.find_by_id(scan_id)
        scan_repo.update_status(scan, 'running')
        
        self.update_state(
            state='PROGRESS',
            meta={'scan_id': scan_id, 'progress': 0, 'status': 'Starting CrackMapExec...'}
        )
        
        protocol = options.get('protocol', 'smb')
        command = ['crackmapexec', protocol, target]
        
        if options.get('username') and options.get('password'):
            command.extend([
                '-u', options['username'],
                '-p', options['password']
            ])
        
        if options.get('enumerate_shares'):
            command.append('--shares')
        
        if options.get('enumerate_users'):
            command.append('--users')
        
        from utils.workspace_filesystem import PROJECT_TMP_DIR
        scans_dir = PROJECT_TMP_DIR / 'scans'
        scans_dir.mkdir(parents=True, exist_ok=True)
        output_file = str(scans_dir / f'cme_{scan_id}.txt')
        
        sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
        
        logger.info(f"Executing CrackMapExec task {scan_id}")
        
        result = subprocess.run(
            sanitized_cmd,
            capture_output=True,
            text=True,
            timeout=800,
            env=CommandSanitizer.get_safe_env()
        )
        
        # Guardar output
        with open(output_file, 'w') as f:
            f.write(result.stdout)
        
        scan_repo.update_status(scan, 'completed')
        scan_repo.update_progress(scan, 100, 'CrackMapExec completed')
        
        return {
            'scan_id': scan_id,
            'status': 'completed',
            'output_file': output_file,
            'completed_at': datetime.utcnow().isoformat()
        }
            
    except Exception as e:
        logger.error(f"CrackMapExec task {scan_id} failed: {e}", exc_info=True)
        scan = scan_repo.find_by_id(scan_id)
        scan_repo.update_status(scan, 'failed', str(e))
        raise



