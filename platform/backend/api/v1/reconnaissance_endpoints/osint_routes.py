"""
OSINT Tools Routes
==================

Endpoints para herramientas OSINT.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ReconnaissanceService

logger = logging.getLogger(__name__)

# Crear sub-blueprint
osint_bp = Blueprint('osint', __name__)

# Inicializar servicio
recon_service = ReconnaissanceService()


@osint_bp.route('/shodan/preview', methods=['POST'])
@jwt_required()
def preview_shodan():
    """Preview del comando Shodan."""
    data = request.get_json()
    query = data.get('query')
    workspace_id = data.get('workspace_id')
    api_key = data.get('api_key')
    
    if not query or not workspace_id:
        return jsonify({'error': 'query and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_shodan_search(
            query=query,
            workspace_id=workspace_id,
            api_key=api_key
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_shodan: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@osint_bp.route('/censys/preview', methods=['POST'])
@jwt_required()
def preview_censys():
    """Preview del comando Censys."""
    data = request.get_json()
    query = data.get('query')
    workspace_id = data.get('workspace_id')
    index_type = data.get('index_type', 'hosts')
    api_id = data.get('api_id')
    api_secret = data.get('api_secret')
    
    if not query or not workspace_id:
        return jsonify({'error': 'query and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_censys_search(
            query=query,
            workspace_id=workspace_id,
            index_type=index_type,
            api_id=api_id,
            api_secret=api_secret
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_censys: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@osint_bp.route('/wayback/preview', methods=['POST'])
@jwt_required()
def preview_wayback():
    """Preview del comando waybackurls."""
    data = request.get_json()
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_wayback_urls(
            domain=domain,
            workspace_id=workspace_id
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_wayback: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@osint_bp.route('/shodan', methods=['POST'])
@jwt_required()
def shodan_search():
    """
    Búsqueda en Shodan.
    
    Body:
        {
            "query": "org:Example OR hostname:example.com",
            "workspace_id": 1,
            "api_key": "shodan_api_key" (opcional, puede estar en env)
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    query = data.get('query')
    workspace_id = data.get('workspace_id')
    api_key = data.get('api_key')
    
    if not query or not workspace_id:
        return jsonify({'error': 'query and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_shodan_search(
            query=query,
            workspace_id=workspace_id,
            user_id=current_user_id,
            api_key=api_key
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in shodan_search: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@osint_bp.route('/censys', methods=['POST'])
@jwt_required()
def censys_search():
    """
    Busca información en Censys.
    
    Body:
        {
            "query": "example.com",
            "workspace_id": 1,
            "index_type": "hosts|certificates" (opcional, default: hosts),
            "api_id": "censys_api_id" (opcional, puede estar en env),
            "api_secret": "censys_api_secret" (opcional, puede estar en env)
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    query = data.get('query')
    workspace_id = data.get('workspace_id')
    index_type = data.get('index_type', 'hosts')
    api_id = data.get('api_id')
    api_secret = data.get('api_secret')
    
    if not query or not workspace_id:
        return jsonify({'error': 'query and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_censys_search(
            query=query,
            workspace_id=workspace_id,
            user_id=current_user_id,
            index_type=index_type,
            api_id=api_id,
            api_secret=api_secret
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in censys_search: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@osint_bp.route('/wayback', methods=['POST'])
@jwt_required()
def wayback_urls():
    """
    Obtiene URLs históricas de Wayback Machine.
    
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
        result = recon_service.start_wayback_urls(
            domain=domain,
            workspace_id=workspace_id,
            user_id=current_user_id
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in wayback_urls: {e}")
        return jsonify({'error': 'Internal server error'}), 500





