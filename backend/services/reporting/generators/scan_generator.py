"""
Scan Summary Generator
======================

Generador de resumen de scans.
"""

from typing import List, Dict, Any
from models import Scan
from services.reporting.utils.helpers import calculate_duration


def generate_scan_summary(scans: List[Scan]) -> List[Dict[str, Any]]:
    """Genera resumen de scans realizados."""
    summary = []
    
    for scan in scans:
        summary.append({
            'scan_id': scan.id,
            'scan_type': scan.scan_type,
            'target': scan.target,
            'tool': scan.options.get('tool'),
            'status': scan.status,
            'progress': scan.progress,
            'started_at': scan.started_at.isoformat() if scan.started_at else None,
            'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
            'duration': calculate_duration(scan)
        })
    
    # Ordenar por fecha (más reciente primero)
    summary.sort(
        key=lambda x: x['started_at'] or '',
        reverse=True
    )
    
    return summary

