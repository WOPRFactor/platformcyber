"""
Reporting Tasks
===============

Tareas asíncronas para generación de reportes.
"""

import logging
import time
from datetime import datetime
from celery import Task
from celery_app import celery
from repositories import ScanRepository, WorkspaceRepository
from repositories.report_repository import ReportRepository
from services.reporting import ReportingService
from services.reporting.report_service_v2 import ReportServiceV2

logger = logging.getLogger(__name__)


class ReportTask(Task):
    """Base class para tareas de reportes."""
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 2}
    retry_backoff = True


@celery.task(
    bind=True,
    base=ReportTask,
    name='tasks.reporting.generate_full_report',
    time_limit=600,  # 10 minutos
    soft_time_limit=550
)
def generate_full_report_task(self, report_id: int, workspace_id: int, options: dict):
    """
    Genera reporte completo en background.
    
    Args:
        report_id: ID del reporte
        workspace_id: ID del workspace
        options: Opciones del reporte
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'report_id': report_id, 'progress': 0, 'status': 'Starting report generation...'}
        )
        
        reporting_service = ReportingService()
        
        # Generar reporte
        result = reporting_service.generate_full_report(
            workspace_id=workspace_id,
            include_scans=options.get('include_scans', True),
            include_vulnerabilities=options.get('include_vulnerabilities', True)
        )
        
        self.update_state(
            state='PROGRESS',
            meta={'report_id': report_id, 'progress': 75, 'status': 'Finalizing report...'}
        )
        
        return {
            'report_id': report_id,
            'status': 'completed',
            'file_path': result.get('file_path'),
            'completed_at': datetime.utcnow().isoformat()
        }
            
    except Exception as e:
        logger.error(f"Report generation task {report_id} failed: {e}", exc_info=True)
        raise


@celery.task(
    bind=True,
    base=ReportTask,
    name='tasks.reporting.export_to_pdf',
    time_limit=300,  # 5 minutos
    soft_time_limit=280
)
def export_to_pdf_task(self, report_id: int):
    """
    Exporta reporte a PDF en background.
    
    Args:
        report_id: ID del reporte
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'report_id': report_id, 'progress': 0, 'status': 'Exporting to PDF...'}
        )
        
        reporting_service = ReportingService()
        
        # Exportar a PDF (función por implementar)
        result = reporting_service.export_to_pdf(report_id)
        
        return {
            'report_id': report_id,
            'status': 'completed',
            'file_path': result.get('file_path'),
            'completed_at': datetime.utcnow().isoformat()
        }
            
    except Exception as e:
        logger.error(f"PDF export task {report_id} failed: {e}", exc_info=True)
        raise


@celery.task(
    bind=True,
    base=ReportTask,
    name='tasks.reporting.generate_report_v2',
    time_limit=600,  # 10 minutos
    soft_time_limit=550
    # Usar cola 'celery' por defecto (la que está actualmente configurada)
)
def generate_report_v2_task(
    self,
    workspace_id: int,
    report_type: str,
    format_type: str,
    user_id: int
):
    """
    Genera reporte usando el nuevo módulo de reportería (V2) en background.
    
    Esta tarea escanea archivos, parsea con múltiples parsers,
    consolida findings y genera reporte PDF, y lo guarda en la base de datos.
    
    Args:
        workspace_id: ID del workspace
        report_type: Tipo de reporte (technical, executive, compliance)
        format_type: Formato del reporte (pdf)
        user_id: ID del usuario que solicita el reporte
        
    Returns:
        Dict con información del reporte generado:
        {
            'report_id': int,
            'report_path': str,
            'file_size': int,
            'statistics': Dict,
            'risk_metrics': Dict,
            'metadata': Dict
        }
    """
    # Obtener contexto de Flask para acceso a base de datos
    from celery_app import get_flask_app
    app = get_flask_app()
    
    start_time = time.time()
    
    try:
        # Actualizar estado inicial
        self.update_state(
            state='PROGRESS',
            meta={
                'workspace_id': workspace_id,
                'progress': 0,
                'status': 'Iniciando generación de reporte...',
                'step': 'initializing'
            }
        )
        
        # Obtener workspace con contexto de Flask
        with app.app_context():
            workspace_repo = WorkspaceRepository()
            workspace = workspace_repo.find_by_id(workspace_id)
        
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        # Inicializar servicio V2
        report_service = ReportServiceV2()
        
        # Usar WeasyPrint para generación profesional de PDFs
        from services.reporting.generators.pdf_generator_weasy import WeasyPrintPDFGenerator
        report_service.pdf_generator = WeasyPrintPDFGenerator()
        
        # Paso 1: Escanear archivos (10%)
        self.update_state(
            state='PROGRESS',
            meta={
                'workspace_id': workspace_id,
                'progress': 10,
                'status': 'Escaneando archivos del workspace...',
                'step': 'scanning'
            }
        )
        
        # Escanear archivos
        files_by_category = report_service.file_scanner.scan_workspace(
            workspace.id,
            workspace.name
        )
        total_files = sum(len(files) for files in files_by_category.values())
        
        if total_files == 0:
            raise ValueError('No files found in workspace')
        
        # Paso 2: Parsear archivos (30%)
        self.update_state(
            state='PROGRESS',
            meta={
                'workspace_id': workspace_id,
                'progress': 30,
                'status': f'Parseando {total_files} archivos...',
                'step': 'parsing',
                'files_found': total_files
            }
        )
        
        all_findings = []
        tools_detected = set()  # Conjunto para almacenar herramientas detectadas
        files_parsed = 0
        for category, files in files_by_category.items():
            for file_path in files:
                # Usar parse_file_with_parser para obtener también el nombre del parser
                findings, parser_name = report_service.parser_manager.parse_file_with_parser(file_path)
                all_findings.extend(findings)
                
                # Agregar herramienta detectada si existe
                if parser_name:
                    tools_detected.add(parser_name)
                
                files_parsed += 1
                # Actualizar progreso durante parsing
                if files_parsed % 10 == 0:
                    progress = 30 + int((files_parsed / total_files) * 30)
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'workspace_id': workspace_id,
                            'progress': progress,
                            'status': f'Parseando archivos... ({files_parsed}/{total_files})',
                            'step': 'parsing',
                            'files_parsed': files_parsed,
                            'files_total': total_files
                        }
                    )
        
        if not all_findings:
            error_msg = (
                f'No findings parsed from {total_files} files in workspace. '
                f'Files may be empty or in unsupported format. '
                f'Files found: {files_parsed} parsed, {total_files} total.'
            )
            logger.warning(error_msg)
            raise ValueError(error_msg)
        
        # Paso 3: Consolidar (70%)
        self.update_state(
            state='PROGRESS',
            meta={
                'workspace_id': workspace_id,
                'progress': 70,
                'status': 'Consolidando y deduplicando findings...',
                'step': 'consolidating',
                'findings_count': len(all_findings)
            }
        )
        
        consolidated_dict = report_service.data_aggregator.consolidate(all_findings)
        
        # Aplanar el diccionario de findings consolidados a una lista plana para el PDF
        consolidated = []
        for category_findings in consolidated_dict.values():
            consolidated.extend(category_findings)
        
        # Statistics y risk_metrics usan el diccionario original
        statistics = report_service.data_aggregator.get_statistics(consolidated_dict)
        risk_metrics = report_service.risk_calculator.calculate(consolidated_dict)
        
        # Paso 4: Generar reporte (90%)
        self.update_state(
            state='PROGRESS',
            meta={
                'workspace_id': workspace_id,
                'progress': 90,
                'status': 'Generando reporte PDF...',
                'step': 'generating'
            }
        )
        
        # Determinar herramientas usadas ANTES de generar el PDF
        # Prioridad 1: Herramientas detectadas durante el parsing (más confiable)
        tools_used_list = list(tools_detected)
        
        # Prioridad 2: Si algún finding tiene raw_data['tool'], agregarlo también
        # (para parsers que ya lo agregaban, como mysql_enum, redis_enum)
        for finding in consolidated:
            if hasattr(finding, 'raw_data') and finding.raw_data:
                tool_from_finding = finding.raw_data.get('tool')
                if tool_from_finding and tool_from_finding != 'unknown':
                    tools_used_list.append(tool_from_finding)
        
        # Eliminar duplicados y ordenar
        tools_used = sorted(list(set(tools_used_list)))
        
        # Si aún no hay herramientas detectadas, log warning
        if not tools_used:
            logger.warning(
                f"No tools detected for workspace {workspace_id}. "
                f"Processed {total_files} files, found {len(all_findings)} findings."
            )
        
        # Generar metadata y reporte
        from services.reporting.generators.metadata_generator import generate_metadata
        metadata = generate_metadata(workspace, report_type)
        metadata['workspace'] = {
            'id': workspace.id,
            'name': workspace.name,
            'description': workspace.description
        }
        # Agregar tools_used y report_type al metadata para que aparezca en el PDF
        metadata['tools_used'] = tools_used
        metadata['report_type'] = report_type  # Necesario para que el generador detecte el tipo
        
        from utils.workspace_filesystem import get_workspace_dir
        from pathlib import Path
        workspace_dir = get_workspace_dir(workspace.id, workspace.name)
        output_dir = workspace_dir / 'reports'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{report_type}_{timestamp}.{format_type}"
        output_path = output_dir / filename
        
        report_service.pdf_generator.generate(
            consolidated,
            statistics,
            risk_metrics,
            metadata,
            output_path
        )
        
        file_size = output_path.stat().st_size if output_path.exists() else 0
        generation_time = time.time() - start_time
        
        # Calcular contadores de severidad
        severity_counts = statistics.get('by_severity', {})
        
        # Guardar en BD con contexto de Flask
        with app.app_context():
            report_repo = ReportRepository()
            
            saved_report = report_repo.create(
                title=f"Reporte {report_type.title()} - {workspace.name}",
                report_type=report_type,
                format=format_type,
                workspace_id=workspace_id,
                created_by=user_id or 1,  # Default a 1 si no hay user_id
                file_path=str(output_path),
                file_size=file_size,
                total_findings=statistics.get('total_findings', 0),
                critical_count=severity_counts.get('critical', 0),
                high_count=severity_counts.get('high', 0),
                medium_count=severity_counts.get('medium', 0),
                low_count=severity_counts.get('low', 0),
                info_count=severity_counts.get('info', 0),
                risk_score=risk_metrics.get('risk_score', 0.0),
                files_processed=total_files,
                tools_used=tools_used,
                generation_time_seconds=generation_time
            )
            
            logger.info(f"Report saved to database with ID: {saved_report.id}")
        
        # Actualizar estado final con datos serializables
        self.update_state(
            state='SUCCESS',
            meta={
                'status': 'completed',
                'progress': 100,
                'message': 'Reporte generado exitosamente',
                'result': {
                    'report_id': saved_report.id,
                    'workspace_id': workspace_id,
                    'report_path': str(output_path),
                    'file_size': file_size,
                    'total_findings': statistics.get('total_findings', 0),
                    'risk_score': float(risk_metrics.get('risk_score', 0.0)),
                    'metadata': {
                        'report_type': report_type,
                        'format': format_type,
                        'title': saved_report.title,
                        'generation_time': float(generation_time),
                        'tools_used': tools_used
                    }
                }
            }
        )
        
        logger.info(
            f"Report V2 generated successfully for workspace {workspace_id}: "
            f"{output_path} (ID: {saved_report.id})"
        )
        
        # Retornar solo datos serializables
        return {
            'report_id': saved_report.id,
            'workspace_id': workspace_id,
            'report_path': str(output_path),
            'file_size': file_size,
            'total_findings': statistics.get('total_findings', 0),
            'risk_score': float(risk_metrics.get('risk_score', 0.0)),
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Capturar el error completo antes de que Celery intente serializarlo
        import traceback
        error_traceback = traceback.format_exc()
        error_message = str(e)
        error_type = type(e).__name__
        
        logger.error(
            f"Report V2 generation task failed for workspace {workspace_id}: {error_type}: {error_message}",
            exc_info=True
        )
        logger.error(f"Traceback completo:\n{error_traceback}")
        
        # Actualizar estado con información del error antes de re-lanzar
        # Esto ayuda a que el error se serialice correctamente
        try:
            self.update_state(
                state='FAILURE',
                meta={
                    'workspace_id': workspace_id,
                    'error': error_message,
                    'error_type': error_type,
                    'status': f'Error: {error_type}'
                }
            )
        except Exception as update_error:
            logger.warning(f"Could not update task state: {update_error}")
        
        # Re-lanzar la excepción original para que Celery la maneje correctamente
        # Celery serializará automáticamente la excepción con el formato correcto
        raise



