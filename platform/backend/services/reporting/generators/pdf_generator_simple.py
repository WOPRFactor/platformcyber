"""
PDF Generator (Simple)
=======================

Generador simple de PDFs sin usar WeasyPrint.
Usa reportlab directamente para crear PDFs básicos pero funcionales.
"""

from pathlib import Path
from typing import Dict, List, Any
import logging
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime


class PDFGeneratorSimple:
    """
    Generador simple de reportes en formato PDF usando ReportLab.
    No renderiza HTML, pero genera PDFs funcionales con la información clave.
    """
    
    def __init__(self):
        """Inicializa el generador PDF."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el PDF."""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0056b3'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#004085'),
            spaceBefore=12,
            spaceAfter=6
        ))
        
        # Severidad crítica
        self.styles.add(ParagraphStyle(
            name='Critical',
            parent=self.styles['Normal'],
            textColor=colors.HexColor('#dc3545'),
            fontSize=10,
            bold=True
        ))
        
        # Severidad alta
        self.styles.add(ParagraphStyle(
            name='High',
            parent=self.styles['Normal'],
            textColor=colors.HexColor('#fd7e14'),
            fontSize=10,
            bold=True
        ))
    
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
            self.logger.info(f"Generating PDF (simple): {output_path}")
            
            # Asegurar que el directorio existe
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Crear documento
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Contenido del PDF
            story = []
            
            # Título
            story.append(Paragraph(metadata.get('title', 'Security Report'), self.styles['CustomTitle']))
            story.append(Spacer(1, 12))
            
            # Metadata
            workspace_info = metadata.get('workspace', {})
            workspace_name = workspace_info.get('name', 'Unknown') if isinstance(workspace_info, dict) else 'Unknown'
            generated_at = datetime.fromisoformat(metadata.get('generated_at', datetime.utcnow().isoformat()))
            story.append(Paragraph(f"<b>Workspace:</b> {workspace_name}", self.styles['Normal']))
            story.append(Paragraph(f"<b>Generated:</b> {generated_at.strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Resumen Ejecutivo
            story.append(Paragraph("Executive Summary", self.styles['CustomHeading']))
            story.append(Paragraph(f"<b>Risk Score:</b> {risk_metrics.get('risk_score', 0)}/10", self.styles['Normal']))
            story.append(Paragraph(f"<b>Risk Level:</b> {risk_metrics.get('risk_level', 'unknown').upper()}", self.styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Estadísticas
            story.append(Paragraph(f"<b>Total Findings:</b> {statistics.get('total_findings', 0)}", self.styles['Normal']))
            story.append(Paragraph(f"<b>Unique Targets:</b> {statistics.get('unique_targets', 0)}", self.styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Distribución por severidad
            severity_dist = risk_metrics.get('severity_distribution', {})
            if severity_dist:
                story.append(Paragraph("Findings by Severity:", self.styles['Normal']))
                for severity, count in severity_dist.items():
                    story.append(Paragraph(f"  • {severity.capitalize()}: {count}", self.styles['Normal']))
                story.append(Spacer(1, 20))
            
            # Findings por categoría
            story.append(Paragraph("Findings by Category", self.styles['CustomHeading']))
            story.append(Spacer(1, 12))
            
            for category, findings_list in consolidated_findings.items():
                if not findings_list:
                    continue
                
                category_title = category.replace('_', ' ').title()
                story.append(Paragraph(f"{category_title} ({len(findings_list)} findings)", self.styles['Heading3']))
                story.append(Spacer(1, 6))
                
                for finding in findings_list[:10]:  # Limitar a 10 por categoría
                    # ParsedFinding es un dataclass, acceder a atributos directamente
                    severity = getattr(finding, 'severity', 'info')
                    title = getattr(finding, 'title', 'Unknown')
                    target = getattr(finding, 'affected_target', 'N/A')
                    
                    story.append(Paragraph(f"<b>[{severity.upper()}]</b> {title}", self.styles['Normal']))
                    story.append(Paragraph(f"Target: {target}", self.styles['Normal']))
                    story.append(Spacer(1, 8))
                
                if len(findings_list) > 10:
                    story.append(Paragraph(f"... and {len(findings_list) - 10} more findings", self.styles['Normal']))
                
                story.append(Spacer(1, 12))
            
            # Generar PDF
            doc.build(story)
            
            self.logger.info(f"PDF generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating PDF: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise

