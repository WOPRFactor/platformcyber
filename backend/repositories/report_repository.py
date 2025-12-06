"""
Report Repository
=================

Repository para operaciones de reportes.
"""

from typing import Optional, List
from models import db, Report


class ReportRepository:
    """Repository para gestión de reportes."""
    
    @staticmethod
    def create(
        title: str,
        report_type: str,
        format: str,
        workspace_id: int,
        created_by: int,
        content: str = None
    ) -> Report:
        """Crea un nuevo reporte."""
        report = Report(
            title=title,
            report_type=report_type,
            format=format,
            workspace_id=workspace_id,
            created_by=created_by,
            content=content,
            status='draft'
        )
        
        db.session.add(report)
        db.session.commit()
        
        return report
    
    @staticmethod
    def find_by_id(report_id: int) -> Optional[Report]:
        """Busca reporte por ID."""
        return Report.query.get(report_id)
    
    @staticmethod
    def find_by_workspace(workspace_id: int) -> List[Report]:
        """Busca reportes por workspace."""
        return Report.query\
            .filter_by(workspace_id=workspace_id)\
            .order_by(Report.created_at.desc())\
            .all()
    
    @staticmethod
    def find_by_user(user_id: int) -> List[Report]:
        """Busca reportes por usuario."""
        return Report.query\
            .filter_by(created_by=user_id)\
            .order_by(Report.created_at.desc())\
            .all()
    
    @staticmethod
    def update(report: Report) -> Report:
        """Actualiza un reporte."""
        db.session.commit()
        return report
    
    @staticmethod
    def delete(report: Report) -> None:
        """Elimina un reporte."""
        db.session.delete(report)
        db.session.commit()



