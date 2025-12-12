"""
Core Module
===========

Componentes core del módulo de reportería:
- FileScanner: Descubre archivos en workspaces
- DataAggregator: Consolida y deduplica findings
- RiskCalculator: Calcula métricas de riesgo
"""

from .file_scanner import FileScanner
from .data_aggregator import DataAggregator
from .risk_calculator import RiskCalculator

__all__ = [
    'FileScanner',
    'DataAggregator',
    'RiskCalculator'
]
