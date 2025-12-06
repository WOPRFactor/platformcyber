"""
MITRE ATT&CK API Endpoints
===========================

Endpoints para MITRE ATT&CK Framework y simulaciones.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from functools import wraps
import logging

from services.mitre import mitre_service

logger = logging.getLogger(__name__)

mitre_bp = Blueprint('mitre', __name__)


def handle_errors(f):
    """Decorator para manejo de errores"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"ValueError en {f.__name__}: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error en {f.__name__}: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function


@mitre_bp.route('/tactics', methods=['GET'])
@jwt_required()
@handle_errors
def get_tactics():
    """
    Obtiene todas las tácticas MITRE ATT&CK.
    
    Returns:
        200: Dict con todas las tácticas
        500: Error del servidor
    """
    tactics = mitre_service.get_all_tactics()
    return jsonify({'tactics': tactics}), 200


@mitre_bp.route('/tactics/<tactic_id>', methods=['GET'])
@jwt_required()
@handle_errors
def get_tactic(tactic_id: str):
    """
    Obtiene una táctica específica.
    
    Args:
        tactic_id: ID de la táctica (ej: TA0001)
        
    Returns:
        200: Detalles de la táctica
        404: Táctica no encontrada
        500: Error del servidor
    """
    tactic = mitre_service.get_tactic(tactic_id)
    
    if not tactic:
        return jsonify({'error': 'Tactic not found'}), 404
    
    return jsonify({'tactic': tactic}), 200


@mitre_bp.route('/techniques', methods=['GET'])
@jwt_required()
@handle_errors
def get_techniques():
    """
    Obtiene técnicas MITRE ATT&CK.
    
    Query Params:
        tactic: Filtrar por ID de táctica
        
    Returns:
        200: Dict con técnicas
        500: Error del servidor
    """
    tactic_filter = request.args.get('tactic')
    
    techniques = mitre_service.get_all_techniques(tactic_filter)
    
    return jsonify({
        'techniques': techniques,
        'total': len(techniques)
    }), 200


@mitre_bp.route('/techniques/<technique_id>', methods=['GET'])
@jwt_required()
@handle_errors
def get_technique(technique_id: str):
    """
    Obtiene una técnica específica.
    
    Args:
        technique_id: ID de la técnica (ej: T1566)
        
    Returns:
        200: Detalles de la técnica
        404: Técnica no encontrada
        500: Error del servidor
    """
    technique = mitre_service.get_technique(technique_id)
    
    if not technique:
        return jsonify({'error': 'Technique not found'}), 404
    
    return jsonify({'technique': technique}), 200


@mitre_bp.route('/campaigns', methods=['POST'])
@jwt_required()
@handle_errors
def create_campaign():
    """
    Crea una campaña de simulación MITRE ATT&CK.
    
    Request Body:
        {
            "name": str (required),
            "workspace_id": int (required),
            "techniques": list[str] (required) - IDs de técnicas,
            "description": str (optional)
        }
        
    Returns:
        201: Campaña creada
        400: Datos inválidos
        500: Error del servidor
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    name = data.get('name')
    workspace_id = data.get('workspace_id')
    techniques = data.get('techniques')
    
    if not name or not workspace_id or not techniques:
        return jsonify({'error': 'name, workspace_id and techniques are required'}), 400
    
    if not isinstance(techniques, list) or len(techniques) == 0:
        return jsonify({'error': 'techniques must be a non-empty list'}), 400
    
    description = data.get('description')
    
    result = mitre_service.create_campaign(name, workspace_id, techniques, description)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@mitre_bp.route('/campaigns', methods=['GET'])
@jwt_required()
@handle_errors
def list_campaigns():
    """
    Lista campañas de simulación.
    
    Query Params:
        workspace_id: Filtrar por workspace
        
    Returns:
        200: Lista de campañas
        500: Error del servidor
    """
    workspace_id = request.args.get('workspace_id', type=int)
    
    campaigns = mitre_service.list_campaigns(workspace_id)
    
    return jsonify({
        'campaigns': campaigns,
        'total': len(campaigns)
    }), 200


@mitre_bp.route('/campaigns/<campaign_id>', methods=['GET'])
@jwt_required()
@handle_errors
def get_campaign(campaign_id: str):
    """
    Obtiene detalles de una campaña.
    
    Args:
        campaign_id: ID de la campaña
        
    Returns:
        200: Detalles de la campaña
        404: Campaña no encontrada
        500: Error del servidor
    """
    campaign = mitre_service.get_campaign(campaign_id)
    
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404
    
    return jsonify(campaign), 200


@mitre_bp.route('/campaigns/<campaign_id>/execute', methods=['POST'])
@jwt_required()
@handle_errors
def execute_technique(campaign_id: str):
    """
    Ejecuta una técnica en una campaña (simulación).
    
    Args:
        campaign_id: ID de la campaña
        
    Request Body:
        {
            "technique_id": str (required),
            "target": str (optional)
        }
        
    Returns:
        200: Ejecución completada
        400: Datos inválidos
        404: Campaña o técnica no encontrada
        500: Error del servidor
    """
    data = request.get_json()
    
    if not data or 'technique_id' not in data:
        return jsonify({'error': 'technique_id is required'}), 400
    
    technique_id = data['technique_id']
    target = data.get('target')
    
    result = mitre_service.execute_technique(campaign_id, technique_id, target)
    
    if result['success']:
        return jsonify(result), 200
    else:
        error = result.get('error', 'Unknown error')
        status_code = 404 if 'not found' in error.lower() else 400
        return jsonify(result), status_code


@mitre_bp.route('/coverage', methods=['GET'])
@jwt_required()
@handle_errors
def get_coverage():
    """
    Obtiene matriz de cobertura de detección.
    
    Returns:
        200: Matriz de cobertura
        500: Error del servidor
    """
    coverage = mitre_service.get_coverage_matrix()
    
    return jsonify(coverage), 200


@mitre_bp.route('/kill-chains', methods=['GET'])
@jwt_required()
@handle_errors
def get_kill_chains():
    """
    Obtiene kill chains predefinidos.
    
    Returns:
        200: Dict con kill chains
        500: Error del servidor
    """
    kill_chains = mitre_service.get_kill_chains()
    
    return jsonify({'kill_chains': kill_chains}), 200


@mitre_bp.route('/kill-chains/<chain_id>', methods=['GET'])
@jwt_required()
@handle_errors
def get_kill_chain(chain_id: str):
    """
    Obtiene un kill chain específico.
    
    Args:
        chain_id: ID del kill chain
        
    Returns:
        200: Detalles del kill chain
        404: Kill chain no encontrado
        500: Error del servidor
    """
    kill_chain = mitre_service.get_kill_chain(chain_id)
    
    if not kill_chain:
        return jsonify({'error': 'Kill chain not found'}), 404
    
    return jsonify({'kill_chain': kill_chain}), 200


@mitre_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'mitre_attack',
        'version': '1.0.0',
        'framework': 'Enterprise v14'
    }), 200


@mitre_bp.route('/stats', methods=['GET'])
@jwt_required()
@handle_errors
def get_stats():
    """
    Obtiene estadísticas del framework MITRE ATT&CK.
    
    Returns:
        200: Estadísticas
        500: Error del servidor
    """
    tactics = mitre_service.get_all_tactics()
    techniques = mitre_service.get_all_techniques()
    kill_chains = mitre_service.get_kill_chains()
    
    return jsonify({
        'total_tactics': len(tactics),
        'total_techniques': len(techniques),
        'total_kill_chains': len(kill_chains),
        'tactics': list(tactics.keys()),
        'framework_version': 'Enterprise v14'
    }), 200




