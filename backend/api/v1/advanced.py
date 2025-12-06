"""
Advanced Features API
=====================

Endpoints para features avanzadas: AI, workflows, scheduling.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import logging

from services.scheduler_service import scheduler_service

# Lazy imports para servicios opcionales
AI_AVAILABLE = False
WORKFLOW_AVAILABLE = False

logger = logging.getLogger(__name__)

advanced_bp = Blueprint('advanced', __name__)


# ============================================================================
# AI RECOMMENDATIONS
# ============================================================================

@advanced_bp.route('/ai/exploit-recommendations', methods=['POST'])
@jwt_required()
def get_exploit_recommendations():
    """Obtiene recomendaciones de exploits para vulnerabilidad."""
    try:
        from services.ai_recommendations_service import ai_recommendations_service
    except Exception as e:
        return jsonify({'error': f'AI service not available: {str(e)}'}), 503
        
    try:
        data = request.get_json()
        vulnerability = data.get('vulnerability')
        
        if not vulnerability:
            return jsonify({'error': 'Vulnerability data required'}), 400
        
        recommendations = ai_recommendations_service.get_exploit_recommendations(vulnerability)
        
        return jsonify(recommendations), 200
        
    except Exception as e:
        logger.error(f"Error getting exploit recommendations: {e}")
        return jsonify({'error': str(e)}), 500


@advanced_bp.route('/ai/remediation-plan', methods=['POST'])
@jwt_required()
def get_remediation_plan():
    """Genera plan de remediación para vulnerabilidades."""
    try:
        data = request.get_json()
        vulnerabilities = data.get('vulnerabilities', [])
        
        if not vulnerabilities:
            return jsonify({'error': 'Vulnerabilities list required'}), 400
        
        plan = ai_recommendations_service.get_remediation_plan(vulnerabilities)
        
        return jsonify(plan), 200
        
    except Exception as e:
        logger.error(f"Error generating remediation plan: {e}")
        return jsonify({'error': str(e)}), 500


@advanced_bp.route('/ai/analyze-patterns', methods=['POST'])
@jwt_required()
def analyze_attack_patterns():
    """Analiza patrones de ataque en resultados."""
    try:
        data = request.get_json()
        scan_results = data.get('scan_results', [])
        
        analysis = ai_recommendations_service.analyze_attack_patterns(scan_results)
        
        return jsonify(analysis), 200
        
    except Exception as e:
        logger.error(f"Error analyzing patterns: {e}")
        return jsonify({'error': str(e)}), 500


@advanced_bp.route('/ai/prioritize-targets', methods=['POST'])
@jwt_required()
def prioritize_targets():
    """Prioriza targets para pentesting."""
    try:
        data = request.get_json()
        targets = data.get('targets', [])
        context = data.get('context')
        
        if not targets:
            return jsonify({'error': 'Targets list required'}), 400
        
        prioritized = ai_recommendations_service.prioritize_targets(targets, context)
        
        return jsonify({'targets': prioritized}), 200
        
    except Exception as e:
        logger.error(f"Error prioritizing targets: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# WORKFLOWS
# ============================================================================

@advanced_bp.route('/workflows', methods=['GET'])
@jwt_required()
def list_workflows():
    """Lista workflows disponibles."""
    try:
        from services.workflow_service import workflow_service
    except Exception as e:
        return jsonify({'error': f'Workflow service not available: {str(e)}'}), 503
        
    try:
        workflows = workflow_service.get_available_workflows()
        return jsonify({'workflows': workflows}), 200
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        return jsonify({'error': str(e)}), 500


@advanced_bp.route('/workflows/<workflow_id>', methods=['GET'])
@jwt_required()
def get_workflow_detail(workflow_id: str):
    """Obtiene detalle de workflow."""
    try:
        workflow = workflow_service.get_workflow(workflow_id)
        return jsonify(workflow), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting workflow: {e}")
        return jsonify({'error': str(e)}), 500


@advanced_bp.route('/workflows/<workflow_id>/execute', methods=['POST'])
@jwt_required()
def execute_workflow(workflow_id: str):
    """Ejecuta workflow automatizado."""
    try:
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        options = data.get('options', {})
        
        if not target or not workspace_id:
            return jsonify({'error': 'Target and workspace_id required'}), 400
        
        result = workflow_service.execute_workflow(
            workflow_id, target, workspace_id, options
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SCHEDULED SCANS
# ============================================================================

@advanced_bp.route('/scheduled-scans', methods=['GET'])
@jwt_required()
def list_scheduled_scans():
    """Lista scans programados."""
    try:
        scans = scheduler_service.get_scheduled_scans()
        return jsonify({'scheduled_scans': scans}), 200
    except Exception as e:
        logger.error(f"Error listing scheduled scans: {e}")
        return jsonify({'error': str(e)}), 500


@advanced_bp.route('/scheduled-scans/preview', methods=['POST'])
@jwt_required()
def preview_scheduled_scan():
    """Preview de scan programado (sin ejecutar)."""
    try:
        data = request.get_json()
        scan_type = data.get('scan_type')
        target = data.get('target')
        schedule = data.get('schedule')
        options = data.get('options', {})
        
        if not all([scan_type, target, schedule]):
            return jsonify({'error': 'scan_type, target, and schedule required'}), 400
        
        result = scheduler_service.preview_scheduled_scan(
            scan_type, target, schedule, options
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error previewing scheduled scan: {e}")
        return jsonify({'error': str(e)}), 500


@advanced_bp.route('/scheduled-scans', methods=['POST'])
@jwt_required()
def create_scheduled_scan():
    """Crea scan programado."""
    try:
        data = request.get_json()
        scan_id = data.get('scan_id')
        scan_type = data.get('scan_type')
        target = data.get('target')
        schedule = data.get('schedule')
        options = data.get('options', {})
        
        if not all([scan_id, scan_type, target, schedule]):
            return jsonify({'error': 'scan_id, scan_type, target, and schedule required'}), 400
        
        result = scheduler_service.schedule_scan(
            scan_id, scan_type, target, schedule, options
        )
        
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Error creating scheduled scan: {e}")
        return jsonify({'error': str(e)}), 500


@advanced_bp.route('/scheduled-scans/<scan_id>', methods=['GET'])
@jwt_required()
def get_scheduled_scan(scan_id: str):
    """Obtiene detalle de scan programado."""
    try:
        scan = scheduler_service.get_scheduled_scan(scan_id)
        return jsonify(scan), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting scheduled scan: {e}")
        return jsonify({'error': str(e)}), 500


@advanced_bp.route('/scheduled-scans/<scan_id>', methods=['DELETE'])
@jwt_required()
def cancel_scheduled_scan(scan_id: str):
    """Cancela scan programado."""
    try:
        success = scheduler_service.cancel_scheduled_scan(scan_id)
        
        if success:
            return jsonify({'message': 'Scheduled scan cancelled'}), 200
        else:
            return jsonify({'error': 'Failed to cancel scan'}), 500
            
    except Exception as e:
        logger.error(f"Error cancelling scheduled scan: {e}")
        return jsonify({'error': str(e)}), 500

