"""
Subdomain Enumeration Routes
============================

Endpoints para enumeración de subdominios.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ReconnaissanceService

logger = logging.getLogger(__name__)

# Crear sub-blueprint
subdomain_bp = Blueprint('subdomain', __name__)

# Inicializar servicio
recon_service = ReconnaissanceService()


@subdomain_bp.route('/subdomains', methods=['POST'])
@jwt_required()
def enumerate_subdomains():
    """
    Enumeración de subdominios.
    
    Body:
        {
            "domain": "example.com",
            "workspace_id": 1,
            "tool": "subfinder|amass|assetfinder"
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    tool = data.get('tool', 'subfinder')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_subdomain_enum(
            domain=domain,
            workspace_id=workspace_id,
            user_id=current_user_id,
            tool=tool
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in enumerate_subdomains: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@subdomain_bp.route('/crtsh', methods=['POST'])
@jwt_required()
def crtsh_lookup():
    """
    Busca subdominios usando Certificate Transparency (crt.sh).
    
    Body:
        {
            "domain": "example.com",
            "workspace_id": 1
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_crtsh_lookup(
            domain=domain,
            workspace_id=workspace_id,
            user_id=current_user_id
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in crtsh_lookup: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@subdomain_bp.route('/subdomains/preview', methods=['POST'])
@jwt_required()
def preview_subdomain_enum():
    """
    Preview del comando de enumeración de subdominios (sin ejecutar).
    
    Body:
        {
            "domain": "example.com",
            "workspace_id": 1,
            "tool": "subfinder|amass|assetfinder",
            "passive_only": true
        }
    """
    data = request.get_json()
    
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    tool = data.get('tool', 'subfinder')
    passive_only = data.get('passive_only', True)
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_subdomain_enum(
            domain=domain,
            workspace_id=workspace_id,
            tool=tool,
            passive_only=passive_only
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_subdomain_enum: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@subdomain_bp.route('/findomain/preview', methods=['POST'])
@jwt_required()
def preview_findomain():
    """Preview del comando Findomain."""
    data = request.get_json()
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    resolvers_file = data.get('resolvers_file')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_findomain_enum(
            domain=domain,
            workspace_id=workspace_id,
            resolvers_file=resolvers_file
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_findomain: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@subdomain_bp.route('/crtsh/preview', methods=['POST'])
@jwt_required()
def preview_crtsh():
    """Preview del comando crt.sh."""
    data = request.get_json()
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_crtsh_lookup(
            domain=domain,
            workspace_id=workspace_id
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_crtsh: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@subdomain_bp.route('/findomain', methods=['POST'])
@jwt_required()
def findomain_enum():
    """
    Enumeración de subdominios con Findomain.
    
    Body:
        {
            "domain": "example.com",
            "workspace_id": 1,
            "resolvers_file": "/path/to/resolvers.txt" (opcional)
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    resolvers_file = data.get('resolvers_file')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_findomain_enum(
            domain=domain,
            workspace_id=workspace_id,
            user_id=current_user_id,
            resolvers_file=resolvers_file
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in findomain_enum: {e}")
        return jsonify({'error': 'Internal server error'}), 500





