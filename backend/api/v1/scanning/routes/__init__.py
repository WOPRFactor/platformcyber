"""
Scanning Routes
===============

Módulo de rutas para escaneos.
"""

from .scan_routes import register_routes as register_scan_routes
from .nmap_routes import register_routes as register_nmap_routes
from .rustscan_routes import register_routes as register_rustscan_routes
from .masscan_routes import register_routes as register_masscan_routes
from .naabu_routes import register_routes as register_naabu_routes
from .smb_enum_routes import register_routes as register_smb_enum_routes
from .network_enum_routes import register_routes as register_network_enum_routes
from .database_enum_routes import register_routes as register_database_enum_routes
from .ssl_enum_routes import register_routes as register_ssl_enum_routes
from .preview_routes import register_routes as register_preview_routes

__all__ = [
    'scan_routes',
    'nmap_routes',
    'rustscan_routes',
    'masscan_routes',
    'naabu_routes',
    'smb_enum_routes',
    'network_enum_routes',
    'database_enum_routes',
    'ssl_enum_routes',
    'preview_routes'
]


