"""
Integrations Services Module
============================

Módulo para servicios de integraciones avanzadas:
- Metasploit Framework
- Burp Suite Professional
- Nmap Advanced
- SQLMap
- Gobuster
"""

from .base import BaseIntegrationService
from .integrations_service import IntegrationsService

__all__ = [
    'BaseIntegrationService',
    'IntegrationsService'
]


