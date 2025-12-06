"""
JSON Exporter
=============

Exportador de reportes a JSON.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def export_to_json(
    report_data: Dict[str, Any],
    output_dir: Path,
    filename: Optional[str] = None
) -> str:
    """Exporta reporte a JSON."""
    if not filename:
        report_id = report_data.get('metadata', {}).get('report_id', 'report')
        filename = f'{report_id}.json'
    
    output_path = output_dir / filename
    
    with open(output_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    logger.info(f"Report exported to JSON: {output_path}")
    return str(output_path)

