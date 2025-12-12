"""
PDF Generator
=============

Generador de reportes en formato PDF usando WeasyPrint.
Convierte HTML renderizado a PDF profesional.
"""

from pathlib import Path
from typing import Dict, List, Any
import logging
from weasyprint import HTML, CSS
from .base_generator import BaseGenerator


class PDFGenerator(BaseGenerator):
    """
    Generador de reportes en formato PDF.
    
    Usa WeasyPrint para convertir HTML renderizado a PDF.
    """
    
    def __init__(self, templates_dir: Path = None):
        """Inicializa el generador PDF."""
        super().__init__(templates_dir)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate(
        self,
        consolidated_findings: Dict[str, List],
        statistics: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        metadata: Dict[str, Any],
        output_path: Path
    ) -> Path:
        """
        Genera reporte en formato PDF.
        
        Args:
            consolidated_findings: Findings organizados por categoría
            statistics: Estadísticas de los findings
            risk_metrics: Métricas de riesgo calculadas
            metadata: Metadata del reporte
            output_path: Path donde guardar el PDF
            
        Returns:
            Path al archivo PDF generado
        """
        try:
            # Preparar contexto para template
            context = self._prepare_context(
                consolidated_findings,
                statistics,
                risk_metrics,
                metadata
            )
            
            # Renderizar template HTML
            html_content = self.render_template(
                'technical/report.html',
                context
            )
            
            # Obtener CSS
            css_path = self.templates_dir / 'static' / 'css' / 'report.css'
            css_content = None
            if css_path.exists():
                css_content = CSS(filename=str(css_path))
            
            # Generar PDF
            self.logger.info(f"Generating PDF: {output_path}")
            HTML(string=html_content).write_pdf(
                output_path,
                stylesheets=[css_content] if css_content else None
            )
            
            self.logger.info(f"PDF generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating PDF: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise





