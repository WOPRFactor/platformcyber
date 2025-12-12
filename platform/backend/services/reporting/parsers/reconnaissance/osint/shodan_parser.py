"""
Shodan Parser
=============

Parser para Shodan - Internet-wide scanning.
Formato: JSON con matches (ip_str, port, product, version, vulns).
"""

from pathlib import Path
from typing import List
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class ShodanParser(BaseParser):
    """Parser para archivos JSON de Shodan."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return 'shodan' in filename and file_path.suffix == '.json'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo JSON de Shodan.
        
        Formato:
        {
          "total": 12,
          "matches": [
            {
              "ip_str": "192.0.2.1",
              "port": 443,
              "product": "nginx",
              "version": "1.18.0",
              "os": "Linux",
              "hostnames": ["example.com"],
              "location": {"country_code": "US", "city": "San Francisco"},
              "vulns": ["CVE-2021-44228"]
            }
          ]
        }
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con servicios descubiertos
        """
        findings = []
        
        try:
            data = self._safe_parse_json(file_path)
            if not data:
                return findings
            
            matches = data.get('matches', [])
            
            for match in matches:
                ip = match.get('ip_str', 'unknown')
                port = match.get('port', 0)
                product = match.get('product', 'unknown')
                version = match.get('version', '')
                os = match.get('os', '')
                hostnames = match.get('hostnames', [])
                vulns = match.get('vulns', [])
                
                # Determinar severidad
                if vulns:
                    severity = 'high'  # Tiene vulnerabilidades conocidas
                    title = f"Shodan: {ip}:{port} - {product} with vulnerabilities"
                else:
                    severity = 'info'
                    title = f"Shodan: {ip}:{port} - {product}"
                
                # Construir descripción
                description_parts = [f"Service: {product}"]
                if version:
                    description_parts.append(f"Version: {version}")
                if os:
                    description_parts.append(f"OS: {os}")
                if hostnames:
                    description_parts.append(f"Hostnames: {', '.join(hostnames)}")
                
                description = " | ".join(description_parts)
                
                # Evidencia con vulnerabilidades
                evidence = None
                if vulns:
                    evidence = f"Known vulnerabilities: {', '.join(vulns)}"
                
                # Location info
                location = match.get('location', {})
                location_str = f"{location.get('city', '')}, {location.get('country_code', '')}"
                
                finding = ParsedFinding(
                    title=title,
                    severity=severity,
                    description=description,
                    category='osint',
                    affected_target=f"{ip}:{port}",
                    evidence=evidence,
                    remediation="Review exposed services and patch known vulnerabilities" if vulns else None,
                    cve_id=vulns[0] if vulns else None,
                    references=[f"https://www.shodan.io/host/{ip}"] if ip != 'unknown' else None,
                    raw_data={
                        'tool': 'shodan',
                        'ip': ip,
                        'port': port,
                        'product': product,
                        'version': version,
                        'os': os,
                        'hostnames': hostnames,
                        'vulnerabilities': vulns,
                        'location': location_str,
                        'full_match': match
                    }
                )
                findings.append(finding)
            
            logger.info(f"Shodan: Parsed {len(findings)} service discoveries")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing Shodan file {file_path}: {e}")
            return findings


