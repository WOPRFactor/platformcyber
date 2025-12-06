"""
Reconnaissance API
==================

Endpoints para reconocimiento y OSINT.

Este archivo exporta el blueprint principal que ya tiene todos los
sub-blueprints registrados.
"""

# Importar el blueprint principal (ya tiene todos los sub-blueprints registrados)
from .reconnaissance_endpoints import reconnaissance_bp

# Exportar el blueprint principal
__all__ = ['reconnaissance_bp']
