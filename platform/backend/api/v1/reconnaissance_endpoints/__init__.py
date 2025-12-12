"""
Reconnaissance Endpoints Package
=================================

Módulos de endpoints para reconocimiento y OSINT.
"""

from flask import Blueprint

# Crear blueprint principal (se registra en app.py con url_prefix)
reconnaissance_bp = Blueprint('reconnaissance', __name__)

# Importar y registrar sub-blueprints
from .subdomain_routes import subdomain_bp
from .dns_routes import dns_bp
from .email_routes import email_bp
from .osint_routes import osint_bp
from .web_crawling_routes import webcrawl_bp
from .secrets_routes import secrets_bp
from .google_dorks_routes import googledorks_bp
from .complete_routes import complete_bp
from .scan_routes import scan_bp

# Registrar todos los sub-blueprints
reconnaissance_bp.register_blueprint(subdomain_bp)
reconnaissance_bp.register_blueprint(dns_bp)
reconnaissance_bp.register_blueprint(email_bp)
reconnaissance_bp.register_blueprint(osint_bp)
reconnaissance_bp.register_blueprint(webcrawl_bp)
reconnaissance_bp.register_blueprint(secrets_bp)
reconnaissance_bp.register_blueprint(googledorks_bp)
reconnaissance_bp.register_blueprint(complete_bp)
reconnaissance_bp.register_blueprint(scan_bp)

