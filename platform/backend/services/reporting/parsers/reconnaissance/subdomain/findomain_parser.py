"""
Findomain Parser
================

Parser para Findomain - Subdomain enumeration.
Formato: TXT con un subdominio por línea.
"""

from pathlib import Path
from typing import List
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class FindomainParser(BaseParser):
    """Parser para archivos de Findomain."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return 'findomain' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de Findomain.
        
        Formato: Lista simple de subdominios, uno por línea.
        
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
            
            for line in content.strip().split('\n'):
                line = line.strip()
                if not line or '.' not in line:
                    continue
                
                finding = ParsedFinding(
                    title=f"Subdomain discovered: {line}",
                    severity='info',
                    description=f"Subdomain found: {line}",
                    category='reconnaissance',
                    affected_target=line,
                    evidence=f"Source: Findomain",
                    raw_data={'tool': 'findomain', 'subdomain': line}
                )
                findings.append(finding)
            
            logger.info(f"Findomain: Parsed {len(findings)} subdomains")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing Findomain: {e}")
            return findings


