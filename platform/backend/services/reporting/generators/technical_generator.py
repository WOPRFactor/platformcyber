"""
Technical Details Generator
===========================

Generador de detalles técnicos.
"""

from typing import List, Dict, Any
from models import Scan, Vulnerability


def generate_technical_details(
    scans: List[Scan],
    vulns: List[Vulnerability]
) -> List[Dict[str, Any]]:
    """Genera detalles técnicos de vulnerabilidades."""
    details = []
    
    # Solo vulnerabilidades críticas y altas
    critical_high = [v for v in vulns if v.severity in ['critical', 'high']]
    
    for vuln in critical_high:
        details.append({
            'vulnerability_id': vuln.id,
            'title': vuln.title,
            'severity': vuln.severity,
            'cve_id': vuln.cve_id,
            'cvss_score': vuln.cvss_score,
            'description': vuln.description,
            'target': vuln.target,
            'port': vuln.port,
            'service': vuln.service,
            'proof_of_concept': vuln.proof_of_concept,
            'impact': vuln.impact,
            'remediation': vuln.remediation,
            'references': vuln.references,
            'discovered_at': vuln.discovered_at.isoformat() if vuln.discovered_at else None
        })
    
    return details


def generate_timeline(
    scans: List[Scan],
    vulns: List[Vulnerability]
) -> List[Dict[str, Any]]:
    """Genera timeline de actividades."""
    events = []
    
    # Agregar scans
    for scan in scans:
        if scan.started_at:
            events.append({
                'timestamp': scan.started_at.isoformat(),
                'type': 'scan_started',
                'scan_id': scan.id,
                'scan_type': scan.scan_type,
                'target': scan.target,
                'tool': scan.options.get('tool')
            })
        
        if scan.completed_at:
            events.append({
                'timestamp': scan.completed_at.isoformat(),
                'type': 'scan_completed',
                'scan_id': scan.id,
                'status': scan.status
            })
    
    # Agregar vulnerabilidades descubiertas
    for vuln in vulns:
        if vuln.discovered_at:
            events.append({
                'timestamp': vuln.discovered_at.isoformat(),
                'type': 'vulnerability_discovered',
                'vulnerability_id': vuln.id,
                'severity': vuln.severity,
                'title': vuln.title,
                'target': vuln.target
            })
    
    # Ordenar por timestamp
    events.sort(key=lambda x: x['timestamp'])
    
    return events

