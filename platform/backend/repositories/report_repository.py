"""
Report Repository
=================

Repository para operaciones de reportes.
Soporta operaciones CRUD completas y funcionalidades específicas
para el módulo de reportería V2.
"""

from typing import Optional, List
from datetime import datetime
from pathlib import Path
import logging
from models import db, Report

logger = logging.getLogger(__name__)


class ReportRepository:
    """Repository para gestión de reportes."""
    
    @staticmethod
    def create(**kwargs) -> Report:
        """
        Crea un nuevo reporte en la BD.
        
        Args:
            title: Título del reporte
            report_type: technical, executive, compliance
            format: pdf, docx, html
            workspace_id: ID del workspace
            created_by: ID del usuario
            file_path: Ruta al archivo generado (opcional)
            file_size: Tamaño en bytes (opcional)
            total_findings: Total de hallazgos (opcional)
            critical_count, high_count, etc.: Contadores por severidad (opcional)
            risk_score: Score de riesgo 0-10 (opcional)
            files_processed: Cantidad de archivos parseados (opcional)
            tools_used: Lista de herramientas detectadas (opcional)
            generation_time_seconds: Tiempo de generación (opcional)
            content: Contenido markdown/html (opcional)
            
        Returns:
            Report: Instancia creada y guardada
        """
        try:
            report = Report(**kwargs)
            
            # Calcular hash del archivo si existe
            if report.file_path:
                report.file_hash = report.calculate_file_hash()
            
            # Establecer estado y timestamp si es un reporte completado
            if report.file_path and not report.generated_at:
                report.status = 'completed'
                report.generated_at = datetime.utcnow()
            
            db.session.add(report)
            db.session.commit()
            
            logger.info(f"Report created: {report.id} - {report.title}")
            return report
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating report: {e}")
            raise
    
    @staticmethod
    def find_by_id(report_id: int) -> Optional[Report]:
        """
        Busca un reporte por ID.
        
        Args:
            report_id: ID del reporte
            
        Returns:
            Report o None si no existe
        """
        return Report.query.filter_by(id=report_id).first()
    
    @staticmethod
    def find_by_workspace(workspace_id: int, limit: int = 50) -> List[Report]:
        """
        Obtiene reportes de un workspace.
        
        Args:
            workspace_id: ID del workspace
            limit: Máximo de reportes a retornar (default: 50)
            
        Returns:
            Lista de reportes ordenados por fecha (más reciente primero)
        """
        return Report.query.filter_by(
            workspace_id=workspace_id
        ).order_by(
            Report.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def find_by_user(user_id: int, limit: int = 50) -> List[Report]:
        """
        Busca reportes por usuario.
        
        Args:
            user_id: ID del usuario
            limit: Máximo de reportes a retornar (default: 50)
            
        Returns:
            Lista de reportes ordenados por fecha (más reciente primero)
        """
        return Report.query.filter_by(
            created_by=user_id
        ).order_by(
            Report.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def find_latest_by_type(
        workspace_id: int, 
        report_type: str
    ) -> Optional[Report]:
        """
        Obtiene el reporte más reciente de un tipo específico.
        
        Args:
            workspace_id: ID del workspace
            report_type: Tipo de reporte (technical, executive, etc.)
            
        Returns:
            Report más reciente o None
        """
        return Report.query.filter_by(
            workspace_id=workspace_id,
            report_type=report_type,
            status='completed'
        ).order_by(
            Report.created_at.desc()
        ).first()
    
    @staticmethod
    def update_status(
        report_id: int, 
        status: str, 
        error_message: str = None
    ) -> bool:
        """
        Actualiza el estado de un reporte.
        
        Args:
            report_id: ID del reporte
            status: Nuevo estado (pending, generating, completed, failed)
            error_message: Mensaje de error si falla
            
        Returns:
            True si se actualizó, False si no se encontró
        """
        try:
            report = ReportRepository.find_by_id(report_id)
            if not report:
                logger.warning(f"Report not found: {report_id}")
                return False
            
            report.status = status
            if error_message:
                report.error_message = error_message
            
            if status == 'completed' and not report.generated_at:
                report.generated_at = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"Report status updated: {report_id} -> {status}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating report status: {e}")
            return False
    
    @staticmethod
    def update(report: Report) -> Report:
        """
        Actualiza un reporte existente.
        
        Args:
            report: Instancia del reporte a actualizar
            
        Returns:
            Report actualizado
        """
        try:
            db.session.commit()
            logger.info(f"Report updated: {report.id}")
            return report
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating report: {e}")
            raise
    
    @staticmethod
    def delete(report_id: int, delete_file: bool = True) -> bool:
        """
        Elimina un reporte de la BD y opcionalmente el archivo.
        
        Args:
            report_id: ID del reporte
            delete_file: Si True, elimina también el archivo físico
            
        Returns:
            True si se eliminó, False si no se encontró
        """
        try:
            report = ReportRepository.find_by_id(report_id)
            if not report:
                logger.warning(f"Report not found for deletion: {report_id}")
                return False
            
            # Opcionalmente eliminar archivo físico
            if delete_file and report.file_path:
                file_path = Path(report.file_path)
                if file_path.exists():
                    try:
                        file_path.unlink()
                        logger.info(f"Report file deleted: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting report file {file_path}: {e}")
                        # No fallar si el archivo no se puede eliminar
            
            db.session.delete(report)
            db.session.commit()
            logger.info(f"Report deleted: {report_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting report: {e}")
            return False
