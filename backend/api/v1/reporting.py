"""
Advanced Reporting API Endpoints
=================================

Endpoints para generación de reportes profesionales.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime

from services import ReportingService

logger = logging.getLogger(__name__)

reporting_bp = Blueprint('reporting', __name__)

# Inicializar servicio
reporting_service = ReportingService()


@reporting_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_report():
    """
    Genera un reporte comprehensivo.
    
    Body:
        {
            "workspace_id": 1,
            "report_type": "full|executive|technical|compliance",
            "include_scans": [1, 2, 3],  // opcional
            "include_vulns": [1, 2, 3],  // opcional
            "date_from": "2025-01-01T00:00:00Z",  // opcional
            "date_to": "2025-12-31T23:59:59Z"      // opcional
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    workspace_id = data.get('workspace_id')
    report_type = data.get('report_type', 'full')
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    valid_types = ['full', 'executive', 'technical', 'compliance']
    if report_type not in valid_types:
        return jsonify({'error': f'Invalid report_type. Must be one of: {valid_types}'}), 400
    
    try:
        # Parse dates
        date_from = None
        date_to = None
        if data.get('date_from'):
            date_from = datetime.fromisoformat(data['date_from'].replace('Z', '+00:00'))
        if data.get('date_to'):
            date_to = datetime.fromisoformat(data['date_to'].replace('Z', '+00:00'))
        
        # Generate report
        report_data = reporting_service.generate_comprehensive_report(
            workspace_id=workspace_id,
            report_type=report_type,
            include_scans=data.get('include_scans'),
            include_vulns=data.get('include_vulns'),
            date_from=date_from,
            date_to=date_to
        )
        
        return jsonify({
            'status': 'success',
            'report': report_data
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@reporting_bp.route('/export/json', methods=['POST'])
@jwt_required()
def export_json():
    """
    Genera y exporta reporte a JSON.
    
    Body: (mismo que /generate)
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    workspace_id = data.get('workspace_id')
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    try:
        # Parse dates
        date_from = None
        date_to = None
        if data.get('date_from'):
            date_from = datetime.fromisoformat(data['date_from'].replace('Z', '+00:00'))
        if data.get('date_to'):
            date_to = datetime.fromisoformat(data['date_to'].replace('Z', '+00:00'))
        
        # Generate report
        report_data = reporting_service.generate_comprehensive_report(
            workspace_id=workspace_id,
            report_type=data.get('report_type', 'full'),
            include_scans=data.get('include_scans'),
            include_vulns=data.get('include_vulns'),
            date_from=date_from,
            date_to=date_to
        )
        
        # Export to JSON
        file_path = reporting_service.export_to_json(report_data)
        
        return send_file(
            file_path,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'{report_data["metadata"]["report_id"]}.json'
        )
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error exporting report to JSON: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@reporting_bp.route('/export/html', methods=['POST'])
@jwt_required()
def export_html():
    """
    Genera y exporta reporte a HTML.
    
    Body: (mismo que /generate)
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    workspace_id = data.get('workspace_id')
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    try:
        # Parse dates
        date_from = None
        date_to = None
        if data.get('date_from'):
            date_from = datetime.fromisoformat(data['date_from'].replace('Z', '+00:00'))
        if data.get('date_to'):
            date_to = datetime.fromisoformat(data['date_to'].replace('Z', '+00:00'))
        
        # Generate report
        report_data = reporting_service.generate_comprehensive_report(
            workspace_id=workspace_id,
            report_type=data.get('report_type', 'full'),
            include_scans=data.get('include_scans'),
            include_vulns=data.get('include_vulns'),
            date_from=date_from,
            date_to=date_to
        )
        
        # Export to HTML
        file_path = reporting_service.export_to_html(report_data)
        
        return send_file(
            file_path,
            mimetype='text/html',
            as_attachment=True,
            download_name=f'{report_data["metadata"]["report_id"]}.html'
        )
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error exporting report to HTML: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@reporting_bp.route('/summary/<int:workspace_id>', methods=['GET'])
@jwt_required()
def get_workspace_summary(workspace_id: int):
    """
    Obtiene un resumen rápido del workspace.
    """
    try:
        report_data = reporting_service.generate_comprehensive_report(
            workspace_id=workspace_id,
            report_type='executive'
        )
        
        return jsonify({
            'workspace_id': workspace_id,
            'metadata': report_data.get('metadata'),
            'executive_summary': report_data.get('executive_summary'),
            'statistics': report_data.get('statistics')
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting workspace summary: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@reporting_bp.route('/vulnerability-breakdown/<int:workspace_id>', methods=['GET'])
@jwt_required()
def get_vulnerability_breakdown(workspace_id: int):
    """
    Obtiene desglose de vulnerabilidades por severidad.
    """
    try:
        report_data = reporting_service.generate_comprehensive_report(
            workspace_id=workspace_id,
            report_type='technical'
        )
        
        return jsonify({
            'workspace_id': workspace_id,
            'vulnerability_breakdown': report_data.get('vulnerability_breakdown'),
            'statistics': report_data.get('statistics', {}).get('vulnerabilities', {})
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting vulnerability breakdown: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@reporting_bp.route('/remediation-roadmap/<int:workspace_id>', methods=['GET'])
@jwt_required()
def get_remediation_roadmap(workspace_id: int):
    """
    Obtiene roadmap de remediación.
    """
    try:
        report_data = reporting_service.generate_comprehensive_report(
            workspace_id=workspace_id,
            report_type='executive'
        )
        
        return jsonify({
            'workspace_id': workspace_id,
            'remediation_roadmap': report_data.get('remediation_roadmap'),
            'risk_assessment': report_data.get('risk_assessment')
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting remediation roadmap: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@reporting_bp.route('/compliance-mapping/<int:workspace_id>', methods=['GET'])
@jwt_required()
def get_compliance_mapping(workspace_id: int):
    """
    Obtiene mapeo de compliance.
    """
    try:
        report_data = reporting_service.generate_comprehensive_report(
            workspace_id=workspace_id,
            report_type='compliance'
        )
        
        return jsonify({
            'workspace_id': workspace_id,
            'compliance_mapping': report_data.get('compliance_mapping')
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting compliance mapping: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@reporting_bp.route('/timeline/<int:workspace_id>', methods=['GET'])
@jwt_required()
def get_timeline(workspace_id: int):
    """
    Obtiene timeline de actividades.
    """
    try:
        report_data = reporting_service.generate_comprehensive_report(
            workspace_id=workspace_id,
            report_type='technical'
        )
        
        return jsonify({
            'workspace_id': workspace_id,
            'timeline': report_data.get('timeline', [])
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting timeline: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@reporting_bp.route('/templates', methods=['GET'])
@jwt_required()
def list_report_templates():
    """
    Lista plantillas de reportes disponibles.
    """
    templates = [
        {
            'id': 'full',
            'name': 'Full Report',
            'description': 'Complete penetration testing report with all sections',
            'includes': [
                'Executive Summary',
                'Technical Details',
                'Compliance Mapping',
                'Remediation Roadmap',
                'Statistics',
                'Timeline'
            ]
        },
        {
            'id': 'executive',
            'name': 'Executive Summary',
            'description': 'High-level report for executives and management',
            'includes': [
                'Executive Summary',
                'Risk Assessment',
                'Remediation Roadmap',
                'Key Statistics'
            ]
        },
        {
            'id': 'technical',
            'name': 'Technical Report',
            'description': 'Detailed technical report for security teams',
            'includes': [
                'Technical Details',
                'Vulnerability Breakdown',
                'Proof of Concepts',
                'Timeline',
                'Scan Summary'
            ]
        },
        {
            'id': 'compliance',
            'name': 'Compliance Report',
            'description': 'Report focused on compliance frameworks',
            'includes': [
                'Compliance Mapping',
                'Vulnerability Breakdown',
                'Remediation Status',
                'Framework Coverage'
            ]
        }
    ]
    
    return jsonify({
        'templates': templates,
        'total': len(templates)
    }), 200


@reporting_bp.route('/export-formats', methods=['GET'])
@jwt_required()
def list_export_formats():
    """
    Lista formatos de exportación disponibles.
    """
    formats = [
        {
            'format': 'json',
            'name': 'JSON',
            'description': 'Machine-readable JSON format',
            'mime_type': 'application/json',
            'supported': True
        },
        {
            'format': 'html',
            'name': 'HTML',
            'description': 'Web-viewable HTML report',
            'mime_type': 'text/html',
            'supported': True
        },
        {
            'format': 'pdf',
            'name': 'PDF',
            'description': 'Professional PDF report',
            'mime_type': 'application/pdf',
            'supported': False,
            'note': 'Planned for future release'
        },
        {
            'format': 'docx',
            'name': 'Microsoft Word',
            'description': 'Editable Word document',
            'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'supported': False,
            'note': 'Planned for future release'
        },
        {
            'format': 'csv',
            'name': 'CSV',
            'description': 'Comma-separated values for spreadsheets',
            'mime_type': 'text/csv',
            'supported': False,
            'note': 'Planned for future release'
        }
    ]
    
    return jsonify({
        'formats': formats,
        'supported_formats': [f['format'] for f in formats if f['supported']]
    }), 200
