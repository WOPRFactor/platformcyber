"""
Executive Summary Generator
===========================

Generador de resumen ejecutivo.
"""

from typing import Dict, Any, List
from collections import defaultdict
from models import Scan, Vulnerability


def generate_executive_summary(
    scans: List[Scan],
    vulns: List[Vulnerability]
) -> Dict[str, Any]:
    """Genera resumen ejecutivo."""
    # Contar por severidad
    severity_counts = defaultdict(int)
    for vuln in vulns:
        severity_counts[vuln.severity] += 1
    
    # Calcular risk score (simplificado)
    risk_score = (
        severity_counts.get('critical', 0) * 10 +
        severity_counts.get('high', 0) * 7 +
        severity_counts.get('medium', 0) * 4 +
        severity_counts.get('low', 0) * 2 +
        severity_counts.get('info', 0) * 1
    )
    
    # Determinar nivel de riesgo
    if risk_score >= 100:
        risk_level = 'Critical'
    elif risk_score >= 50:
        risk_level = 'High'
    elif risk_score >= 20:
        risk_level = 'Medium'
    else:
        risk_level = 'Low'
    
    return {
        'total_scans': len(scans),
        'total_vulnerabilities': len(vulns),
        'severity_distribution': dict(severity_counts),
        'risk_score': risk_score,
        'risk_level': risk_level,
        'key_findings': [
            f'{severity_counts.get("critical", 0)} critical vulnerabilities requiring immediate attention',
            f'{severity_counts.get("high", 0)} high-severity vulnerabilities',
            f'{len(scans)} security assessments performed',
            f'Overall risk level: {risk_level}'
        ]
    }

