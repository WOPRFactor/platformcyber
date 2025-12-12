"""
Secrets Detection Routes
========================

Endpoints para detección de secrets en repositorios.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ReconnaissanceService

logger = logging.getLogger(__name__)

# Crear sub-blueprint
secrets_bp = Blueprint('secrets', __name__)

# Inicializar servicio
recon_service = ReconnaissanceService()


@secrets_bp.route('/secrets/preview', methods=['POST'])
@jwt_required()
def preview_secrets_scan():
    """Preview del comando de secrets detection."""
    data = request.get_json()
    repo_url = data.get('repo_url')
    workspace_id = data.get('workspace_id')
    tool = data.get('tool', 'gitleaks')
    
    if not repo_url or not workspace_id:
        return jsonify({'error': 'repo_url and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_secrets_scan(
            repo_url=repo_url,
            workspace_id=workspace_id,
            tool=tool
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_secrets_scan: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@secrets_bp.route('/secrets', methods=['POST'])
@jwt_required()
def secrets_scan():
    """
    Busca secrets/credentials en repositorios.
    
    Body:
        {
            "repo_url": "https://github.com/user/repo",
            "workspace_id": 1,
            "tool": "gitleaks|trufflehog" (opcional, default: gitleaks)
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    repo_url = data.get('repo_url')
    workspace_id = data.get('workspace_id')
    tool = data.get('tool', 'gitleaks')
    
    if not repo_url or not workspace_id:
        return jsonify({'error': 'repo_url and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_secrets_scan(
            repo_url=repo_url,
            workspace_id=workspace_id,
            user_id=current_user_id,
            tool=tool
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in secrets_scan: {e}")
        return jsonify({'error': 'Internal server error'}), 500





