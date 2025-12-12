"""
Assetfinder Parser
==================

Parser para Assetfinder - Subdomain enumeration.
Formato: TXT con un subdominio por línea.
"""

from pathlib import Path
from typing import List
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class AssetfinderParser(BaseParser):
    """Parser para archivos de Assetfinder."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Criterios:
        - Nombre contiene 'assetfinder'
        - Extensión .txt
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return 'assetfinder' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de Assetfinder.
        
        Formato esperado (TXT):
        subdomain1.example.com
        subdomain2.example.com
        api.example.com
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con subdominios encontrados
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                logger.warning(f"Empty file: {file_path}")
                return findings
            
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Saltar líneas vacías o comentarios
                if not line or line.startswith('#'):
                    continue
                
                # Validar que parece un dominio (contiene punto)
                if '.' not in line:
                    continue
                
                # Crear finding
                finding = ParsedFinding(
                    title=f"Subdomain discovered: {line}",
                    severity='info',
                    description=f"Subdomain enumeration found: {line}",
                    category='reconnaissance',
                    affected_target=line,
                    evidence=f"Source: Assetfinder",
                    remediation=None,
                    cvss_score=None,
                    cve_id=None,
                    references=None,
                    raw_data={
                        'tool': 'assetfinder',
                        'subdomain': line,
                        'type': 'subdomain_enumeration'
                    }
                )
                findings.append(finding)
            
            logger.info(f"Assetfinder: Parsed {len(findings)} subdomains from {file_path}")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing Assetfinder file {file_path}: {e}")
            return findings


