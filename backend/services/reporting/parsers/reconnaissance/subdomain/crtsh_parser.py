"""
crt.sh Parser
=============

Parser para crt.sh - Certificate Transparency logs.
Formato: TXT con subdominios obtenidos de certificados SSL/TLS.
"""

from pathlib import Path
from typing import List
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class CrtshParser(BaseParser):
    """Parser para archivos de crt.sh."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return ('crtsh' in filename or 'crt.sh' in filename) and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de crt.sh.
        
        Formato: Lista de subdominios (puede incluir wildcards).
        
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
                    title=f"Subdomain from certificate: {line}",
                    severity='info',
                    description=f"Subdomain found in CT logs: {line}",
                    category='reconnaissance',
                    affected_target=line,
                    evidence=f"Source: crt.sh (Certificate Transparency)",
                    raw_data={'tool': 'crtsh', 'subdomain': line}
                )
                findings.append(finding)
            
            logger.info(f"crt.sh: Parsed {len(findings)} subdomains")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing crt.sh: {e}")
            return findings


