"""
Metadata Generator
==================

Generador de metadata para reportes.
"""

from typing import Dict, Any
from datetime import datetime
from models import Workspace


def generate_metadata(workspace: Workspace, report_type: str) -> Dict[str, Any]:
    """Genera metadata del reporte."""
    return {
        'report_id': f'RPT-{workspace.id}-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}',
        'report_type': report_type,
        'workspace': {
            'id': workspace.id,
            'name': workspace.name,
            'description': workspace.description
        },
        'generated_at': datetime.utcnow().isoformat(),
        'generated_by': 'dev3-refactor Pentesting Platform',
        'version': '1.0.0'
    }

