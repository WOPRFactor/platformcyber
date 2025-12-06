"""
RustScan Routes
===============

Rutas para escaneos con RustScan.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ScanningService

logger = logging.getLogger(__name__)

scanning_service = ScanningService()


def register_routes(bp: Blueprint):
    """Registra las rutas de RustScan en el blueprint."""
    
    @bp.route('/rustscan/preview', methods=['POST'])
    @jwt_required()
    def preview_rustscan():
        """Preview del comando RustScan."""
        data = request.get_json() or {}
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        batch_size = data.get('batch_size', 4000)
        timeout = data.get('timeout', 1500)
        ulimit = data.get('ulimit', 5000)
        
        if not target or not workspace_id:
            return jsonify({'error': 'Target and workspace_id are required'}), 400
        
        try:
            result = scanning_service.preview_rustscan(
                target=target,
                workspace_id=workspace_id,
                batch_size=batch_size,
                timeout=timeout,
                ulimit=ulimit
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_rustscan: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/rustscan', methods=['POST'])
    @jwt_required()
    def rustscan_scan():
        """Inicia un escaneo RustScan (ultra-rápido)."""
        data = request.get_json() or {}
        current_user_id = get_jwt_identity()
        
        logger.info(f"📡 POST /scanning/rustscan - User: {current_user_id}, Data: {data}")
        
        target = data.get('target')
        workspace_id = data.get('workspace_id') or request.args.get('workspace_id', type=int)
        
        if not target:
            return jsonify({'error': 'Target is required'}), 400
        
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        try:
            workspace_id = int(workspace_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'workspace_id must be a number'}), 400
        
        batch_size = data.get('batch_size', 4000)
        timeout = data.get('timeout', 1500)
        ulimit = data.get('ulimit', 5000)
        
        try:
            result = scanning_service.start_rustscan(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                batch_size=batch_size,
                timeout=timeout,
                ulimit=ulimit
            )
            return jsonify(result), 201
        except ValueError as e:
            logger.error(f"ValueError in rustscan_scan: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in rustscan_scan: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


