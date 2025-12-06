"""
Email Harvesting Routes
=======================

Endpoints para búsqueda de emails y enumeración de personas.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ReconnaissanceService

logger = logging.getLogger(__name__)

# Crear sub-blueprint
email_bp = Blueprint('email', __name__)

# Inicializar servicio
recon_service = ReconnaissanceService()


@email_bp.route('/emails/preview', methods=['POST'])
@jwt_required()
def preview_email_harvest():
    """Preview del comando theHarvester."""
    data = request.get_json()
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    sources = data.get('sources', 'bing,duckduckgo,hunter')
    limit = data.get('limit', 500)
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_email_harvest(
            domain=domain,
            workspace_id=workspace_id,
            sources=sources,
            limit=limit
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_email_harvest: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@email_bp.route('/emails', methods=['POST'])
@jwt_required()
def harvest_emails():
    """
    Búsqueda de emails con theHarvester.
    
    Body:
        {
            "domain": "example.com",
            "workspace_id": 1,
            "sources": "all|google|bing|linkedin"
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    sources = data.get('sources', 'all')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_email_harvest(
            domain=domain,
            workspace_id=workspace_id,
            user_id=current_user_id,
            sources=sources
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in harvest_emails: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@email_bp.route('/hunter-io/preview', methods=['POST'])
@jwt_required()
def preview_hunter_io():
    """Preview del comando Hunter.io."""
    data = request.get_json()
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    api_key = data.get('api_key')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_hunter_io_search(
            domain=domain,
            workspace_id=workspace_id,
            api_key=api_key
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_hunter_io: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@email_bp.route('/hunter-io', methods=['POST'])
@jwt_required()
def hunter_io():
    """
    Busca emails corporativos usando Hunter.io API.
    
    Body:
        {
            "domain": "example.com",
            "workspace_id": 1,
            "api_key": "hunter_io_api_key" (opcional, puede estar en env)
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    api_key = data.get('api_key')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_hunter_io_search(
            domain=domain,
            workspace_id=workspace_id,
            user_id=current_user_id,
            api_key=api_key
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in hunter_io: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@email_bp.route('/linkedin-enum/preview', methods=['POST'])
@jwt_required()
def preview_linkedin_enum():
    """Preview del comando LinkedIn enum."""
    data = request.get_json()
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    company_name = data.get('company_name')
    tool = data.get('tool', 'crosslinked')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_linkedin_enum(
            domain=domain,
            workspace_id=workspace_id,
            company_name=company_name,
            tool=tool
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_linkedin_enum: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@email_bp.route('/linkedin-enum', methods=['POST'])
@jwt_required()
def linkedin_enum():
    """
    Enumera empleados usando LinkedIn.
    
    Body:
        {
            "domain": "example.com",
            "workspace_id": 1,
            "company_name": "Example Company" (opcional),
            "tool": "crosslinked" | "linkedin2username" (default: "crosslinked")
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    company_name = data.get('company_name')
    tool = data.get('tool', 'crosslinked')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_linkedin_enum(
            domain=domain,
            workspace_id=workspace_id,
            user_id=current_user_id,
            company_name=company_name,
            tool=tool
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in linkedin_enum: {e}")
        return jsonify({'error': 'Internal server error'}), 500





