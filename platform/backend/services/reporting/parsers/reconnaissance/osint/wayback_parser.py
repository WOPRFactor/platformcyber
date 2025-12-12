"""
Wayback Machine Parser
=======================

Parser para Wayback Machine - Historical URL snapshots.
Formato: TXT con URLs que incluyen timestamp.
"""

from pathlib import Path
from typing import List
import re
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class WaybackParser(BaseParser):
    """Parser para archivos de Wayback Machine."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return 'wayback' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de Wayback Machine.
        
        Formato:
        https://web.archive.org/web/20200101/http://example.com/
        https://web.archive.org/web/20200615/http://example.com/admin
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con URLs históricas encontradas
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or not line.startswith('http'):
                    continue
                
                # Extraer timestamp y URL original
                # Formato: https://web.archive.org/web/YYYYMMDD/ORIGINAL_URL
                match = re.search(r'web\.archive\.org/web/(\d+)/(https?://[^\s]+)', line)
                if match:
                    timestamp = match.group(1)
                    original_url = match.group(2)
                    
                    # Identificar URLs potencialmente sensibles
                    sensitive_keywords = ['admin', 'login', 'config', 'backup', 'password', 'api', 'key']
                    is_sensitive = any(keyword in original_url.lower() for keyword in sensitive_keywords)
                    
                    severity = 'low' if is_sensitive else 'info'
                    
                    finding = ParsedFinding(
                        title=f"Historical URL: {original_url}",
                        severity=severity,
                        description=f"URL found in Wayback Machine (snapshot: {timestamp})",
                        category='osint',
                        affected_target=original_url,
                        evidence=f"Archive URL: {line}",
                        remediation="Review historical exposure and verify current access controls" if is_sensitive else None,
                        raw_data={
                            'tool': 'wayback',
                            'timestamp': timestamp,
                            'original_url': original_url,
                            'archive_url': line,
                            'is_sensitive': is_sensitive
                        }
                    )
                    findings.append(finding)
            
            logger.info(f"Wayback Machine: Parsed {len(findings)} historical URLs")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing Wayback file {file_path}: {e}")
            return findings


