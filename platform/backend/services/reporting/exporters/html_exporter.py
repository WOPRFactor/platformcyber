"""
HTML Exporter
=============

Exportador de reportes a HTML.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_html_report(report_data: Dict[str, Any]) -> str:
    """Genera HTML del reporte."""
    # HTML básico (se puede mejorar con templates)
    metadata = report_data.get('metadata', {})
    exec_summary = report_data.get('executive_summary', {})
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Penetration Testing Report - {metadata.get('report_id')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
        .severity-critical {{ color: #d32f2f; font-weight: bold; }}
        .severity-high {{ color: #f57c00; font-weight: bold; }}
        .severity-medium {{ color: #fbc02d; font-weight: bold; }}
        .severity-low {{ color: #388e3c; font-weight: bold; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Penetration Testing Report</h1>
    <p><strong>Report ID:</strong> {metadata.get('report_id')}</p>
    <p><strong>Generated:</strong> {metadata.get('generated_at')}</p>
    
    <h2>Executive Summary</h2>
    <p><strong>Total Vulnerabilities:</strong> {exec_summary.get('total_vulnerabilities')}</p>
    <p><strong>Risk Level:</strong> <span class="severity-{exec_summary.get('risk_level', '').lower()}">{exec_summary.get('risk_level')}</span></p>
    <p><strong>Risk Score:</strong> {exec_summary.get('risk_score')}</p>
    
    <h3>Severity Distribution</h3>
    <ul>
        {"".join([f"<li class='severity-{sev}'>{sev.capitalize()}: {count}</li>" for sev, count in exec_summary.get('severity_distribution', {}).items()])}
    </ul>
    
    <h2>Detailed Report</h2>
    <p>For complete technical details, please refer to the JSON export.</p>
</body>
</html>
"""
    return html


def export_to_html(
    report_data: Dict[str, Any],
    output_dir: Path,
    filename: Optional[str] = None
) -> str:
    """Exporta reporte a HTML."""
    if not filename:
        report_id = report_data.get('metadata', {}).get('report_id', 'report')
        filename = f'{report_id}.html'
    
    output_path = output_dir / filename
    
    html_content = generate_html_report(report_data)
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    logger.info(f"Report exported to HTML: {output_path}")
    return str(output_path)

