"""
Web Crawler Parser
==================

Parser para Web Crawlers (Gospider, Hakrawler) - URL discovery.
Formato: TXT con lista de URLs encontradas.
"""

from pathlib import Path
from typing import List
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class WebCrawlerParser(BaseParser):
    """Parser para archivos de web crawlers (Gospider, Hakrawler)."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return (('gospider' in filename or 'hakrawler' in filename or 
                 'crawler' in filename or 'crawl' in filename) 
                and file_path.suffix == '.txt')
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de web crawler.
        
        Formato:
        https://example.com/
        https://example.com/api/v1/users
        https://example.com/admin/login
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con URLs descubiertas
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.strip().split('\n')
            sensitive_paths = []
            api_endpoints = []
            static_resources = []
            
            for line in lines:
                line = line.strip()
                if not line or not line.startswith('http'):
                    continue
                
                # Clasificar URLs
                line_lower = line.lower()
                
                # URLs sensibles (admin, config, backup, etc)
                sensitive_keywords = ['admin', 'login', 'config', 'backup', 'password', 
                                     'credential', 'secret', '.env', 'db_']
                if any(keyword in line_lower for keyword in sensitive_keywords):
                    sensitive_paths.append(line)
                    severity = 'medium'
                    category = 'web_vulnerability'
                    description = f"Potentially sensitive path found: {line}"
                
                # API endpoints
                elif '/api/' in line_lower or '/v1/' in line_lower or '/v2/' in line_lower:
                    api_endpoints.append(line)
                    severity = 'info'
                    category = 'web_reconnaissance'
                    description = f"API endpoint discovered: {line}"
                
                # Recursos estáticos (bajo interés)
                elif any(ext in line_lower for ext in ['.jpg', '.png', '.gif', '.css', '.js', '.svg', '.woff']):
                    static_resources.append(line)
                    continue  # No crear finding para recursos estáticos
                
                else:
                    severity = 'info'
                    category = 'web_reconnaissance'
                    description = f"URL discovered: {line}"
                
                finding = ParsedFinding(
                    title=f"Crawled URL: {line}",
                    severity=severity,
                    description=description,
                    category=category,
                    affected_target=line,
                    evidence="Source: Web crawler",
                    remediation="Review access controls for sensitive paths" if severity == 'medium' else None,
                    raw_data={
                        'tool': 'webcrawler',
                        'url': line,
                        'is_sensitive': severity == 'medium',
                        'is_api': '/api/' in line_lower
                    }
                )
                findings.append(finding)
            
            logger.info(f"WebCrawler: Parsed {len(findings)} URLs ({len(sensitive_paths)} sensitive, {len(api_endpoints)} API)")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing WebCrawler file {file_path}: {e}")
            return findings


