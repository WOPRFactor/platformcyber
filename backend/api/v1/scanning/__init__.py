"""
Scanning API Module
===================

Módulo de API para escaneos de puertos y servicios.
"""

from flask import Blueprint
from .routes import (
    scan_routes,
    nmap_routes,
    rustscan_routes,
    masscan_routes,
    naabu_routes,
    smb_enum_routes,
    network_enum_routes,
    database_enum_routes,
    ssl_enum_routes,
    preview_routes
)

scanning_bp = Blueprint('scanning', __name__)

# Registrar todas las rutas
scan_routes.register_routes(scanning_bp)
nmap_routes.register_routes(scanning_bp)
rustscan_routes.register_routes(scanning_bp)
masscan_routes.register_routes(scanning_bp)
naabu_routes.register_routes(scanning_bp)
smb_enum_routes.register_routes(scanning_bp)
network_enum_routes.register_routes(scanning_bp)
database_enum_routes.register_routes(scanning_bp)
ssl_enum_routes.register_routes(scanning_bp)
preview_routes.register_routes(scanning_bp)


