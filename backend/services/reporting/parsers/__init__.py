"""
Parsers Module
==============

Módulo de parsers para diferentes herramientas de seguridad.
Cada parser hereda de BaseParser y maneja un formato específico.
"""

from .base_parser import BaseParser, ParsedFinding
from .parser_manager import ParserManager

__all__ = [
    'BaseParser',
    'ParsedFinding',
    'ParserManager'
]
