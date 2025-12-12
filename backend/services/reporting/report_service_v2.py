"""
Report Service V2
=================

Servicio que orquesta la generación completa de reportes:
1. Escanea archivos del workspace
2. Parsea archivos con parsers apropiados
3. Consolida y deduplica findings
4. Calcula métricas de riesgo
5. Genera reporte en formato solicitado
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .core import FileScanner, DataAggregator, RiskCalculator
from .parsers import ParserManager
from .generators.pdf_generator_simple import PDFGeneratorSimple
from .generators.pdf_generator_weasy import WeasyPrintPDFGenerator
from .generators.metadata_generator import generate_metadata
from models import Workspace


class ReportServiceV2:
    """
    Servicio principal para generación de reportes.
    
    Orquesta todo el flujo desde el escaneo de archivos hasta
    la generación del reporte final.
    """
    
    def __init__(self):
        """Inicializa el servicio con todos los componentes."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.file_scanner = FileScanner()
        self.parser_manager = ParserManager()
        self.data_aggregator = DataAggregator()
        self.risk_calculator = RiskCalculator()
        # Usar WeasyPrint por defecto para reportes completos
        self.pdf_generator = WeasyPrintPDFGenerator()
    
    def generate_report(
        self,
        workspace: Workspace,
        report_type: str = 'technical',
        format: str = 'pdf',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte completo para un workspace.
        
        Args:
            workspace: Objeto Workspace
            report_type: Tipo de reporte (technical, executive, compliance)
            format: Formato del reporte (pdf, html, docx)
            start_date: Fecha de inicio para filtrar (opcional)
            end_date: Fecha de fin para filtrar (opcional)
            output_dir: Directorio donde guardar el reporte (opcional)
            
        Returns:
            Dict con información del reporte generado:
            {
                'report_path': Path,
                'file_size': int,
                'statistics': Dict,
                'risk_metrics': Dict,
                'metadata': Dict
            }
        """
        self.logger.info(
            f"Generating {report_type} report ({format}) for workspace {workspace.id}"
        )
        
        try:
            # 1. Escanear archivos del workspace
            self.logger.info("Step 1: Scanning workspace files...")
            files_by_category = self.file_scanner.scan_workspace(
                workspace.id,
                workspace.name
            )
            
            total_files = sum(len(files) for files in files_by_category.values())
            if total_files == 0:
                self.logger.warning("No files found in workspace")
                return {
                    'error': 'No files found in workspace',
                    'report_path': None
                }
            
            # 2. Parsear archivos
            self.logger.info("Step 2: Parsing files...")
            all_findings = []
            for category, files in files_by_category.items():
                for file_path in files:
                    findings = self.parser_manager.parse_file(file_path)
                    all_findings.extend(findings)
            
            if not all_findings:
                self.logger.warning("No findings parsed from files")
                return {
                    'error': 'No findings parsed from files',
                    'report_path': None
                }
            
            # 3. Consolidar y deduplicar
            self.logger.info("Step 3: Consolidating findings...")
            consolidated = self.data_aggregator.consolidate(all_findings)
            statistics = self.data_aggregator.get_statistics(consolidated)
            
            # 4. Calcular métricas de riesgo
            self.logger.info("Step 4: Calculating risk metrics...")
            risk_metrics = self.risk_calculator.calculate(consolidated)
            
            # 5. Generar metadata
            metadata = generate_metadata(workspace, report_type)
            metadata['workspace'] = {
                'id': workspace.id,
                'name': workspace.name,
                'description': workspace.description
            }
            
            # 6. Generar reporte
            self.logger.info(f"Step 5: Generating {format} report...")
            
            # Determinar directorio de salida
            if output_dir is None:
                from utils.workspace_filesystem import get_workspace_dir
                workspace_dir = get_workspace_dir(workspace.id, workspace.name)
                output_dir = workspace_dir / 'reports'
                output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{report_type}_{timestamp}.{format}"
            output_path = output_dir / filename
            
            # Generar según formato
            if format == 'pdf':
                self.pdf_generator.generate(
                    consolidated,
                    statistics,
                    risk_metrics,
                    metadata,
                    output_path
                )
            else:
                raise ValueError(f"Format {format} not yet supported")
            
            # Calcular tamaño del archivo
            file_size = output_path.stat().st_size if output_path.exists() else 0
            
            self.logger.info(f"Report generated successfully: {output_path}")
            
            return {
                'report_path': str(output_path),
                'file_size': file_size,
                'statistics': statistics,
                'risk_metrics': risk_metrics,
                'metadata': metadata,
                'files_processed': total_files,
                'findings_count': statistics['total_findings']
            }
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                'error': str(e),
                'report_path': None
            }

