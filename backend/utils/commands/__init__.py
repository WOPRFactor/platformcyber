"""
Safe Command Builders
=====================

Constructores de comandos seguros para herramientas de pentesting.

Cada builder:
- Aplica rate limiting
- Previene opciones peligrosas
- Valida inputs
- Retorna comandos listos para subprocess.run()
"""

from .safe_nmap import SafeNmap
from .safe_sqlmap import SafeSQLMap
from .safe_masscan import SafeMasscan
from .safe_hydra import SafeHydra

__all__ = ['SafeNmap', 'SafeSQLMap', 'SafeMasscan', 'SafeHydra']



