"""
Reporting Tasks
===============

Tareas asíncronas para generación de reportes.
"""

import logging
from datetime import datetime
from celery import Task
from celery_app import celery
from repositories import ScanRepository
from services.reporting import ReportingService

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



