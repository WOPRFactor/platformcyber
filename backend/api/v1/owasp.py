"""
OWASP API Endpoints
===================

Endpoints para auditorías OWASP Top 10.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
import logging

from services.owasp_service import owasp_service

logger = logging.getLogger(__name__)

owasp_bp = Blueprint('owasp', __name__)


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


@owasp_bp.route('/categories', methods=['GET'])
@jwt_required()
@handle_errors
def get_categories():
    """
    Obtiene todas las categorías OWASP Top 10.
    
    Returns:
        200: Dict con todas las categorías
        500: Error del servidor
    """
    categories = owasp_service.get_all_categories()
    return jsonify({'categories': categories}), 200


@owasp_bp.route('/categories/<category_id>', methods=['GET'])
@jwt_required()
@handle_errors
def get_category(category_id: str):
    """
    Obtiene información de una categoría específica.
    
    Args:
        category_id: ID de la categoría OWASP
        
    Returns:
        200: Información de la categoría
        404: Categoría no encontrada
        500: Error del servidor
    """
    category = owasp_service.get_category_info(category_id)
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    return jsonify({'category': category}), 200


@owasp_bp.route('/audits', methods=['GET'])
@jwt_required()
@handle_errors
def list_audits():
    """
    Lista auditorías OWASP.
    
    Query Params:
        workspace_id: Filtrar por workspace
        status: Filtrar por estado (pending, running, completed, failed)
        
    Returns:
        200: Lista de auditorías
        500: Error del servidor
    """
    workspace_id = request.args.get('workspace_id', type=int)
    status = request.args.get('status')
    
    audits = owasp_service.list_audits(workspace_id, status)
    
    return jsonify({
        'audits': audits,
        'total': len(audits)
    }), 200


@owasp_bp.route('/audits/preview', methods=['POST'])
@jwt_required()
@handle_errors
def preview_audit():
    """
    Preview de una auditoría OWASP (sin ejecutar).
    
    Request Body:
        {
            "target": str (required) - URL o IP objetivo,
            "workspace_id": int (required),
            "categories": list[str] (optional) - Categorías específicas,
            "options": dict (optional) - Opciones adicionales
        }
        
    Returns:
        200: Preview de la auditoría
        400: Datos inválidos
        500: Error del servidor
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    target = data.get('target')
    workspace_id = data.get('workspace_id')
    
    if not target or not workspace_id:
        return jsonify({'error': 'target and workspace_id are required'}), 400
    
    categories = data.get('categories')
    options = data.get('options', {})
    
    result = owasp_service.preview_audit(target, workspace_id, categories, options)
    return jsonify(result), 200


@owasp_bp.route('/audits', methods=['POST'])
@jwt_required()
@handle_errors
def create_audit():
    """
    Crea una nueva auditoría OWASP.
    
    Request Body:
        {
            "target": str (required) - URL o IP objetivo,
            "workspace_id": int (required),
            "categories": list[str] (optional) - Categorías específicas,
            "options": dict (optional) - Opciones adicionales
        }
        
    Returns:
        201: Auditoría creada exitosamente
        400: Datos inválidos
        500: Error del servidor
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    target = data.get('target')
    workspace_id = data.get('workspace_id')
    
    if not target or not workspace_id:
        return jsonify({'error': 'target and workspace_id are required'}), 400
    
    categories = data.get('categories')
    options = data.get('options', {})
    
    result = owasp_service.create_audit(target, workspace_id, categories, options)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@owasp_bp.route('/audits/<audit_id>', methods=['GET'])
@jwt_required()
@handle_errors
def get_audit(audit_id: str):
    """
    Obtiene detalles de una auditoría OWASP.
    
    Args:
        audit_id: ID de la auditoría
        
    Returns:
        200: Detalles de la auditoría
        404: Auditoría no encontrada
        500: Error del servidor
    """
    audit = owasp_service.get_audit(audit_id)
    
    if not audit:
        return jsonify({'error': 'Audit not found'}), 404
    
    return jsonify(audit), 200


@owasp_bp.route('/audits/<audit_id>', methods=['DELETE'])
@jwt_required()
@handle_errors
def delete_audit(audit_id: str):
    """
    Elimina una auditoría.
    
    Args:
        audit_id: ID de la auditoría
        
    Returns:
        200: Auditoría eliminada
        404: Auditoría no encontrada
        500: Error del servidor
    """
    success = owasp_service.delete_audit(audit_id)
    
    if success:
        return jsonify({'message': 'Audit deleted successfully'}), 200
    else:
        return jsonify({'error': 'Audit not found'}), 404


@owasp_bp.route('/audits/<audit_id>/progress', methods=['PUT'])
@jwt_required()
@handle_errors
def update_progress(audit_id: str):
    """
    Actualiza progreso de auditoría.
    
    Args:
        audit_id: ID de la auditoría
        
    Request Body:
        {
            "progress": int (0-100),
            "status": str (optional) - pending, running, completed, failed
        }
        
    Returns:
        200: Progreso actualizado
        400: Datos inválidos
        404: Auditoría no encontrada
        500: Error del servidor
    """
    data = request.get_json()
    
    if not data or 'progress' not in data:
        return jsonify({'error': 'progress is required'}), 400
    
    progress = data['progress']
    status = data.get('status')
    
    success = owasp_service.update_audit_progress(audit_id, progress, status)
    
    if success:
        return jsonify({'message': 'Progress updated'}), 200
    else:
        return jsonify({'error': 'Audit not found'}), 404


@owasp_bp.route('/audits/<audit_id>/findings', methods=['POST'])
@jwt_required()
@handle_errors
def add_finding(audit_id: str):
    """
    Agrega un hallazgo a la auditoría.
    
    Args:
        audit_id: ID de la auditoría
        
    Request Body:
        {
            "category": str (required) - Categoría OWASP,
            "severity": str - info, low, medium, high, critical,
            "title": str,
            "description": str,
            "evidence": str,
            "remediation": str,
            "cve": str (optional),
            "cvss": float (optional)
        }
        
    Returns:
        201: Hallazgo agregado
        400: Datos inválidos
        404: Auditoría no encontrada
        500: Error del servidor
    """
    data = request.get_json()
    
    if not data or 'category' not in data:
        return jsonify({'error': 'category is required'}), 400
    
    category = data['category']
    
    success = owasp_service.add_finding(audit_id, category, data)
    
    if success:
        return jsonify({'message': 'Finding added'}), 201
    else:
        return jsonify({'error': 'Audit not found'}), 404


@owasp_bp.route('/audits/<audit_id>/simulate', methods=['POST'])
@jwt_required()
@handle_errors
def simulate_audit(audit_id: str):
    """
    Simula ejecución de auditoría (para testing).
    
    Args:
        audit_id: ID de la auditoría
        
    Returns:
        200: Simulación completada
        404: Auditoría no encontrada
        500: Error del servidor
    """
    success = owasp_service.simulate_audit(audit_id)
    
    if success:
        return jsonify({'message': 'Audit simulation completed'}), 200
    else:
        return jsonify({'error': 'Audit not found'}), 404


@owasp_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'owasp',
        'version': '1.0.0'
    }), 200
