"""
Naabu Routes
============

Rutas para escaneos con Naabu.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ScanningService

logger = logging.getLogger(__name__)

scanning_service = ScanningService()


def register_routes(bp: Blueprint):
    """Registra las rutas de Naabu en el blueprint."""
    
    @bp.route('/naabu/preview', methods=['POST'])
    @jwt_required()
    def preview_naabu():
        """Preview del comando Naabu."""
        data = request.get_json() or {}
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        top_ports = data.get('top_ports')
        rate = data.get('rate', 1000)
        verify = data.get('verify', True)
        
        if not target or not workspace_id:
            return jsonify({'error': 'Target and workspace_id are required'}), 400
        
        try:
            result = scanning_service.preview_naabu(
                target=target,
                workspace_id=workspace_id,
                top_ports=top_ports,
                rate=rate,
                verify=verify
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_naabu: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/naabu', methods=['POST'])
    @jwt_required()
    def naabu_scan():
        """Inicia un escaneo Naabu (port discovery rápido)."""
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        
        if not target or not workspace_id:
            return jsonify({'error': 'Target and workspace_id are required'}), 400
        
        top_ports = data.get('top_ports')
        rate = data.get('rate', 1000)
        verify = data.get('verify', True)
        
        try:
            result = scanning_service.start_naabu(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                top_ports=top_ports,
                rate=rate,
                verify=verify
            )
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in naabu_scan: {e}")
            return jsonify({'error': 'Internal server error'}), 500


