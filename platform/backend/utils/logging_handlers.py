"""
Logging Handlers for WebSocket
===============================

Handlers personalizados para emitir logs vía WebSocket en tiempo real.
"""

import logging
from typing import Optional
from websockets.events import emit_backend_log, emit_celery_log, emit_tool_log


class WebSocketLogHandler(logging.Handler):
    """
    Handler de logging que emite logs vía WebSocket.
    
    Usado para capturar logs de Flask y emitirlos en tiempo real.
    """
    
    def __init__(self, workspace_id: int, source: str = 'BACKEND'):
        super().__init__()
        self.workspace_id = workspace_id
        self.source = source.upper()
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emitir log vía WebSocket."""
        try:
            # Convertir nivel de logging a string
            level = self._get_level_string(record.levelno)
            
            # Obtener mensaje
            message = self.format(record)
            
            # Emitir según la fuente
            if self.source == 'BACKEND':
                emit_backend_log(
                    workspace_id=self.workspace_id,
                    level=level,
                    message=message
                )
            elif self.source == 'CELERY':
                emit_celery_log(
                    workspace_id=self.workspace_id,
                    level=level,
                    message=message,
                    task_id=getattr(record, 'task_id', None)
                )
            else:
                # Para herramientas (NIKTO, NMAP, etc.)
                emit_tool_log(
                    workspace_id=self.workspace_id,
                    tool=self.source,
                    level=level,
                    message=message,
                    command=getattr(record, 'command', None)
                )
        except Exception:
            # No fallar si hay error al emitir (evitar loops infinitos)
            self.handleError(record)
    
    def _get_level_string(self, levelno: int) -> str:
        """Convertir nivel numérico a string."""
        if levelno >= logging.ERROR:
            return 'ERROR'
        elif levelno >= logging.WARNING:
            return 'WARNING'
        elif levelno >= logging.INFO:
            return 'INFO'
        else:
            return 'DEBUG'


def setup_backend_logging_handler(workspace_id: int) -> WebSocketLogHandler:
    """
    Configurar handler de logging para backend Flask.
    
    Args:
        workspace_id: ID del workspace
        
    Returns:
        Handler configurado
    """
    handler = WebSocketLogHandler(workspace_id=workspace_id, source='BACKEND')
    handler.setLevel(logging.INFO)  # Solo INFO y superiores
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    return handler


def setup_celery_logging_handler(workspace_id: int) -> WebSocketLogHandler:
    """
    Configurar handler de logging para Celery workers.
    
    Args:
        workspace_id: ID del workspace
        
    Returns:
        Handler configurado
    """
    handler = WebSocketLogHandler(workspace_id=workspace_id, source='CELERY')
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    return handler


