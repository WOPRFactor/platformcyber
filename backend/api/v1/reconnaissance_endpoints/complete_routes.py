"""
Complete Reconnaissance Routes
==============================

Endpoints para reconocimiento completo y WHOIS.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ReconnaissanceService

logger = logging.getLogger(__name__)

# Crear sub-blueprint
complete_bp = Blueprint('complete', __name__)

# Inicializar servicio
recon_service = ReconnaissanceService()


@complete_bp.route('/whois/preview', methods=['POST'])
@jwt_required()
def preview_whois():
    """Preview del comando WHOIS."""
    data = request.get_json()
    target = data.get('target')
    workspace_id = data.get('workspace_id')
    
    if not target or not workspace_id:
        return jsonify({'error': 'Target and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_whois_lookup(
            target=target,
            workspace_id=workspace_id
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_whois: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@complete_bp.route('/whois', methods=['POST'])
@jwt_required()
def whois_lookup():
    """
    Consulta WHOIS para dominio o IP.
    
    Body:
        {
            "target": "example.com",
            "workspace_id": 1
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    target = data.get('target')
    workspace_id = data.get('workspace_id')
    
    if not target or not workspace_id:
        return jsonify({'error': 'Target and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_whois_lookup(
            target=target,
            workspace_id=workspace_id,
            user_id=current_user_id
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in whois_lookup: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@complete_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_recon():
    """
    Ejecuta reconocimiento completo (todas las fases básicas).
    
    Body:
        {
            "target": "example.com",
            "workspace_id": 1,
            "include_advanced": false (opcional)
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    target = data.get('target')
    workspace_id = data.get('workspace_id')
    include_advanced = data.get('include_advanced', False)
    
    if not target or not workspace_id:
        return jsonify({'error': 'target and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_complete_recon(
            target=target,
            workspace_id=workspace_id,
            user_id=current_user_id,
            include_advanced=include_advanced
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in complete_recon: {e}")
        return jsonify({'error': 'Internal server error'}), 500





