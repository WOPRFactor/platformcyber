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
from services.reporting.report_service_v2 import ReportServiceV2
from utils.workspace_logger import log_to_workspace
from repositories.report_repository import ReportRepository
from repositories.workspace_repository import WorkspaceRepository
from tasks.reporting_tasks import generate_report_v2_task
from celery_app import celery
from models import db
import json

logger = logging.getLogger(__name__)

reporting_bp = Blueprint('reporting', __name__)

# Inicializar servicios
reporting_service = ReportingService()
report_service_v2 = ReportServiceV2()


@reporting_bp.route('/generate', methods=['GET', 'POST'])
@jwt_required()
def generate_report():
    """
    Genera un reporte comprehensivo.

    POST Body:
        {
            "workspace_id": 1,
            "report_type": "full|executive|technical|compliance",
            "include_scans": [1, 2, 3],  // opcional
            "include_vulns": [1, 2, 3],  // opcional
            "date_from": "2025-01-01T00:00:00Z",  // opcional
            "date_to": "2025-12-31T23:59:59Z"      // opcional
        }

    GET Query params: (para debugging)
        workspace_id, report_type, date_from, date_to
    """
    import traceback

    logger.info(f"📊 [REPORTING] ===== INICIANDO GENERACIÓN DE REPORTE =====")
    logger.info(f"   Path: {request.path}")
    logger.info(f"   Method: {request.method}")
    logger.info(f"   Origin: {request.headers.get('Origin')}")
    logger.info(f"   Content-Type: {request.headers.get('Content-Type')}")
    logger.info(f"   Authorization: {'Bearer ***' if request.headers.get('Authorization') else 'None'}")

    # Manejar tanto GET como POST
    if request.method == 'GET':
        logger.info("   📥 Método GET detectado - obteniendo parámetros de query")
        data = {
            'workspace_id': request.args.get('workspace_id', type=int),
            'report_type': request.args.get('report_type', 'executive'),
            'include_scans': request.args.getlist('include_scans', type=int) or None,
            'include_vulns': request.args.getlist('include_vulns', type=int) or None,
            'date_from': request.args.get('date_from'),
            'date_to': request.args.get('date_to')
        }
    else:
        logger.info("   📥 Método POST detectado - obteniendo datos del body")
        data = request.get_json()

    logger.info(f"   ✅ Datos obtenidos: {data}")

    try:
        current_user_id = get_jwt_identity()
        logger.info(f"   👤 User ID autenticado: {current_user_id}")

        logger.info("   🔍 Validando parámetros...")
        
        workspace_id = data.get('workspace_id')
        report_type = data.get('report_type', 'full')

        logger.info(f"   📋 workspace_id: {workspace_id} (tipo: {type(workspace_id)})")
        logger.info(f"   📋 report_type: {report_type} (tipo: {type(report_type)})")

        if not workspace_id:
            logger.error("   ❌ VALIDATION ERROR: workspace_id no proporcionado")
            return jsonify({'error': 'workspace_id is required'}), 400

        valid_types = ['full', 'executive', 'technical', 'compliance']
        if report_type not in valid_types:
            logger.error(f"   ❌ VALIDATION ERROR: Tipo de reporte inválido: {report_type}. Válidos: {valid_types}")
            return jsonify({'error': f'Invalid report_type. Must be one of: {valid_types}'}), 400

        logger.info(f"   ✅ Validación inicial completada correctamente")
    except Exception as e:
        logger.error(f"   ❌ ERROR EN VALIDACIÓN INICIAL: {e}")
        logger.error(f"   Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Invalid request: {str(e)}'}), 400
    
    try:
        # Parse dates
        logger.info("   📅 Procesando fechas...")
        date_from = None
        date_to = None

        if data.get('date_from'):
            logger.info(f"   📅 date_from raw: {data['date_from']}")
            try:
                date_from = datetime.fromisoformat(data['date_from'].replace('Z', '+00:00'))
                logger.info(f"   ✅ date_from parsed: {date_from}")
            except Exception as date_error:
                logger.error(f"   ❌ Error parsing date_from: {date_error}")
                return jsonify({'error': f'Invalid date_from format: {data["date_from"]}'}), 400

        if data.get('date_to'):
            logger.info(f"   📅 date_to raw: {data['date_to']}")
            try:
                date_to = datetime.fromisoformat(data['date_to'].replace('Z', '+00:00'))
                logger.info(f"   ✅ date_to parsed: {date_to}")
            except Exception as date_error:
                logger.error(f"   ❌ Error parsing date_to: {date_error}")
                return jsonify({'error': f'Invalid date_to format: {data["date_to"]}'}), 400

        logger.info(f"   ✅ Fechas procesadas: from={date_from}, to={date_to}")

        # Log inicio de generación
        logger.info("   📝 Registrando inicio en workspace logs...")
        try:
            log_to_workspace(
                workspace_id=workspace_id,
                level='info',
                category='reporting',
                message=f'Iniciando generación de reporte tipo: {report_type}',
                user_id=current_user_id,
                metadata={'report_type': report_type, 'date_from': str(date_from), 'date_to': str(date_to)}
            )
            logger.info("   ✅ Log registrado correctamente")
        except Exception as log_error:
            logger.warning(f"   ⚠️ Error registrando log (continuando): {log_error}")
        
        # Generate report
        logger.info(f"   🔄 Llamando a reporting_service.generate_comprehensive_report()")
        logger.info(f"      Params: workspace_id={workspace_id}, report_type={report_type}, include_scans={data.get('include_scans')}, include_vulns={data.get('include_vulns')}")
        
        # Generar reporte usando el servicio
        logger.info("   🔨 Iniciando generación del reporte...")
        logger.info(f"   Parámetros del servicio:")
        logger.info(f"     - workspace_id: {workspace_id}")
        logger.info(f"     - report_type: {report_type}")
        logger.info(f"     - include_scans: {data.get('include_scans')}")
        logger.info(f"     - include_vulns: {data.get('include_vulns')}")
        logger.info(f"     - date_from: {date_from}")
        logger.info(f"     - date_to: {date_to}")

        report_data = reporting_service.generate_comprehensive_report(
            workspace_id=workspace_id,
            report_type=report_type,
            include_scans=data.get('include_scans'),
            include_vulns=data.get('include_vulns'),
            date_from=date_from,
            date_to=date_to
        )

        logger.info("   ✅ Reporte generado exitosamente por el servicio")
        logger.info(f"   📊 Tamaño del reporte: {len(str(report_data))} caracteres")
        
        # Guardar reporte en la BD
        logger.info("   💾 Guardando reporte en la base de datos...")
        try:
            from models.workspace import Workspace
            workspace = Workspace.query.get(workspace_id)
            workspace_name = workspace.name if workspace else f"Workspace {workspace_id}"
            
            report_title = f"Reporte {report_type.capitalize()} - {workspace_name}"
            report_content = json.dumps(report_data, ensure_ascii=False, indent=2)
            
            saved_report = ReportRepository.create(
                title=report_title,
                report_type=report_type,
                format='json',  # Por ahora guardamos como JSON, luego se puede exportar a otros formatos
                workspace_id=workspace_id,
                created_by=current_user_id,
                content=report_content
            )
            
            # Actualizar status y generated_at
            saved_report.status = 'completed'
            saved_report.generated_at = datetime.utcnow()
            saved_report.file_size = len(report_content.encode('utf-8'))
            ReportRepository.update(saved_report)
            
            logger.info(f"   ✅ Reporte guardado en BD con ID: {saved_report.id}")
            
            # Agregar ID del reporte a la respuesta
            report_data['metadata']['report_id'] = saved_report.id
        except Exception as save_error:
            logger.warning(f"   ⚠️ Error guardando reporte en BD (continuando): {save_error}")
            import traceback
            logger.warning(f"   Traceback: {traceback.format_exc()}")
        
        logger.info(f"   ✅ Reporte generado exitosamente")
        
        # Log éxito
        logger.info("   📝 Registrando éxito en workspace logs...")
        try:
            log_to_workspace(
                workspace_id=workspace_id,
                level='success',
                category='reporting',
                message=f'Reporte {report_type} generado exitosamente',
                user_id=current_user_id,
                metadata={'report_type': report_type, 'report_id': report_data.get('metadata', {}).get('report_id')}
            )
            logger.info("   ✅ Log de éxito registrado")
        except Exception as log_error:
            logger.warning(f"   ⚠️ Error registrando log de éxito: {log_error}")

        logger.info("   🎉 ===== GENERACIÓN DE REPORTE COMPLETADA EXITOSAMENTE =====")
        return jsonify({
            'status': 'success',
            'report': report_data
        }), 200
        
    except ValueError as e:
        log_to_workspace(
            workspace_id=workspace_id,
            level='error',
            category='reporting',
            message=f'Error generando reporte: {str(e)}',
            user_id=current_user_id
        )
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        import traceback
        logger.error(f"❌ [REPORTING] Error generando reporte: {e}", exc_info=True)
        logger.error(f"   Traceback completo:")
        logger.error(f"   {traceback.format_exc()}")
        logger.error(f"   workspace_id: {workspace_id}, report_type: {report_type}")
        logger.error(f"   user_id: {current_user_id}")
        
        try:
            log_to_workspace(
                workspace_id=workspace_id,
                level='error',
                category='reporting',
                message=f'Error interno generando reporte: {str(e)}',
                user_id=current_user_id
            )
        except Exception as log_error:
            logger.error(f"   ❌ Error al loguear en workspace: {log_error}")
        
        return jsonify({'error': 'Internal server error'}), 500


@reporting_bp.route('/generate-v2', methods=['POST'])
@jwt_required()
def generate_report_v2():
    """
    Genera un reporte usando el nuevo módulo de reportería (Fase 1B).
    
    POST Body:
        {
            "workspace_id": 1,
            "report_type": "technical",
            "format": "pdf"
        }
    
    Returns:
        {
            "report_path": "/path/to/report.pdf",
            "file_size": 12345,
            "statistics": {...},
            "risk_metrics": {...},
            "metadata": {...}
        }
    """
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        workspace_id = data.get('workspace_id')
        report_type = data.get('report_type', 'technical')
        format_type = data.get('format', 'pdf')
        
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        valid_types = ['technical', 'executive', 'compliance']
        if report_type not in valid_types:
            return jsonify({
                'error': f'Invalid report_type. Must be one of: {valid_types}'
            }), 400
        
        valid_formats = ['pdf']
        if format_type not in valid_formats:
            return jsonify({
                'error': f'Invalid format. Must be one of: {valid_formats}'
            }), 400
        
        # Obtener workspace
        workspace_repo = WorkspaceRepository()
        workspace = workspace_repo.find_by_id(workspace_id)
        
        if not workspace:
            return jsonify({'error': 'Workspace not found'}), 404
        
        # Iniciar generación asíncrona
        task = generate_report_v2_task.delay(
            workspace_id=workspace_id,
            report_type=report_type,
            format_type=format_type,
            user_id=current_user_id
        )
        
        # Log en workspace
        try:
            log_to_workspace(
                workspace_id=workspace_id,
                source='reporting',
                level='info',
                message=f'Iniciando generación asíncrona de reporte {report_type} (V2)',
                metadata={'task_id': task.id, 'user_id': current_user_id}
            )
        except Exception as log_error:
            logger.warning(f"Error logging to workspace: {log_error}")
        
        return jsonify({
            'task_id': task.id,
            'status': 'pending',
            'message': 'Report generation started',
            'workspace_id': workspace_id,
            'report_type': report_type,
            'format': format_type
        }), 202  # 202 Accepted para operación asíncrona
        
    except Exception as e:
        logger.error(f"Error generating report V2: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@reporting_bp.route('/status/<task_id>', methods=['GET'])
@jwt_required()
def get_report_status(task_id: str):
    """
    Obtiene el estado de una tarea de generación de reporte.
    
    Args:
        task_id: ID de la tarea Celery
        
    Returns:
        {
            "task_id": "...",
            "status": "PENDING|PROGRESS|SUCCESS|FAILURE",
            "progress": 0-100,
            "result": {...} (si está completo),
            "error": "..." (si falló)
        }
    """
    try:
        task = celery.AsyncResult(task_id)
        
        # Acceder a task.state puede fallar si la excepción no está serializada correctamente
        # Envolver en try-except para manejar este caso
        try:
            task_state = task.state
        except ValueError as state_error:
            # Si no podemos obtener el estado porque la excepción no está serializada,
            # asumir que la tarea falló
            logger.warning(f"Could not get task.state for task {task_id}: {state_error}")
            return jsonify({
                'task_id': task_id,
                'status': 'failed',
                'progress': 0,
                'error': 'Task failed (error details unavailable due to serialization issue)',
                'message': 'Report generation failed'
            }), 200
        
        if task_state == 'PENDING':
            response = {
                'task_id': task_id,
                'status': 'pending',
                'progress': 0,
                'message': 'Task is waiting to be processed'
            }
        elif task_state == 'PROGRESS':
            meta = task.info or {}
            response = {
                'task_id': task_id,
                'status': 'processing',
                'progress': meta.get('progress', 0),
                'message': meta.get('status', 'Processing...'),
                'step': meta.get('step', 'unknown')
            }
        elif task_state == 'SUCCESS':
            result = task.result
            response = {
                'task_id': task_id,
                'status': 'completed',
                'progress': 100,
                'result': result,
                'message': 'Report generated successfully'
            }
        elif task_state == 'FAILURE':
            # Manejar información de excepción de Celery correctamente
            # Acceder a task.info puede fallar si la excepción no está serializada correctamente
            error_message = 'Report generation failed'
            error_type = 'UnknownError'
            
            try:
                error_info = task.info
                
                # Si es un diccionario con metadata (de update_state)
                if isinstance(error_info, dict):
                    error_message = error_info.get('error', str(error_info))
                    error_type = error_info.get('error_type', 'UnknownError')
                # Si es una tupla (formato antiguo de Celery)
                elif isinstance(error_info, tuple) and len(error_info) >= 2:
                    error_message = str(error_info[1]) if error_info[1] else str(error_info[0])
                    error_type = str(error_info[0]) if error_info[0] else 'UnknownError'
                # Si es una excepción directamente
                elif isinstance(error_info, Exception):
                    error_message = str(error_info)
                    error_type = type(error_info).__name__
                # Si tiene atributo error
                elif hasattr(error_info, 'error'):
                    error_message = str(getattr(error_info, 'error', 'Unknown error'))
                # Cualquier otro formato
                else:
                    error_message = str(error_info) if error_info else 'Unknown error'
                    
            except ValueError as ve:
                # Error de serialización de Celery
                logger.warning(f"Could not access task.info for failed task {task_id}: {ve}")
                error_message = 'Report generation failed (error details unavailable due to serialization issue)'
                error_type = 'SerializationError'
            except Exception as info_error:
                # Cualquier otro error al acceder a task.info
                logger.warning(f"Could not access task.info for failed task {task_id}: {info_error}")
                error_message = f'Report generation failed (could not retrieve error details: {str(info_error)})'
                error_type = type(info_error).__name__
            
            response = {
                'task_id': task_id,
                'status': 'failed',
                'progress': 0,
                'error': error_message,
                'error_type': error_type,
                'message': 'Report generation failed'
            }
        else:
            response = {
                'task_id': task_id,
                'status': task.state.lower(),
                'progress': 0,
                'message': f'Task state: {task.state}'
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting task status {task_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'task_id': task_id
        }), 500


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
        
        # Log inicio de exportación
        log_to_workspace(
            workspace_id=workspace_id,
            level='info',
            category='reporting',
            message='Iniciando exportación de reporte a JSON',
            user_id=current_user_id,
            metadata={'format': 'json', 'report_type': data.get('report_type', 'full')}
        )
        
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
        
        # Log éxito
        log_to_workspace(
            workspace_id=workspace_id,
            level='success',
            category='reporting',
            message='Reporte exportado a JSON exitosamente',
            user_id=current_user_id,
            metadata={'format': 'json', 'filename': f'{report_data["metadata"]["report_id"]}.json'}
        )
        
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
        
        # Log inicio de exportación
        log_to_workspace(
            workspace_id=workspace_id,
            level='info',
            category='reporting',
            message='Iniciando exportación de reporte a HTML',
            user_id=current_user_id,
            metadata={'format': 'html', 'report_type': data.get('report_type', 'full')}
        )
        
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
        
        # Log éxito
        log_to_workspace(
            workspace_id=workspace_id,
            level='success',
            category='reporting',
            message='Reporte exportado a HTML exitosamente',
            user_id=current_user_id,
            metadata={'format': 'html', 'filename': f'{report_data["metadata"]["report_id"]}.html'}
        )
        
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


@reporting_bp.route('/history', methods=['GET'])
@jwt_required()
def get_report_history():
    """
    Obtiene el historial de reportes generados.
    
    Query params:
        workspace_id: ID del workspace (opcional, filtra por workspace)
        limit: Cantidad de reportes a retornar (default: 20)
        offset: Offset para paginación (default: 0)
    """
    try:
        current_user_id = get_jwt_identity()
        workspace_id = request.args.get('workspace_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if workspace_id:
            reports = ReportRepository.find_by_workspace(workspace_id)
        else:
            reports = ReportRepository.find_by_user(current_user_id)
        
        # Aplicar paginación
        reports = reports[offset:offset + limit]
        
        # Serializar reportes
        reports_data = []
        for report in reports:
            report_dict = report.to_dict()
            # Agregar nombre del workspace si está disponible
            if report.workspace:
                report_dict['workspace_name'] = report.workspace.name
            reports_data.append(report_dict)
        
        return jsonify({
            'status': 'success',
            'reports': reports_data,
            'total': len(reports_data),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo historial de reportes: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@reporting_bp.route('/history/<int:report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id: int):
    """
    Obtiene un reporte específico por ID.
    """
    try:
        current_user_id = get_jwt_identity()
        report = ReportRepository.find_by_id(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        report_dict = report.to_dict()
        if report.content:
            try:
                report_dict['content'] = json.loads(report.content)
            except:
                report_dict['content'] = report.content
        
        if report.workspace:
            report_dict['workspace_name'] = report.workspace.name
        
        return jsonify({
            'status': 'success',
            'report': report_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo reporte {report_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


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


@reporting_bp.route('/list/<int:workspace_id>', methods=['GET'])
@jwt_required()
def list_reports(workspace_id: int):
    """
    Lista todos los reportes de un workspace.
    
    Query params opcionales:
        limit: Máximo de reportes (default: 50)
        report_type: Filtrar por tipo
    
    Args:
        workspace_id: ID del workspace
        
    Returns:
        {
            "success": true,
            "reports": [
                {
                    "id": 123,
                    "title": "Reporte Técnico...",
                    "report_type": "technical",
                    "format": "pdf",
                    "file_size": 2469,
                    "risk_score": 7.8,
                    "total_findings": 35,
                    "severity_counts": {...},
                    "created_at": "2025-12-10T10:30:00",
                    "can_download": true
                },
                ...
            ],
            "total": 10
        }
    """
    try:
        report_repo = ReportRepository()
        limit = request.args.get('limit', 50, type=int)
        report_type_filter = request.args.get('report_type')
        
        reports = report_repo.find_by_workspace(workspace_id, limit=limit)
        
        # Filtrar por tipo si se especifica
        if report_type_filter:
            reports = [r for r in reports if r.report_type == report_type_filter]
        
        # Verificar que los archivos existan
        from pathlib import Path
        reports_data = []
        for report in reports:
            data = report.to_dict()
            data['can_download'] = Path(report.file_path).exists() if report.file_path else False
            reports_data.append(data)
        
        return jsonify({
            'success': True,
            'reports': reports_data,
            'total': len(reports_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing reports for workspace {workspace_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reporting_bp.route('/download/<int:report_id>', methods=['GET'])
@jwt_required()
def download_report(report_id):
    """
    Descarga un reporte generado.
    
    Args:
        report_id: ID del reporte a descargar
    
    Returns:
        Archivo PDF del reporte
    """
    try:
        report_repo = ReportRepository()
        report = report_repo.find_by_id(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        if not report.file_path:
            return jsonify({'error': 'Report file not available'}), 404
        
        # Verificar que el archivo existe
        from pathlib import Path
        file_path = Path(report.file_path)
        
        if not file_path.exists():
            return jsonify({'error': 'Report file not found on disk'}), 404
        
        # Enviar archivo
        return send_file(
            str(file_path),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{report.title}.pdf"
        )
        
    except Exception as e:
        logger.error(f"Error downloading report {report_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@reporting_bp.route('/download-by-path', methods=['POST'])
@jwt_required()
def download_by_path():
    """
    Descarga un reporte usando su ruta en el filesystem.
    
    POST Body:
        {
            "report_path": "/path/to/report.pdf"
        }
    """
    try:
        data = request.get_json()
        report_path = data.get('report_path')
        
        if not report_path:
            return jsonify({'error': 'report_path is required'}), 400
        
        from pathlib import Path
        file_path = Path(report_path)
        
        # Validación de seguridad: el archivo debe estar dentro de workspaces
        if 'workspaces' not in str(file_path):
            return jsonify({'error': 'Invalid file path'}), 403
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        if not file_path.is_file():
            return jsonify({'error': 'Path is not a file'}), 400
        
        filename = file_path.name
        
        return send_file(
            str(file_path),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error downloading report by path: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
