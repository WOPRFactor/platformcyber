"""
Repositories Module
===================

Capa de acceso a datos (Data Access Layer).

Patrones:
- Repository Pattern
- Separación de lógica de negocio y acceso a datos
"""

from .user_repository import UserRepository
from .workspace_repository import WorkspaceRepository
from .scan_repository import ScanRepository
from .vulnerability_repository import VulnerabilityRepository
from .report_repository import ReportRepository

__all__ = [
    'UserRepository',
    'WorkspaceRepository',
    'ScanRepository',
    'VulnerabilityRepository',
    'ReportRepository'
]



