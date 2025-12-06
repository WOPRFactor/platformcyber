"""
API v1 Blueprints
=================

Blueprints para la API versión 1.
"""

from .auth import auth_bp
from .reconnaissance import reconnaissance_bp
from .scanning import scanning_bp  # Importa desde módulo refactorizado
from .vulnerability import vulnerability_bp
from .exploitation import exploitation_bp  # Importa desde módulo refactorizado
from .post_exploitation import post_exploitation_bp
from .active_directory import active_directory_bp
from .cloud import cloud_bp
from .api_testing import api_testing_bp
from .mobile import mobile_bp
from .container import container_bp
from .reporting import reporting_bp
from .workspaces import workspaces_bp  # Importa desde módulo refactorizado
from .system import system_bp
from .owasp import owasp_bp
from .advanced import advanced_bp
from .mitre import mitre_bp

__all__ = [
    'auth_bp',
    'reconnaissance_bp',
    'scanning_bp',
    'vulnerability_bp',
    'exploitation_bp',
    'post_exploitation_bp',
    'active_directory_bp',
    'cloud_bp',
    'api_testing_bp',
    'mobile_bp',
    'container_bp',
    'reporting_bp',
    'workspaces_bp',
    'system_bp',
    'owasp_bp',
    'advanced_bp',
    'mitre_bp'
]



