"""
TheHarvester Parser
===================

Parser para theHarvester - OSINT gathering (emails, hosts, IPs).
Formato: JSON con hosts, emails, ips, urls.
"""

from pathlib import Path
from typing import List
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class TheHarvesterParser(BaseParser):
    """Parser para archivos JSON de theHarvester."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return ('theharvester' in filename or 'harvester' in filename) and file_path.suffix == '.json'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo JSON de theHarvester.
        
        Formato:
        {
          "hosts": ["www.example.com", "api.example.com"],
          "emails": ["admin@example.com"],
          "ips": ["192.0.2.1"],
          "urls": ["https://www.example.com"],
          "interesting_urls": ["https://example.com/admin"]
        }
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con información OSINT encontrada
        """
        findings = []
        
        try:
            data = self._safe_parse_json(file_path)
            if not data:
                return findings
            
            # Parsear hosts
            hosts = data.get('hosts', [])
            for host in hosts:
                finding = ParsedFinding(
                    title=f"Host discovered: {host}",
                    severity='info',
                    description=f"Host found via OSINT: {host}",
                    category='reconnaissance',
                    affected_target=host,
                    evidence="Source: theHarvester OSINT",
                    raw_data={'tool': 'theharvester', 'type': 'host', 'value': host}
                )
                findings.append(finding)
            
            # Parsear emails
            emails = data.get('emails', [])
            for email in emails:
                finding = ParsedFinding(
                    title=f"Email discovered: {email}",
                    severity='info',
                    description=f"Email address found: {email}",
                    category='osint',
                    affected_target=email,
                    evidence="Source: theHarvester OSINT",
                    remediation="Verify email exposure and consider SPF/DMARC policies",
                    raw_data={'tool': 'theharvester', 'type': 'email', 'value': email}
                )
                findings.append(finding)
            
            # Parsear IPs
            ips = data.get('ips', [])
            for ip in ips:
                finding = ParsedFinding(
                    title=f"IP address: {ip}",
                    severity='info',
                    description=f"IP address associated with target: {ip}",
                    category='reconnaissance',
                    affected_target=ip,
                    evidence="Source: theHarvester OSINT",
                    raw_data={'tool': 'theharvester', 'type': 'ip', 'value': ip}
                )
                findings.append(finding)
            
            # Parsear interesting URLs
            interesting_urls = data.get('interesting_urls', [])
            for url in interesting_urls:
                finding = ParsedFinding(
                    title=f"Interesting URL: {url}",
                    severity='low',  # Potentially sensitive
                    description=f"Potentially sensitive URL found: {url}",
                    category='osint',
                    affected_target=url,
                    evidence="Source: theHarvester OSINT",
                    remediation="Review access controls for sensitive paths",
                    raw_data={'tool': 'theharvester', 'type': 'interesting_url', 'value': url}
                )
                findings.append(finding)
            
            logger.info(f"theHarvester: Parsed {len(findings)} OSINT findings")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing theHarvester file {file_path}: {e}")
            return findings


