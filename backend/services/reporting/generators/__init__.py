"""
Reporting Generators Package
============================

Módulos para generación de secciones de reportes.
"""

from .metadata_generator import generate_metadata
from .executive_generator import generate_executive_summary
from .statistics_generator import generate_statistics
from .vulnerability_generator import generate_vulnerability_breakdown
from .scan_generator import generate_scan_summary
from .technical_generator import generate_technical_details, generate_timeline
from .compliance_generator import generate_compliance_mapping
from .remediation_generator import generate_remediation_roadmap, generate_risk_assessment

__all__ = [
    'generate_metadata',
    'generate_executive_summary',
    'generate_statistics',
    'generate_vulnerability_breakdown',
    'generate_scan_summary',
    'generate_technical_details',
    'generate_timeline',
    'generate_compliance_mapping',
    'generate_remediation_roadmap',
    'generate_risk_assessment'
]

