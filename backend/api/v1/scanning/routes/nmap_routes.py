"""
Nmap Routes
===========

Rutas para escaneos con Nmap.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ScanningService

logger = logging.getLogger(__name__)

scanning_service = ScanningService()


def register_routes(bp: Blueprint):
    """Registra las rutas de Nmap en el blueprint."""
    
    @bp.route('/nmap/preview', methods=['POST'])
    @jwt_required()
    def preview_nmap_scan():
        """Preview del comando Nmap."""
        data = request.get_json() or {}
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        scan_type = data.get('scan_type', 'comprehensive')
        ports = data.get('ports')
        scripts = data.get('scripts')
        os_detection = data.get('os_detection', False)
        version_detection = data.get('version_detection', False)
        
        if not target or not workspace_id:
            return jsonify({'error': 'Target and workspace_id are required'}), 400
        
        try:
            result = scanning_service.preview_nmap_scan(
                target=target,
                scan_type=scan_type,
                workspace_id=workspace_id,
                ports=ports,
                scripts=scripts,
                os_detection=os_detection,
                version_detection=version_detection
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_nmap_scan: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/nmap', methods=['POST'])
    @jwt_required()
    def nmap_scan():
        """Inicia un escaneo Nmap."""
        data = request.get_json() or {}
        current_user_id = get_jwt_identity()
        
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        
        if not target or not workspace_id:
            return jsonify({'error': 'Target and workspace_id are required'}), 400
        
        scan_type = data.get('scan_type', 'comprehensive')
        ports = data.get('ports')
        scripts = data.get('scripts')
        os_detection = data.get('os_detection', False)
        version_detection = data.get('version_detection', False)
        
        try:
            result = scanning_service.start_nmap_scan(
                target=target,
                scan_type=scan_type,
                workspace_id=workspace_id,
                user_id=current_user_id,
                ports=ports,
                scripts=scripts,
                os_detection=os_detection,
                version_detection=version_detection
            )
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in nmap_scan endpoint: {e}")
            return jsonify({'error': 'Internal server error'}), 500


