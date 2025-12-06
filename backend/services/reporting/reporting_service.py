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
        workspace = self.workspace_repo.find_by_id(workspace_id)

        if not workspace:
            raise ValueError(f'Workspace {workspace_id} not found')

        # Obtener scans
        if include_scans:
            scans = [self.scan_repo.find_by_id(sid) for sid in include_scans]
            scans = [s for s in scans if s]  # Filtrar None
        else:
            scans = self.scan_repo.find_by_workspace(workspace_id)

        # Filtrar por fecha
        if date_from:
            scans = [s for s in scans if s.started_at and s.started_at >= date_from]
        if date_to:
            scans = [s for s in scans if s.started_at and s.started_at <= date_to]

        # Obtener vulnerabilidades
        if include_vulns:
            vulns = [self.vuln_repo.find_by_id(vid) for vid in include_vulns]
            vulns = [v for v in vulns if v]
        else:
            vulns = self.vuln_repo.find_by_workspace(workspace_id)

        # Filtrar por fecha
        if date_from:
            vulns = [v for v in vulns if v.discovered_at and v.discovered_at >= date_from]
        if date_to:
            vulns = [v for v in vulns if v.discovered_at and v.discovered_at <= date_to]

        # Construir reporte según tipo
        report = {
            'metadata': generate_metadata(workspace, report_type),
            'executive_summary': generate_executive_summary(scans, vulns),
            'statistics': generate_statistics(scans, vulns),
            'vulnerability_breakdown': generate_vulnerability_breakdown(vulns),
            'scan_summary': generate_scan_summary(scans),
        }

        if report_type in ['full', 'technical']:
            report['technical_details'] = generate_technical_details(scans, vulns)
            report['timeline'] = generate_timeline(scans, vulns)

        if report_type in ['full', 'compliance']:
            report['compliance_mapping'] = generate_compliance_mapping(vulns)

        if report_type in ['full', 'executive']:
            report['remediation_roadmap'] = generate_remediation_roadmap(vulns)
            report['risk_assessment'] = generate_risk_assessment(vulns)

        return report

    def export_to_json(self, report_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Exporta reporte a JSON."""
        return export_to_json(report_data, self.output_dir, filename)

    def export_to_html(self, report_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Exporta reporte a HTML."""
        return export_to_html(report_data, self.output_dir, filename)

