"""
Base Parser
===========

Clase base abstracta para todos los parsers del módulo de reportería.
Define la interfaz común y métodos helper para manejo de archivos.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging
import json


@dataclass
class ParsedFinding:
    """
    Estructura estándar para un hallazgo parseado.
    
    Todos los parsers deben convertir sus resultados a este formato
    para permitir consolidación y deduplicación.
    """
    title: str
    severity: str  # critical, high, medium, low, info
    description: str
    category: str
    affected_target: str
    evidence: Optional[str] = None
    remediation: Optional[str] = None
    cvss_score: Optional[float] = None
    cve_id: Optional[str] = None
    references: Optional[List[str]] = field(default_factory=list)
    raw_data: Optional[Dict[str, Any]] = field(default_factory=dict)


class BaseParser(ABC):
    """
    Clase base abstracta para todos los parsers.
    
    Cada parser debe implementar:
    - can_parse(): Verifica si puede procesar un archivo
    - parse(): Parsea el archivo y retorna lista de ParsedFinding
    """
    
    def __init__(self):
        """Inicializa el parser con un logger específico."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si este parser puede manejar el archivo.
        
        Args:
            file_path: Ruta al archivo a evaluar
            
        Returns:
            True si el parser puede procesar el archivo
        """
        pass
    
    @abstractmethod
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea el archivo y retorna lista de findings.
        
        Args:
            file_path: Ruta al archivo a parsear
            
        Returns:
            Lista de ParsedFinding (puede estar vacía si no hay findings)
        """
        pass
    
    def _read_file(self, file_path: Path, encoding: str = 'utf-8') -> str:
        """
        Lee archivo con manejo robusto de encoding.
        
        Intenta UTF-8 primero, luego latin-1 como fallback.
        Retorna string vacío si falla completamente.
        
        Args:
            file_path: Ruta al archivo
            encoding: Encoding a usar (default: utf-8)
            
        Returns:
            Contenido del archivo como string
        """
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            self.logger.warning(
                f"UTF-8 decode failed for {file_path}, trying latin-1"
            )
            try:
                return file_path.read_text(encoding='latin-1')
            except Exception as e:
                self.logger.error(f"Failed to read {file_path}: {e}")
                return ""
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return ""
    
    def _safe_parse_json(self, file_path: Path) -> Optional[Dict]:
        """
        Parsea JSON con manejo robusto de errores.
        
        Args:
            file_path: Ruta al archivo JSON
            
        Returns:
            Diccionario parseado o None si falla
        """
        try:
            content = self._read_file(file_path)
            if not content:
                return None
            return json.loads(content)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error in {file_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error parsing JSON {file_path}: {e}")
            return None
    
    def _validate_file_size(self, file_path: Path, max_size: int) -> bool:
        """
        Valida que el archivo no exceda el tamaño máximo.
        
        Args:
            file_path: Ruta al archivo
            max_size: Tamaño máximo en bytes
            
        Returns:
            True si el archivo es válido, False si excede el límite
        """
        try:
            size = file_path.stat().st_size
            if size > max_size:
                self.logger.warning(
                    f"File {file_path} exceeds max size: {size} > {max_size}"
                )
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error checking file size for {file_path}: {e}")
            return False
