"""
WebSocket API Endpoints
=======================

Endpoints REST para gestión y monitoreo de WebSocket.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from websockets.events import (
    emit_notification,
    emit_scan_progress
)

logger = logging.getLogger(__name__)

websocket_bp = Blueprint('websocket', __name__)


@websocket_bp.route('/status', methods=['GET'])
@jwt_required()
def get_websocket_status():
    """
    Obtener estado del servidor WebSocket.
    
    GET /api/v1/websocket/status
    
    Response:
        {
            "status": "active",
            "connected_clients": 5,
            "active_rooms": 3,
            "uptime": 3600
        }
    """
    try:
        from websockets import socketio
        
        # TODO: Implementar contadores reales
        # Por ahora retornar info básica
        
        return jsonify({
            'status': 'active',
            'server': {
                'async_mode': socketio.async_mode,
                'ping_timeout': socketio.server.ping_timeout,
                'ping_interval': socketio.server.ping_interval
            },
            'message': 'WebSocket server is running'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting WebSocket status: {e}")
        return jsonify({'error': str(e)}), 500


@websocket_bp.route('/test/notification', methods=['POST'])
@jwt_required()
def test_notification():
    """
    Enviar notificación de prueba (solo desarrollo).
    
    POST /api/v1/websocket/test/notification
    Body:
        {
            "workspace_id": 1,
            "title": "Test Notification",
            "message": "This is a test",
            "level": "info"
        }
    """
    try:
        data = request.get_json()
        
        workspace_id = data.get('workspace_id')
        title = data.get('title', 'Test Notification')
        message = data.get('message', 'This is a test notification')
        level = data.get('level', 'info')
        
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        emit_notification(
            workspace_id=workspace_id,
            title=title,
            message=message,
            level=level
        )
        
        logger.info(f"Test notification sent to workspace {workspace_id}")
        
        return jsonify({
            'success': True,
            'message': 'Notification sent successfully',
            'data': {
                'workspace_id': workspace_id,
                'title': title,
                'message': message,
                'level': level
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        return jsonify({'error': str(e)}), 500


@websocket_bp.route('/test/scan-progress', methods=['POST'])
@jwt_required()
def test_scan_progress():
    """
    Enviar progreso de scan de prueba (solo desarrollo).
    
    POST /api/v1/websocket/test/scan-progress
    Body:
        {
            "scan_id": "test-123",
            "workspace_id": 1,
            "progress": 50,
            "message": "Scanning..."
        }
    """
    try:
        data = request.get_json()
        
        scan_id = data.get('scan_id')
        workspace_id = data.get('workspace_id')
        progress = data.get('progress', 0)
        message = data.get('message', 'Processing...')
        
        if not scan_id or not workspace_id:
            return jsonify({'error': 'scan_id and workspace_id are required'}), 400
        
        emit_scan_progress(
            scan_id=scan_id,
            workspace_id=workspace_id,
            progress=progress,
            status='running' if progress < 100 else 'completed',
            message=message
        )
        
        logger.info(f"Test scan progress sent: {scan_id} - {progress}%")
        
        return jsonify({
            'success': True,
            'message': 'Scan progress sent successfully',
            'data': {
                'scan_id': scan_id,
                'workspace_id': workspace_id,
                'progress': progress,
                'message': message
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error sending test scan progress: {e}")
        return jsonify({'error': str(e)}), 500


@websocket_bp.route('/rooms', methods=['GET'])
@jwt_required()
def get_active_rooms():
    """
    Listar salas activas (workspaces, scans).
    
    GET /api/v1/websocket/rooms
    
    Response:
        {
            "rooms": ["workspace_1", "scan_abc123"],
            "count": 2
        }
    """
    try:
        # TODO: Implementar tracking real de salas activas
        
        return jsonify({
            'message': 'Room tracking not yet implemented',
            'rooms': [],
            'count': 0
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting active rooms: {e}")
        return jsonify({'error': str(e)}), 500


__all__ = ['websocket_bp']

