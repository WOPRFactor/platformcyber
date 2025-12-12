"""
Sublist3r Parser
================

Parser para Sublist3r - Subdomain enumeration.
Formato: TXT con un subdominio por línea (idéntico a Assetfinder).
"""

from pathlib import Path
from typing import List
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class Sublist3rParser(BaseParser):
    """Parser para archivos de Sublist3r."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return 'sublist3r' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de Sublist3r.
        
        Formato idéntico a Assetfinder.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con subdominios encontrados
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                if not line or line.startswith('#') or '.' not in line:
                    continue
                
                finding = ParsedFinding(
                    title=f"Subdomain discovered: {line}",
                    severity='info',
                    description=f"Subdomain enumeration found: {line}",
                    category='reconnaissance',
                    affected_target=line,
                    evidence=f"Source: Sublist3r",
                    raw_data={
                        'tool': 'sublist3r',
                        'subdomain': line,
                        'type': 'subdomain_enumeration'
                    }
                )
                findings.append(finding)
            
            logger.info(f"Sublist3r: Parsed {len(findings)} subdomains")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing Sublist3r file {file_path}: {e}")
            return findings


