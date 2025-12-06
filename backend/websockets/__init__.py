"""
WebSocket Module for Real-Time Communication
============================================

Gestiona comunicación bidireccional en tiempo real usando Flask-SocketIO.

Eventos disponibles:
- scan_progress: Progreso de escaneos (nmap, nuclei, etc.)
- vuln_found: Vulnerabilidad detectada en tiempo real
- task_update: Actualización de tareas Celery
- notification: Notificaciones generales
- log_entry: Logs en tiempo real
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import logging

logger = logging.getLogger(__name__)

# Inicializar SocketIO (se configurará en app.py)
socketio = SocketIO(
    cors_allowed_origins="*",  # En producción, especificar dominios permitidos
    async_mode='threading',     # Usar 'gevent' o 'eventlet' en producción
    logger=True,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25
)


# ===================================
# CONNECTION HANDLERS
# ===================================

@socketio.on('connect')
def handle_connect():
    """Cliente conectado."""
    client_id = request.sid
    logger.info(f"✅ Cliente conectado: {client_id}")
    
    emit('connection_established', {
        'status': 'connected',
        'client_id': client_id,
        'message': 'Connected to Cybersecurity Platform WebSocket'
    })


@socketio.on('disconnect')
def handle_disconnect(*args, **kwargs):
    """Cliente desconectado."""
    client_id = request.sid
    logger.info(f"❌ Cliente desconectado: {client_id}")


# ===================================
# ROOM MANAGEMENT
# ===================================

@socketio.on('join_workspace')
def handle_join_workspace(data):
    """
    Unirse a una sala de workspace.
    
    Args:
        data: {'workspace_id': int}
    """
    workspace_id = data.get('workspace_id')
    if not workspace_id:
        emit('error', {'message': 'workspace_id is required'})
        return
    
    room = f"workspace_{workspace_id}"
    join_room(room)
    
    logger.info(f"👥 Cliente {request.sid} joined room: {room}")
    emit('joined_workspace', {
        'workspace_id': workspace_id,
        'room': room,
        'message': f'Joined workspace {workspace_id}'
    })


@socketio.on('leave_workspace')
def handle_leave_workspace(data):
    """
    Salir de una sala de workspace.
    
    Args:
        data: {'workspace_id': int}
    """
    workspace_id = data.get('workspace_id')
    if not workspace_id:
        emit('error', {'message': 'workspace_id is required'})
        return
    
    room = f"workspace_{workspace_id}"
    leave_room(room)
    
    logger.info(f"👋 Cliente {request.sid} left room: {room}")
    emit('left_workspace', {
        'workspace_id': workspace_id,
        'room': room,
        'message': f'Left workspace {workspace_id}'
    })


@socketio.on('join_scan')
def handle_join_scan(data):
    """
    Unirse a una sala de scan específico.
    
    Args:
        data: {'scan_id': str}
    """
    scan_id = data.get('scan_id')
    if not scan_id:
        emit('error', {'message': 'scan_id is required'})
        return
    
    room = f"scan_{scan_id}"
    join_room(room)
    
    logger.info(f"🔍 Cliente {request.sid} joined scan room: {room}")
    emit('joined_scan', {
        'scan_id': scan_id,
        'room': room,
        'message': f'Joined scan {scan_id}'
    })


# ===================================
# AUTHENTICATION (opcional)
# ===================================

@socketio.on('authenticate')
def handle_authenticate(data):
    """
    Autenticar cliente con JWT token.
    
    Args:
        data: {'token': str}
    """
    token = data.get('token')
    
    if not token:
        emit('auth_failed', {'message': 'Token is required'})
        return
    
    # TODO: Validar JWT token aquí
    # from flask_jwt_extended import decode_token
    
    # Por ahora, aceptar cualquier token (CAMBIAR EN PRODUCCIÓN)
    logger.info(f"🔐 Cliente {request.sid} authenticated")
    emit('authenticated', {
        'status': 'success',
        'message': 'Authentication successful'
    })


# ===================================
# PING/PONG para keep-alive
# ===================================

@socketio.on('ping')
def handle_ping():
    """Responder a ping del cliente."""
    emit('pong', {'timestamp': int(__import__('time').time())})


# ===================================
# ERROR HANDLER
# ===================================

@socketio.on_error_default
def default_error_handler(e):
    """Handler global de errores."""
    logger.error(f"❌ WebSocket error: {e}")
    emit('error', {
        'message': 'An error occurred',
        'details': str(e)
    })


__all__ = ['socketio']
