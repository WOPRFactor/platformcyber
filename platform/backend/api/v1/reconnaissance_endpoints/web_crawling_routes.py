"""
Web Crawling Routes
===================

Endpoints para crawling web y descubrimiento de URLs.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ReconnaissanceService

logger = logging.getLogger(__name__)

# Crear sub-blueprint
webcrawl_bp = Blueprint('webcrawl', __name__)

# Inicializar servicio
recon_service = ReconnaissanceService()


@webcrawl_bp.route('/crawl/preview', methods=['POST'])
@jwt_required()
def preview_web_crawl():
    """Preview del comando de web crawling."""
    data = request.get_json()
    url = data.get('url')
    workspace_id = data.get('workspace_id')
    tool = data.get('tool', 'katana')
    depth = data.get('depth', 3)
    scope = data.get('scope', 'same-domain')
    
    if not url or not workspace_id:
        return jsonify({'error': 'URL and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_web_crawl(
            url=url,
            workspace_id=workspace_id,
            tool=tool,
            depth=depth,
            scope=scope
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_web_crawl: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@webcrawl_bp.route('/crawl', methods=['POST'])
@jwt_required()
def web_crawl():
    """
    Web crawling con Katana, GoSpider o Hakrawler.
    
    Body:
        {
            "url": "https://example.com",
            "workspace_id": 1,
            "tool": "katana|gospider|hakrawler" (opcional, default: katana),
            "depth": 3 (opcional)
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    url = data.get('url')
    workspace_id = data.get('workspace_id')
    tool = data.get('tool', 'katana')
    depth = data.get('depth', 3)
    
    if not url or not workspace_id:
        return jsonify({'error': 'URL and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_web_crawl(
            url=url,
            workspace_id=workspace_id,
            user_id=current_user_id,
            tool=tool,
            depth=depth
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in web_crawl: {e}")
        return jsonify({'error': 'Internal server error'}), 500





