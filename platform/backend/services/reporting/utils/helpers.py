"""
Reporting Helpers
=================

Funciones auxiliares para generación de reportes.
"""

from typing import Optional
from models import Scan, Vulnerability


def calculate_duration(scan: Scan) -> Optional[str]:
    """Calcula duración del scan."""
    if scan.started_at and scan.completed_at:
        duration = scan.completed_at - scan.started_at
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f'{hours}h {minutes}m {seconds}s'
        elif minutes > 0:
            return f'{minutes}m {seconds}s'
        else:
            return f'{seconds}s'
    return None


def estimate_remediation_effort(vuln: Vulnerability) -> str:
    """Estima esfuerzo de remediación."""
    effort_map = {
        'critical': 'High',
        'high': 'Medium-High',
        'medium': 'Medium',
        'low': 'Low',
        'info': 'Minimal'
    }
    return effort_map.get(vuln.severity, 'Unknown')


def generate_risk_recommendations(severity_counts: dict) -> list:
    """Genera recomendaciones basadas en el perfil de riesgo."""
    recommendations = []
    
    if severity_counts.get('critical', 0) > 0:
        recommendations.append('Immediate action required: Address all critical vulnerabilities within 7 days')
    
    if severity_counts.get('high', 0) > 5:
        recommendations.append('High-priority remediation plan needed for numerous high-severity findings')
    
    if severity_counts.get('medium', 0) > 10:
        recommendations.append('Consider systematic approach to medium-severity vulnerabilities')
    
    if not recommendations:
        recommendations.append('Maintain current security posture with regular assessments')
    
    return recommendations

