"""
Celery Tasks - Brute Force
===========================

Tareas asíncronas para ataques de fuerza bruta.
"""

from celery import Task
from celery_app import celery
from services.brute_force_service import BruteForceService
from repositories import ScanRepository
import logging

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """Task base con callbacks."""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Callback en éxito."""
        logger.info(f"Task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Callback en fallo."""
        logger.error(f"Task {task_id} failed: {exc}")


@celery.task(
    bind=True,
    base=CallbackTask,
    name='tasks.brute_force.hydra_attack',
    max_retries=1,
    default_retry_delay=60
)
def hydra_attack_task(
    self,
    scan_id: int,
    target: str,
    service: str,
    username: str = None,
    username_list: str = None,
    password: str = None,
    password_list: str = None,
    port: int = None,
    options: dict = None
):
    """
    Task asíncrona para ataque Hydra.
    
    Args:
        scan_id: ID del scan
        target: Host objetivo
        service: Servicio
        username: Usuario único
        username_list: Archivo con usuarios
        password: Contraseña única
        password_list: Archivo con contraseñas
        port: Puerto
        options: Opciones adicionales
    
    Returns:
        Resultado del ataque
    """
    brute_force_service = BruteForceService()
    scan_repo = ScanRepository()
    
    try:
        # Obtener scan
        scan = scan_repo.find_by_id(scan_id)
        if not scan:
            raise ValueError(f"Scan {scan_id} not found")
        
        # Actualizar estado
        scan_repo.update_status(scan, 'running')
        scan_repo.update_progress(scan, 10, f'Starting Hydra attack against {target}:{service}')
        
        logger.info(f"[Task {self.request.id}] Starting Hydra attack: {target}:{service}")
        
        # Ejecutar ataque
        result = brute_force_service.hydra_attack(
            target=target,
            service=service,
            username=username,
            username_list=username_list,
            password=password,
            password_list=password_list,
            port=port,
            options=options or {}
        )
        
        # Actualizar scan según resultado
        if result['status'] == 'completed':
            scan_repo.update_status(scan, 'completed')
            scan_repo.update_progress(
                scan,
                100,
                f"Hydra completed. Found {len(result.get('valid_credentials', []))} valid credentials"
            )
            
            # Guardar resultados
            from models.scan_result import ScanResult
            from models import db
            
            scan_result = ScanResult(
                scan_id=scan_id,
                result_type='brute_force_credentials',
                data={
                    'target': target,
                    'service': service,
                    'port': port,
                    'valid_credentials': result.get('valid_credentials', []),
                    'attempts': result.get('attempts'),
                    'output_file': result.get('output_file')
                },
                severity='high' if result.get('valid_credentials') else 'info'
            )
            
            db.session.add(scan_result)
            db.session.commit()
            
            logger.info(
                f"[Task {self.request.id}] Hydra completed. "
                f"Found {len(result.get('valid_credentials', []))} credentials"
            )
            
        elif result['status'] == 'timeout':
            scan_repo.update_status(scan, 'failed')
            scan_repo.update_progress(scan, 0, 'Hydra timeout')
            logger.warning(f"[Task {self.request.id}] Hydra timeout")
            
        else:
            scan_repo.update_status(scan, 'failed')
            scan_repo.update_progress(
                scan,
                0,
                f"Hydra failed: {result.get('error', 'Unknown error')}"
            )
            logger.error(f"[Task {self.request.id}] Hydra failed: {result.get('error')}")
        
        return {
            'status': result['status'],
            'scan_id': scan_id,
            'target': target,
            'service': service,
            'valid_credentials': result.get('valid_credentials', []),
            'output_file': result.get('output_file')
        }
    
    except Exception as e:
        logger.error(f"[Task {self.request.id}] Error in Hydra task: {e}")
        
        # Actualizar scan
        scan = scan_repo.find_by_id(scan_id)
        if scan:
            scan_repo.update_status(scan, 'failed')
            scan_repo.update_progress(scan, 0, f'Error: {str(e)}')
        
        # Retry si es posible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        
        return {
            'status': 'error',
            'scan_id': scan_id,
            'error': str(e)
        }



