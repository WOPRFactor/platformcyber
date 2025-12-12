"""
System API Module
=================

Módulo de API para información del sistema y health checks.

Refactorizado: 2025-12-04
"""

from flask import Blueprint
from .routes import register_routes

system_bp = Blueprint('system', __name__)

# Registrar todas las rutas
register_routes(system_bp)


