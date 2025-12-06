"""
Masscan Routes
==============

Rutas para escaneos con Masscan.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ScanningService

logger = logging.getLogger(__name__)

scanning_service = ScanningService()


def register_routes(bp: Blueprint):
    """Registra las rutas de Masscan en el blueprint."""
    
    @bp.route('/masscan/preview', methods=['POST'])
    @jwt_required()
    def preview_masscan():
        """Preview del comando Masscan."""
        data = request.get_json() or {}
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        ports = data.get('ports', '1-65535')
        rate = data.get('rate', 1000)
        environment = data.get('environment', 'internal')
        
        if not target or not workspace_id:
            return jsonify({'error': 'Target and workspace_id are required'}), 400
        
        try:
            result = scanning_service.preview_masscan(
                target=target,
                ports=ports,
                workspace_id=workspace_id,
                rate=rate,
                environment=environment
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_masscan: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/masscan', methods=['POST'])
    @jwt_required()
    def masscan_scan():
        """Inicia un escaneo Masscan (masivo)."""
        data = request.get_json() or {}
        current_user_id = get_jwt_identity()
        
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        ports = data.get('ports', '1-65535')
        rate = data.get('rate', 1000)
        environment = data.get('environment', 'internal')
        
        if not target or not workspace_id:
            return jsonify({'error': 'Target and workspace_id are required'}), 400
        
        try:
            result = scanning_service.start_masscan(
                target=target,
                ports=ports,
                workspace_id=workspace_id,
                user_id=current_user_id,
                rate=rate,
                environment=environment
            )
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in masscan_scan: {e}")
            return jsonify({'error': 'Internal server error'}), 500


