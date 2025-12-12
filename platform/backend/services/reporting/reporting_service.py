"""
Advanced Reporting Service
===========================

Servicio completo para generación de reportes profesionales de pentesting.

Características:
- Generación de reportes ejecutivos y técnicos
- Exportación a múltiples formatos (PDF, DOCX, HTML, JSON, CSV)
- Plantillas personalizables
- Estadísticas y métricas consolidadas
- Executive summary
- Technical details con evidencias
- Remediation roadmap
- Compliance mapping
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from repositories import (
    ScanRepository, VulnerabilityRepository,
    WorkspaceRepository, UserRepository
)
from models import Workspace
from services.reporting.generators import (
    generate_metadata,
    generate_executive_summary,
    generate_statistics,
    generate_vulnerability_breakdown,
    generate_scan_summary,
    generate_technical_details,
    generate_timeline,
    generate_compliance_mapping,
    generate_remediation_roadmap,
    generate_risk_assessment
)
from services.reporting.exporters import export_to_json, export_to_html

logger = logging.getLogger(__name__)


class ReportingService:
    """Servicio avanzado para generación de reportes."""

    def __init__(
        self,
        scan_repository: ScanRepository = None,
        vuln_repository: VulnerabilityRepository = None,
        workspace_repository: WorkspaceRepository = None,
        user_repository: UserRepository = None
    ):
        """Inicializa el servicio."""
        self.scan_repo = scan_repository or ScanRepository()
        self.vuln_repo = vuln_repository or VulnerabilityRepository()
        self.workspace_repo = workspace_repository or WorkspaceRepository()
        self.user_repo = user_repository or UserRepository()
        from utils.workspace_filesystem import PROJECT_TMP_DIR
        self.output_dir = PROJECT_TMP_DIR / 'reports'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_comprehensive_report(
        self,
        workspace_id: int,
        report_type: str = 'full',
        include_scans: Optional[List[int]] = None,
        include_vulns: Optional[List[int]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte comprehensivo de pentesting.

        Args:
            workspace_id: ID del workspace
            report_type: Tipo de reporte (full, executive, technical, compliance)
            include_scans: Lista de scan IDs a incluir (opcional)
            include_vulns: Lista de vulnerability IDs a incluir (opcional)
            date_from: Fecha inicio (opcional)
            date_to: Fecha fin (opcional)

        Returns:
            Dict con el reporte completo
        """
        logger.info(f"📊 [ReportingService] Iniciando generate_comprehensive_report")
        logger.info(f"   workspace_id: {workspace_id}, report_type: {report_type}")
        logger.info(f"   include_scans: {include_scans}, include_vulns: {include_vulns}")
        logger.info(f"   date_from: {date_from}, date_to: {date_to}")
        
        try:
            logger.info(f"   🔍 Obteniendo workspace {workspace_id}")
            workspace = self.workspace_repo.find_by_id(workspace_id)

            if not workspace:
                logger.error(f"   ❌ Workspace {workspace_id} no encontrado")
                raise ValueError(f'Workspace {workspace_id} not found')
            
            logger.info(f"   ✅ Workspace encontrado: {workspace.name}")
        except Exception as e:
            logger.error(f"   ❌ Error obteniendo workspace: {e}", exc_info=True)
            raise

        # Obtener scans
        try:
            logger.info(f"   🔍 Obteniendo scans para workspace {workspace_id}")
            if include_scans:
                scans = [self.scan_repo.find_by_id(sid) for sid in include_scans]
                scans = [s for s in scans if s]  # Filtrar None
                logger.info(f"   ✅ {len(scans)} scans obtenidos (filtrados por IDs)")
            else:
                scans = self.scan_repo.find_by_workspace(workspace_id)
                logger.info(f"   ✅ {len(scans)} scans obtenidos del workspace")

            # Filtrar por fecha
            if date_from:
                scans_before = len(scans)
                scans = [s for s in scans if s.started_at and s.started_at >= date_from]
                logger.info(f"   📅 Filtrados por date_from: {scans_before} -> {len(scans)}")
            if date_to:
                scans_before = len(scans)
                scans = [s for s in scans if s.started_at and s.started_at <= date_to]
                logger.info(f"   📅 Filtrados por date_to: {scans_before} -> {len(scans)}")
        except Exception as e:
            logger.error(f"   ❌ Error obteniendo scans: {e}", exc_info=True)
            raise

        # Obtener vulnerabilidades
        try:
            logger.info(f"   🔍 Obteniendo vulnerabilidades para workspace {workspace_id}")
            if include_vulns:
                vulns = [self.vuln_repo.find_by_id(vid) for vid in include_vulns]
                vulns = [v for v in vulns if v]
                logger.info(f"   ✅ {len(vulns)} vulnerabilidades obtenidas (filtradas por IDs)")
            else:
                vulns = self.vuln_repo.find_by_workspace(workspace_id)
                logger.info(f"   ✅ {len(vulns)} vulnerabilidades obtenidas del workspace")

            # Filtrar por fecha
            if date_from:
                vulns_before = len(vulns)
                vulns = [v for v in vulns if v.discovered_at and v.discovered_at >= date_from]
                logger.info(f"   📅 Filtradas por date_from: {vulns_before} -> {len(vulns)}")
            if date_to:
                vulns_before = len(vulns)
                vulns = [v for v in vulns if v.discovered_at and v.discovered_at <= date_to]
                logger.info(f"   📅 Filtradas por date_to: {vulns_before} -> {len(vulns)}")
        except Exception as e:
            logger.error(f"   ❌ Error obteniendo vulnerabilidades: {e}", exc_info=True)
            raise

        # Construir reporte según tipo
        logger.info(f"   🔨 Construyendo reporte tipo: {report_type}")
        
        try:
            logger.info(f"      Generando metadata...")
            report = {
                'metadata': generate_metadata(workspace, report_type),
            }
            logger.info(f"      ✅ Metadata generada")
            
            logger.info(f"      Generando executive_summary...")
            report['executive_summary'] = generate_executive_summary(scans, vulns)
            logger.info(f"      ✅ Executive summary generado")
            
            logger.info(f"      Generando statistics...")
            report['statistics'] = generate_statistics(scans, vulns)
            logger.info(f"      ✅ Statistics generadas")
            
            logger.info(f"      Generando vulnerability_breakdown...")
            report['vulnerability_breakdown'] = generate_vulnerability_breakdown(vulns)
            logger.info(f"      ✅ Vulnerability breakdown generado")
            
            logger.info(f"      Generando scan_summary...")
            report['scan_summary'] = generate_scan_summary(scans)
            logger.info(f"      ✅ Scan summary generado")
        except Exception as e:
            logger.error(f"   ❌ Error generando secciones básicas del reporte: {e}", exc_info=True)
            raise

        if report_type in ['full', 'technical']:
            try:
                logger.info(f"      Generando technical_details...")
                report['technical_details'] = generate_technical_details(scans, vulns)
                logger.info(f"      ✅ Technical details generados")
                
                logger.info(f"      Generando timeline...")
                report['timeline'] = generate_timeline(scans, vulns)
                logger.info(f"      ✅ Timeline generado")
            except Exception as e:
                logger.error(f"   ❌ Error generando secciones técnicas: {e}", exc_info=True)
                raise

        if report_type in ['full', 'compliance']:
            try:
                logger.info(f"      Generando compliance_mapping...")
                report['compliance_mapping'] = generate_compliance_mapping(vulns)
                logger.info(f"      ✅ Compliance mapping generado")
            except Exception as e:
                logger.error(f"   ❌ Error generando compliance mapping: {e}", exc_info=True)
                raise

        if report_type in ['full', 'executive']:
            try:
                logger.info(f"      Generando remediation_roadmap...")
                report['remediation_roadmap'] = generate_remediation_roadmap(vulns)
                logger.info(f"      ✅ Remediation roadmap generado")
                
                logger.info(f"      Generando risk_assessment...")
                report['risk_assessment'] = generate_risk_assessment(vulns)
                logger.info(f"      ✅ Risk assessment generado")
            except Exception as e:
                logger.error(f"   ❌ Error generando secciones ejecutivas: {e}", exc_info=True)
                raise

        logger.info(f"   ✅ Reporte completo generado exitosamente")
        return report

    def export_to_json(self, report_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Exporta reporte a JSON."""
        return export_to_json(report_data, self.output_dir, filename)

    def export_to_html(self, report_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Exporta reporte a HTML."""
        return export_to_html(report_data, self.output_dir, filename)

