"""
Remediation Roadmap Generator
==============================

Generador de roadmap de remediación.
"""

from typing import Dict, Any, List
from models import Vulnerability
from services.reporting.utils.helpers import estimate_remediation_effort


def generate_remediation_roadmap(
    vulns: List[Vulnerability]
) -> Dict[str, Any]:
    """Genera roadmap de remediación priorizado."""
    # Agrupar por prioridad
    immediate = []  # Critical
    short_term = []  # High
    medium_term = []  # Medium
    long_term = []  # Low
    
    for vuln in vulns:
        if vuln.status in ['resolved', 'false_positive']:
            continue  # Skip resolved/FP
        
        vuln_item = {
            'id': vuln.id,
            'title': vuln.title,
            'target': vuln.target,
            'remediation': vuln.remediation,
            'estimated_effort': estimate_remediation_effort(vuln)
        }
        
        if vuln.severity == 'critical':
            immediate.append(vuln_item)
        elif vuln.severity == 'high':
            short_term.append(vuln_item)
        elif vuln.severity == 'medium':
            medium_term.append(vuln_item)
        else:
            long_term.append(vuln_item)
    
    return {
        'immediate_action': {
            'timeframe': '0-7 days',
            'priority': 'Critical',
            'items': immediate,
            'count': len(immediate)
        },
        'short_term': {
            'timeframe': '1-4 weeks',
            'priority': 'High',
            'items': short_term,
            'count': len(short_term)
        },
        'medium_term': {
            'timeframe': '1-3 months',
            'priority': 'Medium',
            'items': medium_term,
            'count': len(medium_term)
        },
        'long_term': {
            'timeframe': '3-6 months',
            'priority': 'Low',
            'items': long_term,
            'count': len(long_term)
        }
    }


def generate_risk_assessment(vulns: List[Vulnerability]) -> Dict[str, Any]:
    """Genera evaluación de riesgos."""
    from collections import defaultdict
    from services.reporting.utils.helpers import generate_risk_recommendations
    
    # Calcular métricas de riesgo
    total_vulns = len(vulns)
    unresolved = len([v for v in vulns if v.status not in ['resolved', 'false_positive']])
    
    severity_counts = defaultdict(int)
    for vuln in vulns:
        if vuln.status not in ['resolved', 'false_positive']:
            severity_counts[vuln.severity] += 1
    
    # Risk score ponderado
    risk_score = (
        severity_counts.get('critical', 0) * 10 +
        severity_counts.get('high', 0) * 7 +
        severity_counts.get('medium', 0) * 4 +
        severity_counts.get('low', 0) * 2 +
        severity_counts.get('info', 0) * 1
    )
    
    # Normalizar a 0-100
    max_possible_score = total_vulns * 10
    normalized_score = (risk_score / max_possible_score * 100) if max_possible_score > 0 else 0
    
    return {
        'overall_risk_score': round(normalized_score, 2),
        'total_vulnerabilities': total_vulns,
        'unresolved_vulnerabilities': unresolved,
        'resolution_rate': round((total_vulns - unresolved) / total_vulns * 100, 2) if total_vulns > 0 else 0,
        'critical_count': severity_counts.get('critical', 0),
        'high_count': severity_counts.get('high', 0),
        'medium_count': severity_counts.get('medium', 0),
        'low_count': severity_counts.get('low', 0),
        'recommendations': generate_risk_recommendations(severity_counts)
    }

