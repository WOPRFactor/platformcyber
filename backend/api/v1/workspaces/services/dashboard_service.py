"""
Dashboard Service for Workspaces
================================

Servicio para operaciones de dashboard de workspaces.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_, extract
from models import Scan, Vulnerability, Workspace
from repositories.workspace_repository import WorkspaceRepository

logger = logging.getLogger(__name__)


class WorkspaceDashboardService:
    """Servicio para operaciones de dashboard de workspaces."""
    
    def __init__(self, workspace_repository: WorkspaceRepository = None):
        """Inicializa el servicio."""
        from repositories.workspace_repository import WorkspaceRepository
        self.workspace_repo = workspace_repository or WorkspaceRepository()
    
    def get_stats(self, workspace_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene métricas generales del dashboard.
        
        Args:
            workspace_id: ID del workspace
        
        Returns:
            Dict con estadísticas o None si no existe el workspace
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        scans = Scan.query.filter_by(workspace_id=workspace_id).all()
        active_scans = [s for s in scans if s.status == 'running']
        completed_scans = [s for s in scans if s.status == 'completed']
        failed_scans = [s for s in scans if s.status == 'failed']
        
        vulns = Vulnerability.query.filter_by(workspace_id=workspace_id).all()
        total_vulns = len(vulns)
        
        vulns_by_severity = {
            'critical': len([v for v in vulns if v.severity == 'critical']),
            'high': len([v for v in vulns if v.severity == 'high']),
            'medium': len([v for v in vulns if v.severity == 'medium']),
            'low': len([v for v in vulns if v.severity == 'low']),
            'info': len([v for v in vulns if v.severity == 'info']),
        }
        
        security_score = 100
        if total_vulns > 0:
            security_score = max(0, 100 - (
                vulns_by_severity['critical'] * 5 +
                vulns_by_severity['high'] * 2 +
                vulns_by_severity['medium'] * 0.5 +
                vulns_by_severity['low'] * 0.1
            ))
        
        return {
            'workspace_id': workspace_id,
            'scans': {
                'total': len(scans),
                'active': len(active_scans),
                'completed': len(completed_scans),
                'failed': len(failed_scans),
            },
            'vulnerabilities': {
                'total': total_vulns,
                'by_severity': vulns_by_severity,
            },
            'security_score': round(security_score, 1),
            'audits': {
                'total': 0,
                'completed': 0,
            },
        }
    
    def get_vulnerabilities(self, workspace_id: int) -> Optional[list]:
        """
        Obtiene distribución de vulnerabilidades por severidad.
        
        Args:
            workspace_id: ID del workspace
        
        Returns:
            Lista de distribuciones o None si no existe el workspace
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        vulns = Vulnerability.query.filter_by(workspace_id=workspace_id).all()
        
        distribution = {}
        for vuln in vulns:
            severity = vuln.severity or 'unknown'
            distribution[severity] = distribution.get(severity, 0) + 1
        
        return [{'severity': k, 'count': v} for k, v in distribution.items()]
    
    def get_timeline(self, workspace_id: int, days: int = 30) -> Optional[list]:
        """
        Obtiene timeline de actividades.
        
        Args:
            workspace_id: ID del workspace
            days: Días de antigüedad
        
        Returns:
            Lista de eventos o None si no existe el workspace
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        scans = Scan.query.filter(
            and_(
                Scan.workspace_id == workspace_id,
                Scan.created_at >= cutoff_date
            )
        ).order_by(Scan.created_at.desc()).all()
        
        timeline = []
        for scan in scans:
            timeline.append({
                'date': scan.created_at.isoformat() if scan.created_at else None,
                'type': 'scan',
                'title': f"Scan: {scan.scan_type}",
                'status': scan.status,
                'target': scan.target
            })
        
        return timeline
    
    def get_trends(self, workspace_id: int, days: int = 30) -> Optional[Dict[str, Any]]:
        """
        Obtiene tendencias de vulnerabilidades.
        
        Args:
            workspace_id: ID del workspace
            days: Días de antigüedad
        
        Returns:
            Dict con tendencias o None si no existe el workspace
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        vulns_by_day = Vulnerability.query.filter(
            and_(
                Vulnerability.workspace_id == workspace_id,
                Vulnerability.updated_at >= cutoff_date
            )
        ).with_entities(
            func.date(Vulnerability.updated_at).label('date'),
            Vulnerability.severity,
            func.count(Vulnerability.id).label('count')
        ).group_by(
            func.date(Vulnerability.updated_at),
            Vulnerability.severity
        ).all()
        
        trends = {}
        for date, severity, count in vulns_by_day:
            # func.date() devuelve un string, no un objeto date
            date_str = str(date) if date else None
            if date_str not in trends:
                trends[date_str] = {}
            trends[date_str][severity] = count
        
        return {
            'by_day': [{'date': k, 'vulnerabilities': v} for k, v in trends.items()],
            'period_days': days
        }
    
    def get_top_vulnerabilities(self, workspace_id: int, limit: int = 10) -> Optional[list]:
        """
        Obtiene top vulnerabilidades.
        
        Args:
            workspace_id: ID del workspace
            limit: Límite de resultados
        
        Returns:
            Lista de vulnerabilidades o None si no existe el workspace
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        vulns = Vulnerability.query.filter_by(workspace_id=workspace_id).all()
        
        vuln_groups = {}
        for vuln in vulns:
            title = vuln.title
            if title not in vuln_groups:
                vuln_groups[title] = {
                    'name': title,
                    'count': 0,
                    'severity': vuln.severity,
                    'cve': vuln.cve_id,
                    'affected_hosts': set(),
                }
            
            vuln_groups[title]['count'] += 1
            if vuln.target:
                vuln_groups[title]['affected_hosts'].add(vuln.target)
        
        data = []
        for group in vuln_groups.values():
            data.append({
                'name': group['name'],
                'count': group['count'],
                'severity': group['severity'],
                'cve': group['cve'],
                'affected_hosts': len(group['affected_hosts']),
            })
        
        data.sort(key=lambda x: x['count'], reverse=True)
        return data[:limit]
    
    def get_risk_matrix(self, workspace_id: int) -> Optional[list]:
        """
        Obtiene datos para la matriz de riesgo.
        
        Args:
            workspace_id: ID del workspace
        
        Returns:
            Lista de datos de riesgo o None si no existe el workspace
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        vulns = Vulnerability.query.filter_by(workspace_id=workspace_id).all()
        
        vuln_groups = {}
        for vuln in vulns:
            title = vuln.title
            if title not in vuln_groups:
                vuln_groups[title] = {
                    'name': title,
                    'count': 0,
                    'severity': vuln.severity,
                    'cvss_score': vuln.cvss_score or 0,
                    'cve': vuln.cve_id,
                    'affected_hosts': set(),
                }
            
            vuln_groups[title]['count'] += 1
            if vuln.target:
                vuln_groups[title]['affected_hosts'].add(vuln.target)
        
        data = []
        max_count = max([g['count'] for g in vuln_groups.values()]) if vuln_groups else 1
        
        for idx, (title, group) in enumerate(vuln_groups.items(), 1):
            probability = min(100, (group['count'] / max_count) * 100) if max_count > 0 else 50
            
            if group['cvss_score'] > 0:
                impact = group['cvss_score'] * 10
            else:
                severity_impact = {
                    'critical': 95,
                    'high': 75,
                    'medium': 55,
                    'low': 35,
                    'info': 15,
                }
                impact = severity_impact.get(group['severity'], 50)
            
            data.append({
                'id': str(idx),
                'name': group['name'],
                'probability': round(probability, 1),
                'impact': round(impact, 1),
                'severity': group['severity'],
                'count': group['count'],
                'affected_hosts': len(group['affected_hosts']),
                'cve': group['cve'],
            })
        
        return data

