"""
System API Routes
=================

Módulos de rutas para la API del sistema.
"""

from flask import Blueprint

def register_routes(bp: Blueprint):
    """Registra todas las rutas del sistema."""
    from .health_routes import register_routes as register_health_routes
    from .metrics_routes import register_routes as register_metrics_routes
    from .scans_routes import register_routes as register_scans_routes
    from .console_routes import register_routes as register_console_routes
    from .network_routes import register_routes as register_network_routes
    
    register_health_routes(bp)
    register_metrics_routes(bp)
    register_scans_routes(bp)
    register_console_routes(bp)
    register_network_routes(bp)


