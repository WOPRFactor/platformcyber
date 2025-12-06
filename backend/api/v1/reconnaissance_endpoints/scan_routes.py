"""
Scan Management Routes
======================

Endpoints para gestión y consulta de escaneos.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, verify_jwt_in_request
import logging

from services import ReconnaissanceService

logger = logging.getLogger(__name__)

# Crear sub-blueprint
scan_bp = Blueprint('scan', __name__)

# Inicializar servicio
recon_service = ReconnaissanceService()


@scan_bp.route('/scans/<int:scan_id>', methods=['GET', 'OPTIONS'])
def get_scan_status(scan_id):
    """Obtiene el estado de un escaneo de reconocimiento.
    
    Flask-CORS maneja automáticamente los headers CORS.
    Este endpoint está excluido del rate limiting (ver app.py init_extensions).
    """
    # Flask-CORS maneja OPTIONS automáticamente
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        return response, 200
    
    # Para GET, requerir autenticación
    try:
        verify_jwt_in_request()
    except Exception as auth_error:
        logger.warning(f"Authentication error in get_scan_status: {auth_error}")
        response = jsonify({'error': 'Unauthorized', 'message': 'Authentication required'})
        return response, 401
    
    try:
        from repositories.scan_repository import ScanRepository
        scan_repo = ScanRepository()
        scan = scan_repo.find_by_id(scan_id)
        
        if not scan:
            response = jsonify({'error': f'Scan {scan_id} not found'})
            return response, 404
        
        response = jsonify({
            'scan_id': scan.id,
            'status': scan.status,
            'progress': scan.progress,
            'target': scan.target,
            'scan_type': scan.scan_type,
            'tool': scan.options.get('tool') if scan.options else None,
            'started_at': scan.started_at.isoformat() if scan.started_at else None,
            'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
            'error': scan.error
        })
        return response, 200
        
    except ValueError as e:
        response = jsonify({'error': str(e)})
        return response, 404
    except Exception as e:
        logger.error(f"Error getting scan status: {e}", exc_info=True)
        response = jsonify({'error': 'Internal server error'})
        return response, 500


@scan_bp.route('/scans/<int:scan_id>/results', methods=['GET'])
@jwt_required()
def get_scan_results(scan_id):
    """Obtiene resultados parseados de un escaneo."""
    try:
        results = recon_service.get_scan_results(scan_id)
        return jsonify(results), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting scan results: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@scan_bp.route('/scans/<int:scan_id>/subdomains', methods=['GET'])
@jwt_required()
def get_subdomains(scan_id):
    """Obtiene subdominios encontrados en un escaneo (compatibilidad hacia atrás)."""
    try:
        results = recon_service.get_scan_results(scan_id)
        
        # Extraer subdominios si están disponibles
        subdomains = []
        if results.get('results') and isinstance(results['results'], dict):
            if 'subdomains' in results['results']:
                subdomains = results['results']['subdomains']
            elif 'findings' in results['results']:
                subdomains = [f.get('domain') for f in results['results']['findings'] if f.get('domain')]
        
        return jsonify({
            'scan_id': scan_id,
            'subdomains': subdomains,
            'total': len(subdomains)
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting subdomains: {e}")
        return jsonify({'error': 'Internal server error'}), 500

