"""
Celery Helpers
==============

Funciones helper para trabajar con Celery tasks.
"""

import logging
from typing import Optional, Dict, Any
from celery.result import AsyncResult
from celery_app import celery

logger = logging.getLogger(__name__)


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Obtiene el estado de una tarea de Celery.
    
    Args:
        task_id: ID de la tarea
    
    Returns:
        dict: Estado de la tarea
    """
    try:
        result = AsyncResult(task_id, app=celery)
        
        response = {
            'task_id': task_id,
            'state': result.state,
            'ready': result.ready(),
            'successful': result.successful() if result.ready() else None,
            'failed': result.failed() if result.ready() else None,
        }
        
        # Si está en progreso, incluir metadata
        if result.state == 'PROGRESS':
            response['meta'] = result.info
        
        # Si completó, incluir resultado
        elif result.ready():
            if result.successful():
                response['result'] = result.result
            elif result.failed():
                response['error'] = str(result.info)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting task status {task_id}: {e}")
        return {
            'task_id': task_id,
            'state': 'UNKNOWN',
            'error': str(e)
        }


def cancel_task(task_id: str) -> Dict[str, Any]:
    """
    Cancela una tarea de Celery.
    
    Args:
        task_id: ID de la tarea
    
    Returns:
        dict: Resultado de la cancelación
    """
    try:
        result = AsyncResult(task_id, app=celery)
        result.revoke(terminate=True)
        
        return {
            'task_id': task_id,
            'status': 'cancelled',
            'message': 'Task cancelled successfully'
        }
        
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {e}")
        return {
            'task_id': task_id,
            'status': 'error',
            'error': str(e)
        }


def get_active_tasks(queue: Optional[str] = None) -> Dict[str, Any]:
    """
    Obtiene las tareas activas en las colas de Celery.
    
    Args:
        queue: Nombre de la cola (opcional)
    
    Returns:
        dict: Tareas activas
    """
    try:
        inspect = celery.control.inspect()
        active = inspect.active()
        
        if not active:
            return {'active_tasks': [], 'total': 0}
        
        all_tasks = []
        for worker, tasks in active.items():
            for task in tasks:
                if queue is None or task.get('delivery_info', {}).get('routing_key') == queue:
                    all_tasks.append({
                        'task_id': task.get('id'),
                        'name': task.get('name'),
                        'worker': worker,
                        'args': task.get('args'),
                        'kwargs': task.get('kwargs'),
                    })
        
        return {
            'active_tasks': all_tasks,
            'total': len(all_tasks)
        }
        
    except Exception as e:
        logger.error(f"Error getting active tasks: {e}")
        return {
            'active_tasks': [],
            'total': 0,
            'error': str(e)
        }


def get_worker_stats() -> Dict[str, Any]:
    """
    Obtiene estadísticas de los workers de Celery.
    
    Returns:
        dict: Estadísticas de workers
    """
    try:
        inspect = celery.control.inspect()
        stats = inspect.stats()
        active = inspect.active()
        registered = inspect.registered()
        
        if not stats:
            return {
                'workers': [],
                'total_workers': 0,
                'status': 'no_workers'
            }
        
        workers_info = []
        for worker_name, worker_stats in stats.items():
            workers_info.append({
                'name': worker_name,
                'total_tasks': worker_stats.get('total', {}),
                'active_tasks': len(active.get(worker_name, [])) if active else 0,
                'registered_tasks': len(registered.get(worker_name, [])) if registered else 0,
                'pool': worker_stats.get('pool', {})
            })
        
        return {
            'workers': workers_info,
            'total_workers': len(workers_info),
            'status': 'healthy'
        }
        
    except Exception as e:
        logger.error(f"Error getting worker stats: {e}")
        return {
            'workers': [],
            'total_workers': 0,
            'status': 'error',
            'error': str(e)
        }


def purge_queue(queue: str) -> Dict[str, Any]:
    """
    Limpia una cola de Celery (elimina todas las tareas pendientes).
    
    Args:
        queue: Nombre de la cola
    
    Returns:
        dict: Resultado de la limpieza
    """
    try:
        purged_count = celery.control.purge()
        
        return {
            'queue': queue,
            'status': 'purged',
            'tasks_removed': purged_count
        }
        
    except Exception as e:
        logger.error(f"Error purging queue {queue}: {e}")
        return {
            'queue': queue,
            'status': 'error',
            'error': str(e)
        }



