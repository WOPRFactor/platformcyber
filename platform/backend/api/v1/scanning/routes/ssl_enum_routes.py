"""
SSL/TLS Enumeration Routes
===========================

Rutas para análisis SSL/TLS.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ScanningService

logger = logging.getLogger(__name__)

scanning_service = ScanningService()


def register_routes(bp: Blueprint):
    """Registra las rutas de análisis SSL/TLS en el blueprint."""
    
    @bp.route('/enum/ssl/sslscan', methods=['POST'])
    @jwt_required()
    def sslscan_analysis():
        """Análisis SSL con sslscan."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.start_sslscan(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                port=data.get('port', 443),
                show_certificate=data.get('show_certificate', False)
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in sslscan: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/enum/ssl/sslyze', methods=['POST'])
    @jwt_required()
    def sslyze_analysis():
        """Análisis SSL/TLS con sslyze."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.start_sslyze(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                port=data.get('port', 443),
                regular=data.get('regular', True)
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in sslyze: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500


