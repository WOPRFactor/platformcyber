"""
Google Dorks Parser
===================

Parser para Google Dorks - Sensitive information disclosure.
Formato: TXT con URLs sensibles encontradas.
"""

from pathlib import Path
from typing import List
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class GoogleDorksParser(BaseParser):
    """Parser para archivos de Google Dorks."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return (('googledork' in filename or 'dork' in filename or 'google' in filename) 
                and file_path.suffix == '.txt')
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de Google Dorks.
        
        Formato:
        https://example.com/admin/config.php
        https://example.com/backup/db_backup.sql
        https://example.com/.env
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con exposiciones sensibles encontradas
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
                
                # Clasificar severidad basado en tipo de archivo/path
                line_lower = line.lower()
                
                # Crítico: backups, credenciales, keys
                if any(kw in line_lower for kw in ['.sql', 'backup', '.env', 'credentials', 
                                                   'password', 'secret', 'key', 'token']):
                    severity = 'critical'
                    remediation = "IMMEDIATE: Remove exposed file and audit for data breach"
                
                # Alto: configuraciones, admin panels
                elif any(kw in line_lower for kw in ['config', 'admin', 'phpinfo', 'web.config', 'htaccess']):
                    severity = 'high'
                    remediation = "Remove or restrict access to configuration files"
                
                # Medio: logs, traces
                elif any(kw in line_lower for kw in ['.log', 'error', 'debug', 'trace']):
                    severity = 'medium'
                    remediation = "Remove or restrict access to log files"
                
                else:
                    severity = 'low'
                    remediation = "Review and remove if sensitive"
                
                finding = ParsedFinding(
                    title=f"Sensitive exposure: {line}",
                    severity=severity,
                    description=f"Potentially sensitive file/path exposed via search engines: {line}",
                    category='information_disclosure',
                    affected_target=line,
                    evidence="Source: Google Dorks",
                    remediation=remediation,
                    raw_data={
                        'tool': 'googledorks',
                        'url': line,
                        'exposure_type': self._classify_exposure(line_lower)
                    }
                )
                findings.append(finding)
            
            logger.info(f"GoogleDorks: Parsed {len(findings)} sensitive exposures")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing GoogleDorks file {file_path}: {e}")
            return findings
    
    def _classify_exposure(self, url: str) -> str:
        """
        Clasifica el tipo de exposición.
        
        Args:
            url: URL en minúsculas
            
        Returns:
            Tipo de exposición
        """
        if '.sql' in url or 'backup' in url:
            return 'database_backup'
        elif '.env' in url or 'config' in url:
            return 'configuration'
        elif 'admin' in url or 'login' in url:
            return 'admin_panel'
        elif '.log' in url:
            return 'log_file'
        else:
            return 'other'


