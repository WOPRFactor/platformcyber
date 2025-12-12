"""
Google Dorks Routes
===================

Endpoints para búsqueda con Google Dorks.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ReconnaissanceService

logger = logging.getLogger(__name__)

# Crear sub-blueprint
googledorks_bp = Blueprint('googledorks', __name__)

# Inicializar servicio
recon_service = ReconnaissanceService()


@googledorks_bp.route('/google-dorks/preview', methods=['POST'])
@jwt_required()
def preview_google_dorks():
    """Preview del comando Google Dorks."""
    data = request.get_json()
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    dork_query = data.get('dork_query')
    tool = data.get('tool', 'manual')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_google_dorks(
            domain=domain,
            workspace_id=workspace_id,
            dork_query=dork_query,
            tool=tool
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_google_dorks: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@googledorks_bp.route('/google-dorks', methods=['POST'])
@jwt_required()
def google_dorks():
    """
    Ejecuta Google Dorks manuales o automatizados.
    
    Body:
        {
            "domain": "example.com",
            "workspace_id": 1,
            "dork_query": "site:example.com filetype:pdf" (opcional, para modo manual),
            "tool": "manual" | "goofuzz" | "pagodo" | "dorkscanner" (default: "manual")
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    dork_query = data.get('dork_query')
    tool = data.get('tool', 'manual')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_google_dorks(
            domain=domain,
            workspace_id=workspace_id,
            user_id=current_user_id,
            dork_query=dork_query,
            tool=tool
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in google_dorks: {e}")
        return jsonify({'error': 'Internal server error'}), 500





