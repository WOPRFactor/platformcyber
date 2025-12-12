"""
WeasyPrint PDF Generator
========================

Generador de PDFs profesionales usando WeasyPrint.
Convierte templates HTML/CSS a PDF de alta calidad.

Ventajas sobre ReportLab:
- Diseño mucho más bonito y profesional
- Usa HTML/CSS (más fácil de mantener)
- Soporta CSS moderno (Grid, Flexbox, etc.)
- Mejor manejo de estilos y colores
"""

from pathlib import Path
from typing import Dict, Any, List
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WeasyPrintPDFGenerator:
    """Generador de PDFs usando WeasyPrint + Jinja2."""
    
    def __init__(self):
        """Inicializa el generador con Jinja2 para templates."""
        # Configurar directorio de templates
        template_dir = Path(__file__).parent.parent / 'templates'
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
        
        # Inicializar ChartBuilder para gráficos
        from ..utils.chart_builder import ChartBuilder
        self.chart_builder = ChartBuilder()
        
        logger.info(f"WeasyPrint PDF Generator initialized with templates from: {template_dir}")
    
    def generate_technical_report(
        self,
        output_path: Path,
        workspace_name: str,
        findings: List[Any],
        statistics: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Path:
        """
        Genera un reporte técnico en PDF.
        
        Args:
            output_path: Ruta donde guardar el PDF
            workspace_name: Nombre del workspace
            findings: Lista de findings consolidados
            statistics: Estadísticas del escaneo
            risk_metrics: Métricas de riesgo
            metadata: Metadata adicional
            
        Returns:
            Path al archivo PDF generado
        """
        try:
            logger.info(f"Generating technical report with WeasyPrint: {output_path}")
            
            # Generar gráficos primero
            charts_dir = output_path.parent / 'charts'
            
            # Organizar findings por categoría para el gráfico
            findings_by_category = {}
            for finding in findings:
                category = finding.category
                if category not in findings_by_category:
                    findings_by_category[category] = []
                findings_by_category[category].append(finding)
            
            # Generar todos los gráficos
            charts = self.chart_builder.generate_all_charts(
                severity_distribution=risk_metrics.get('severity_distribution', {}),
                findings_by_category=findings_by_category,
                risk_score=risk_metrics.get('risk_score', 0.0),
                output_dir=charts_dir
            )
            
            logger.info(f"Generated {len(charts)} charts for report")
            
            # Preparar datos para el template
            template_data = self._prepare_template_data(
                workspace_name=workspace_name,
                findings=findings,
                statistics=statistics,
                risk_metrics=risk_metrics,
                metadata=metadata
            )
            
            # Agregar paths de gráficos
            template_data['charts'] = charts
            
            # Renderizar template HTML
            template = self.jinja_env.get_template('technical/report_weasy.html')
            html_content = template.render(**template_data)
            
            # Convertir HTML a PDF
            HTML(string=html_content).write_pdf(
                target=str(output_path),
                stylesheets=[self._get_pdf_stylesheet()]
            )
            
            logger.info(f"PDF generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF with WeasyPrint: {e}", exc_info=True)
            raise
    
    def _prepare_template_data(
        self,
        workspace_name: str,
        findings: List[Any],
        statistics: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepara datos estructurados para el template.
        
        Args:
            workspace_name: Nombre del workspace
            findings: Lista de findings
            statistics: Estadísticas
            risk_metrics: Métricas de riesgo
            metadata: Metadata
            
        Returns:
            Dict con datos estructurados para Jinja2
        """
        # Organizar findings por categoría
        findings_by_category = {}
        for finding in findings:
            category = finding.category
            if category not in findings_by_category:
                findings_by_category[category] = []
            findings_by_category[category].append(finding)
        
        # Ordenar por severidad dentro de cada categoría
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        for category in findings_by_category:
            findings_by_category[category].sort(
                key=lambda f: (severity_order.get(f.severity, 999), f.title)
            )
        
        # Obtener todas las vulnerabilidades críticas/altas
        critical_and_high = [
            f for f in findings 
            if f.severity in ['critical', 'high']
        ]
        
        return {
            'workspace_name': workspace_name,
            'report_date': datetime.now().strftime('%d de %B, %Y'),
            'report_time': datetime.now().strftime('%H:%M'),
            
            # Findings
            'findings': findings,
            'findings_by_category': findings_by_category,
            'critical_findings': critical_and_high,
            
            # Estadísticas
            'total_findings': statistics.get('total_findings', 0),
            'total_files': statistics.get('total_files', 0),
            'unique_targets': len(statistics.get('targets', [])),
            'files_by_category': statistics.get('by_category', {}),
            
            # Risk metrics
            'risk_score': risk_metrics.get('risk_score', 0.0),
            'risk_level': risk_metrics.get('risk_level', 'unknown'),
            'severity_distribution': risk_metrics.get('severity_distribution', {}),
            
            # Metadata
            'tools_used': metadata.get('tools_used', []),
            'generation_time': metadata.get('generation_time', 0),
        }
    
    def _get_pdf_stylesheet(self) -> CSS:
        """
        Retorna stylesheet CSS para el PDF.
        
        CSS optimizado para WeasyPrint con soporte para:
        - Paginación profesional
        - Colores de severidad
        - Layouts responsivos
        - Prevención de cortes de página
        
        Returns:
            Objeto CSS de WeasyPrint
        """
        css_content = """
        @page {
            size: A4;
            margin: 2cm;
            
            @top-center {
                content: "Reporte Técnico de Seguridad";
                font-family: Arial, sans-serif;
                font-size: 10pt;
                color: #666;
            }
            
            @bottom-right {
                content: "Página " counter(page) " de " counter(pages);
                font-family: Arial, sans-serif;
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: Arial, Helvetica, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 24pt;
            margin-bottom: 10pt;
            page-break-after: avoid;
        }
        
        h2 {
            color: #34495e;
            font-size: 18pt;
            margin-top: 20pt;
            margin-bottom: 10pt;
            page-break-after: avoid;
        }
        
        h3 {
            color: #555;
            font-size: 14pt;
            margin-top: 15pt;
            margin-bottom: 8pt;
            page-break-after: avoid;
        }
        
        /* Evitar que elementos se corten entre páginas */
        .finding-card, .stat-box, .section-box {
            page-break-inside: avoid;
        }
        
        /* Colores de severidad */
        .severity-critical {
            color: #ffffff;
            background-color: #e74c3c;
            padding: 4pt 10pt;
            border-radius: 12pt;
            font-weight: bold;
            font-size: 10pt;
        }
        
        .severity-high {
            color: #ffffff;
            background-color: #e67e22;
            padding: 4pt 10pt;
            border-radius: 12pt;
            font-weight: bold;
            font-size: 10pt;
        }
        
        .severity-medium {
            color: #ffffff;
            background-color: #f39c12;
            padding: 4pt 10pt;
            border-radius: 12pt;
            font-weight: bold;
            font-size: 10pt;
        }
        
        .severity-low {
            color: #ffffff;
            background-color: #3498db;
            padding: 4pt 10pt;
            border-radius: 12pt;
            font-weight: bold;
            font-size: 10pt;
        }
        
        .severity-info {
            color: #ffffff;
            background-color: #95a5a6;
            padding: 4pt 10pt;
            border-radius: 12pt;
            font-weight: bold;
            font-size: 10pt;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10pt 0;
        }
        
        table th {
            background-color: #34495e;
            color: white;
            padding: 8pt;
            text-align: left;
            font-weight: bold;
        }
        
        table td {
            padding: 8pt;
            border-bottom: 1px solid #ddd;
        }
        
        table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        code {
            background-color: #f4f4f4;
            padding: 2pt 6pt;
            border-radius: 3pt;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }
        
        pre {
            background-color: #f4f4f4;
            padding: 10pt;
            border-radius: 4pt;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            line-height: 1.4;
        }
        """
        
        return CSS(string=css_content)
    
    def generate_executive_report(
        self,
        output_path: Path,
        workspace_name: str,
        findings: List[Any],
        statistics: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Path:
        """
        Genera un reporte ejecutivo en PDF.
        
        El reporte ejecutivo se enfoca en:
        - Métricas visuales y gráficos grandes
        - Top 5 vulnerabilidades críticas/altas
        - Recomendaciones priorizadas
        - Menos detalles técnicos
        
        Args:
            output_path: Ruta donde guardar el PDF
            workspace_name: Nombre del workspace
            findings: Lista de findings consolidados (solo críticos/altos para ejecutivo)
            statistics: Estadísticas del escaneo
            risk_metrics: Métricas de riesgo
            metadata: Metadata adicional
            
        Returns:
            Path al archivo PDF generado
        """
        try:
            logger.info(f"Generating executive report with WeasyPrint: {output_path}")
            
            # Generar gráficos primero
            charts_dir = output_path.parent / 'charts'
            
            # Organizar findings por categoría para el gráfico (usar todos los findings para estadísticas)
            findings_by_category = {}
            for finding in findings:
                category = finding.category
                if category not in findings_by_category:
                    findings_by_category[category] = []
                findings_by_category[category].append(finding)
            
            # Generar todos los gráficos
            charts = self.chart_builder.generate_all_charts(
                severity_distribution=risk_metrics.get('severity_distribution', {}),
                findings_by_category=findings_by_category,
                risk_score=risk_metrics.get('risk_score', 0.0),
                output_dir=charts_dir
            )
            
            logger.info(f"Generated {len(charts)} charts for executive report")
            
            # Preparar datos específicos para template ejecutivo
            template_data = self._prepare_executive_template_data(
                workspace_name=workspace_name,
                findings=findings,
                statistics=statistics,
                risk_metrics=risk_metrics,
                metadata=metadata
            )
            
            # Agregar paths de gráficos
            template_data['charts'] = charts
            
            # Renderizar template HTML ejecutivo
            template = self.jinja_env.get_template('executive/report_weasy.html')
            html_content = template.render(**template_data)
            
            # Convertir HTML a PDF
            HTML(string=html_content).write_pdf(
                target=str(output_path),
                stylesheets=[self._get_pdf_stylesheet()]
            )
            
            logger.info(f"Executive PDF generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating executive PDF with WeasyPrint: {e}", exc_info=True)
            raise
    
    def _prepare_executive_template_data(
        self,
        workspace_name: str,
        findings: List[Any],
        statistics: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepara datos estructurados para el template ejecutivo.
        
        Args:
            workspace_name: Nombre del workspace
            findings: Lista de findings (ya filtrados para ejecutivo)
            statistics: Estadísticas
            risk_metrics: Métricas de riesgo
            metadata: Metadata
            
        Returns:
            Dict con datos estructurados para Jinja2 (template ejecutivo)
        """
        # Filtrar solo críticos y altos para el ejecutivo
        critical_and_high = [
            f for f in findings 
            if f.severity in ['critical', 'high']
        ]
        
        # Ordenar por severidad (críticos primero) y tomar top 5
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        critical_and_high.sort(
            key=lambda f: (severity_order.get(f.severity, 999), f.title)
        )
        top_critical_findings = critical_and_high[:5]
        
        return {
            'workspace_name': workspace_name,
            'report_date': datetime.now().strftime('%d de %B, %Y'),
            'report_time': datetime.now().strftime('%H:%M'),
            
            # Solo top 5 críticas/altas para ejecutivo
            'top_critical_findings': top_critical_findings,
            
            # Estadísticas (todas, para contexto completo)
            'total_findings': statistics.get('total_findings', 0),
            'total_files': statistics.get('total_files', 0),
            'unique_targets': len(statistics.get('targets', [])),
            
            # Risk metrics
            'risk_score': risk_metrics.get('risk_score', 0.0),
            'risk_level': risk_metrics.get('risk_level', 'unknown'),
            'severity_distribution': risk_metrics.get('severity_distribution', {}),
            
            # Metadata
            'tools_used': metadata.get('tools_used', []),
            'generation_time': metadata.get('generation_time', 0),
        }
    
    def generate(
        self,
        findings: Dict[str, List] | List[Any],
        statistics: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        metadata: Dict[str, Any],
        output_path: Path
    ) -> Path:
        """
        Método de interfaz compatible con el generador anterior.
        
        Detecta el tipo de reporte desde metadata y genera el apropiado.
        
        Args:
            findings: Diccionario {categoria: [findings]} o Lista de findings
            statistics: Estadísticas
            risk_metrics: Métricas de riesgo
            metadata: Metadata (debe incluir workspace info y report_type)
            output_path: Path de salida
            
        Returns:
            Path al PDF generado
        """
        workspace_name = metadata.get('workspace', {}).get('name', 'Unknown Workspace')
        report_type = metadata.get('report_type', 'technical')
        
        # Convertir diccionario consolidado a lista plana si es necesario
        if isinstance(findings, dict):
            # Es un diccionario {categoria: [findings]}
            findings_list = []
            for category, findings_list_in_category in findings.items():
                findings_list.extend(findings_list_in_category)
            findings = findings_list
        
        # Filtrar findings para ejecutivo (solo críticos/altos)
        if report_type == 'executive':
            findings = [
                f for f in findings 
                if f.severity in ['critical', 'high']
            ]
            logger.info(f"Filtered findings for executive report: {len(findings)} critical/high findings")
            return self.generate_executive_report(
                output_path=output_path,
                workspace_name=workspace_name,
                findings=findings,
                statistics=statistics,
                risk_metrics=risk_metrics,
                metadata=metadata
            )
        else:
            # Reporte técnico (default)
            return self.generate_technical_report(
                output_path=output_path,
                workspace_name=workspace_name,
                findings=findings,
                statistics=statistics,
                risk_metrics=risk_metrics,
                metadata=metadata
            )

