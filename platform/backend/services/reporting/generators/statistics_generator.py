"""
Statistics Generator
====================

Generador de estadísticas para reportes.
"""

from typing import Dict, Any, List
from collections import defaultdict
from models import Scan, Vulnerability


def generate_statistics(
    scans: List[Scan],
    vulns: List[Vulnerability]
) -> Dict[str, Any]:
    """Genera estadísticas detalladas."""
    # Scans por tipo
    scans_by_type = defaultdict(int)
    scans_by_status = defaultdict(int)
    scans_by_tool = defaultdict(int)
    
    for scan in scans:
        scans_by_type[scan.scan_type] += 1
        scans_by_status[scan.status] += 1
        tool = scan.options.get('tool', 'unknown')
        scans_by_tool[tool] += 1
    
    # Vulnerabilidades por estado
    vulns_by_status = defaultdict(int)
    vulns_by_target = defaultdict(int)
    vulns_by_service = defaultdict(int)
    
    for vuln in vulns:
        vulns_by_status[vuln.status] += 1
        if vuln.target:
            vulns_by_target[vuln.target] += 1
        if vuln.service:
            vulns_by_service[vuln.service] += 1
    
    return {
        'scans': {
            'by_type': dict(scans_by_type),
            'by_status': dict(scans_by_status),
            'by_tool': dict(scans_by_tool),
            'total': len(scans)
        },
        'vulnerabilities': {
            'by_status': dict(vulns_by_status),
            'top_targets': dict(sorted(
                vulns_by_target.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
            'by_service': dict(sorted(
                vulns_by_service.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
            'total': len(vulns)
        }
    }

