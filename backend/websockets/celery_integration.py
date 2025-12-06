"""
Celery Integration with WebSockets
==================================

Integración de WebSockets con tareas Celery para notificaciones en tiempo real.
"""

from celery import Task
from typing import Dict, Any, Optional
import logging

from websockets.events import (
    emit_task_update,
    emit_scan_progress,
    emit_notification
)

logger = logging.getLogger(__name__)


class WebSocketTask(Task):
    """
    Base Task class con soporte para WebSocket events.
    
    Uso:
        @celery_app.task(base=WebSocketTask, bind=True)
        def my_task(self, workspace_id, ...):
            self.emit_progress(workspace_id, 50, "Processing...")
            # ... trabajo ...
            return result
    """
    
    def emit_progress(
        self,
        workspace_id: int,
        progress: int,
        message: str = "",
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Emitir progreso de la tarea.
        
        Args:
            workspace_id: ID del workspace
            progress: Porcentaje (0-100)
            message: Mensaje descriptivo
            data: Datos adicionales
        """
        emit_task_update(
            task_id=self.request.id,
            workspace_id=workspace_id,
            status='STARTED',
            progress=progress,
            result={'message': message, 'data': data} if data else {'message': message}
        )
    
    def emit_scan_update(
        self,
        scan_id: str,
        workspace_id: int,
        progress: int,
        status: str,
        message: str = "",
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Emitir actualización de scan.
        
        Args:
            scan_id: ID del scan
            workspace_id: ID del workspace
            progress: Porcentaje (0-100)
            status: Estado del scan
            message: Mensaje descriptivo
            data: Datos del scan
        """
        emit_scan_progress(
            scan_id=scan_id,
            workspace_id=workspace_id,
            progress=progress,
            status=status,
            message=message,
            data=data
        )
    
    def emit_notification(
        self,
        workspace_id: int,
        title: str,
        message: str,
        level: str = "info"
    ) -> None:
        """
        Emitir notificación.
        
        Args:
            workspace_id: ID del workspace
            title: Título
            message: Mensaje
            level: Nivel (info, success, warning, error)
        """
        emit_notification(
            workspace_id=workspace_id,
            title=title,
            message=message,
            level=level
        )
    
    def on_success(self, retval, task_id, args, kwargs):
        """Callback cuando la tarea se completa exitosamente."""
        workspace_id = kwargs.get('workspace_id') or (args[0] if args else None)
        
        if workspace_id:
            emit_task_update(
                task_id=task_id,
                workspace_id=workspace_id,
                status='SUCCESS',
                progress=100,
                result=retval
            )
            
            emit_notification(
                workspace_id=workspace_id,
                title="Task Completed",
                message=f"Task {self.name} completed successfully",
                level="success"
            )
        
        logger.info(f"✅ Task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Callback cuando la tarea falla."""
        workspace_id = kwargs.get('workspace_id') or (args[0] if args else None)
        
        if workspace_id:
            emit_task_update(
                task_id=task_id,
                workspace_id=workspace_id,
                status='FAILURE',
                error=str(exc)
            )
            
            emit_notification(
                workspace_id=workspace_id,
                title="Task Failed",
                message=f"Task {self.name} failed: {str(exc)}",
                level="error"
            )
        
        logger.error(f"❌ Task {task_id} failed: {exc}")
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Callback cuando la tarea se reintenta."""
        workspace_id = kwargs.get('workspace_id') or (args[0] if args else None)
        
        if workspace_id:
            emit_notification(
                workspace_id=workspace_id,
                title="Task Retrying",
                message=f"Task {self.name} is retrying after error: {str(exc)}",
                level="warning"
            )
        
        logger.warning(f"🔄 Task {task_id} retrying: {exc}")


def progress_callback(scan_id: str, workspace_id: int):
    """
    Genera un callback para emitir progreso durante scans largos.
    
    Uso:
        def long_running_scan(target, workspace_id):
            callback = progress_callback("scan_123", workspace_id)
            
            for i, item in enumerate(items):
                process(item)
                callback(i, len(items), f"Processing {item}")
    
    Args:
        scan_id: ID del scan
        workspace_id: ID del workspace
    
    Returns:
        Función callback
    """
    def callback(current: int, total: int, message: str = ""):
        progress = int((current / total) * 100) if total > 0 else 0
        
        emit_scan_progress(
            scan_id=scan_id,
            workspace_id=workspace_id,
            progress=progress,
            status='running',
            message=message,
            data={'current': current, 'total': total}
        )
    
    return callback


def emit_celery_task_state(task_id: str, workspace_id: int, state: Dict[str, Any]) -> None:
    """
    Emitir estado de tarea Celery.
    
    Args:
        task_id: ID de la tarea
        workspace_id: ID del workspace
        state: Estado de la tarea de Celery
    """
    status = state.get('status', 'UNKNOWN')
    
    emit_task_update(
        task_id=task_id,
        workspace_id=workspace_id,
        status=status,
        progress=state.get('current') if 'current' in state else None,
        result=state.get('result'),
        error=state.get('error')
    )


__all__ = [
    'WebSocketTask',
    'progress_callback',
    'emit_celery_task_state'
]

