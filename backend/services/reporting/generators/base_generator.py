"""
Base Generator
==============

Clase base abstracta para todos los generadores de reportes.
Define la interfaz común y métodos helper para renderizado.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class BaseGenerator(ABC):
    """
    Clase base abstracta para todos los generadores de reportes.
    
    Cada generador debe implementar:
    - generate(): Genera el reporte en el formato específico
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Inicializa el generador.
        
        Args:
            templates_dir: Directorio de templates (default: templates/)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configurar directorio de templates
        if templates_dir is None:
            # Buscar templates relativo a este archivo
            # Este archivo está en: .../services/reporting/generators/base_generator.py
            # Necesitamos: .../services/reporting/templates/
            templates_dir = Path(__file__).parent.parent / "templates"
        
        self.templates_dir = Path(templates_dir)
        self._setup_jinja()
    
    def _setup_jinja(self):
        """Configura el entorno Jinja2 para renderizado de templates."""
        try:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )
            self.logger.debug(f"Jinja2 environment configured: {self.templates_dir}")
        except Exception as e:
            self.logger.error(f"Error setting up Jinja2: {e}")
            raise
    
    def render_template(
        self, 
        template_name: str, 
        context: Dict[str, Any]
    ) -> str:
        """
        Renderiza un template HTML con el contexto proporcionado.
        
        Args:
            template_name: Nombre del template (ej: 'technical/report.html')
            context: Diccionario con variables para el template
            
        Returns:
            String con HTML renderizado
            
        Raises:
            TemplateNotFound: Si el template no existe
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except TemplateNotFound as e:
            self.logger.error(f"Template not found: {template_name}")
            raise
        except Exception as e:
            self.logger.error(f"Error rendering template {template_name}: {e}")
            raise
    
    @abstractmethod
    def generate(
        self,
        consolidated_findings: Dict[str, List],
        statistics: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        metadata: Dict[str, Any],
        output_path: Path
    ) -> Path:
        """
        Genera el reporte en el formato específico.
        
        Args:
            consolidated_findings: Findings organizados por categoría
            statistics: Estadísticas de los findings
            risk_metrics: Métricas de riesgo calculadas
            metadata: Metadata del reporte (workspace, fecha, etc.)
            output_path: Path donde guardar el reporte generado
            
        Returns:
            Path al archivo generado
        """
        pass
    
    def _prepare_context(
        self,
        consolidated_findings: Dict[str, List],
        statistics: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepara el contexto para los templates.
        
        Args:
            consolidated_findings: Findings organizados por categoría
            statistics: Estadísticas
            risk_metrics: Métricas de riesgo
            metadata: Metadata
            
        Returns:
            Diccionario con contexto completo para templates
        """
        return {
            'metadata': metadata,
            'statistics': statistics,
            'risk_metrics': risk_metrics,
            'findings_by_category': consolidated_findings,
            'severity_colors': {
                'critical': '#dc3545',
                'high': '#fd7e14',
                'medium': '#ffc107',
                'low': '#17a2b8',
                'info': '#6c757d'
            },
            'severity_labels': {
                'critical': 'Critical',
                'high': 'High',
                'medium': 'Medium',
                'low': 'Low',
                'info': 'Info'
            }
        }

