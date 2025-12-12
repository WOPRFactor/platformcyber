"""
Workspace Logger
===============

Función centralizada para logging con persistencia y WebSocket.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from models import db, WorkspaceLog
from utils.message_sanitizer import MessageSanitizer
from websockets.events import emit_backend_log, emit_celery_log, emit_tool_log

logger = logging.getLogger(__name__)


def log_to_workspace(
    workspace_id: int,
    source: str,
    level: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None,
    task_id: Optional[str] = None,
    emit_websocket: bool = True
) -> WorkspaceLog:
    """
    Registra log en workspace con persistencia y emisión WebSocket.
    
    Esta función:
    1. Sanitiza el mensaje (remueve credenciales/tokens)
    2. Emite vía WebSocket (tiempo real)
    3. Guarda en BD (persistencia)
    
    Args:
        workspace_id: ID del workspace
        source: Fuente del log (BACKEND, CELERY, NIKTO, NMAP, etc.)
        level: Nivel (DEBUG, INFO, WARNING, ERROR)
        message: Mensaje del log
        metadata: Metadatos adicionales (opcional)
        task_id: ID de tarea Celery (opcional)
        emit_websocket: Si emitir vía WebSocket (default: True)
        
    Returns:
        WorkspaceLog: Log creado en BD
    """
    try:
        # 1. Sanitizar mensaje
        sanitized_message = MessageSanitizer.sanitize(message)
        
        # 2. Sanitizar metadata si existe
        sanitized_metadata = None
        if metadata:
            sanitized_metadata = MessageSanitizer.sanitize_dict(metadata)
        
        # 3. Emitir vía WebSocket (tiempo real)
        if emit_websocket:
            try:
                source_upper = source.upper()
                if source_upper == 'BACKEND':
                    emit_backend_log(
                        workspace_id=workspace_id,
                        level=level,
                        message=sanitized_message
                    )
                elif source_upper == 'CELERY':
                    emit_celery_log(
                        workspace_id=workspace_id,
                        level=level,
                        message=sanitized_message,
                        task_id=task_id
                    )
                else:
                    # Herramientas (NIKTO, NMAP, etc.)
                    emit_tool_log(
                        workspace_id=workspace_id,
                        tool=source,
                        level=level,
                        message=sanitized_message,
                        command=metadata.get('command') if metadata else None
                    )
            except Exception as e:
                # No fallar si WebSocket no está disponible
                logger.warning(f"Failed to emit WebSocket log: {e}")
        
        # 4. Guardar en BD (persistencia)
        log_entry = WorkspaceLog(
            workspace_id=workspace_id,
            source=source.upper(),
            level=level.upper(),
            message=sanitized_message,
            timestamp=datetime.utcnow(),
            task_id=task_id
        )
        # Establecer metadata usando el método set_metadata (convierte dict a JSON)
        if sanitized_metadata:
            log_entry.set_metadata(sanitized_metadata)
        
        db.session.add(log_entry)
        db.session.commit()
        
        return log_entry
        
    except Exception as e:
        # Log error pero no fallar la aplicación
        logger.error(f"Error logging to workspace {workspace_id}: {e}", exc_info=True)
        db.session.rollback()
        # Retornar objeto dummy para no romper el flujo
        return None

