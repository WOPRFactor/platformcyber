"""
Workspaces API Module
====================

Módulo de API para gestión de workspaces.
"""

from flask import Blueprint
from .routes import crud_routes, logs_routes, sessions_routes, evidence_routes, files_routes, dashboard_routes

workspaces_bp = Blueprint('workspaces', __name__, url_prefix='/workspaces')

# Registrar todas las rutas
crud_routes.register_routes(workspaces_bp)
logs_routes.register_routes(workspaces_bp)
sessions_routes.register_routes(workspaces_bp)
evidence_routes.register_routes(workspaces_bp)
files_routes.register_routes(workspaces_bp)
dashboard_routes.register_routes(workspaces_bp)


