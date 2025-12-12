"""
Fierce Parser
=============

Parser para Fierce - DNS reconnaissance.
Formato: TXT con estructura de NS, SOA, subdominios encontrados.
"""

from pathlib import Path
from typing import List
import re
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class FierceParser(BaseParser):
    """Parser para archivos de Fierce."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return 'fierce' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de Fierce.
        
        Formato esperado:
        NS: ns1.example.com. ns2.example.com.
        SOA: ns1.example.com. (192.0.2.1)
        Zone: failure
        Wildcard: failure
        Found: ftp.example.com. (192.0.2.10)
        Nearby:
        {'192.0.2.9': 'server1.example.com.'}
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con información DNS encontrada
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            domain_base = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Extraer Name Servers
                if line.startswith('NS:'):
                    ns_servers = line.replace('NS:', '').strip().split()
                    for ns in ns_servers:
                        ns = ns.rstrip('.')
                        finding = ParsedFinding(
                            title=f"Name Server: {ns}",
                            severity='info',
                            description=f"Name server discovered: {ns}",
                            category='dns_enumeration',
                            affected_target=ns,
                            evidence="Source: Fierce DNS scan",
                            raw_data={'tool': 'fierce', 'type': 'NS', 'server': ns}
                        )
                        findings.append(finding)
                
                # Extraer SOA
                elif line.startswith('SOA:'):
                    match = re.search(r'SOA:\s+([\w\.\-]+)\.?\s+\(([\d\.]+)\)', line)
                    if match:
                        soa_server = match.group(1)
                        soa_ip = match.group(2)
                        finding = ParsedFinding(
                            title=f"SOA Record: {soa_server}",
                            severity='info',
                            description=f"SOA server: {soa_server} ({soa_ip})",
                            category='dns_enumeration',
                            affected_target=soa_server,
                            evidence=f"IP: {soa_ip}",
                            raw_data={'tool': 'fierce', 'type': 'SOA', 'server': soa_server, 'ip': soa_ip}
                        )
                        findings.append(finding)
                
                # Extraer subdominios encontrados
                elif line.startswith('Found:'):
                    match = re.search(r'Found:\s+([\w\.\-]+)\.?\s+\(([\d\.]+)\)', line)
                    if match:
                        subdomain = match.group(1)
                        ip = match.group(2)
                        finding = ParsedFinding(
                            title=f"Subdomain discovered: {subdomain}",
                            severity='info',
                            description=f"Subdomain found via DNS bruteforce: {subdomain}",
                            category='reconnaissance',
                            affected_target=subdomain,
                            evidence=f"IP: {ip}",
                            raw_data={'tool': 'fierce', 'type': 'subdomain', 'domain': subdomain, 'ip': ip}
                        )
                        findings.append(finding)
                
                # Extraer IPs cercanas (nearby)
                elif "'" in line and ':' in line:
                    # Parsear diccionario Python: {'192.0.2.9': 'server1.example.com.'}
                    match = re.search(r"'([\d\.]+)':\s+'([\w\.\-]+)'", line)
                    if match:
                        ip = match.group(1)
                        hostname = match.group(2).rstrip('.')
                        finding = ParsedFinding(
                            title=f"Nearby host: {hostname}",
                            severity='info',
                            description=f"Nearby IP found: {ip} → {hostname}",
                            category='reconnaissance',
                            affected_target=hostname,
                            evidence=f"IP: {ip}",
                            raw_data={'tool': 'fierce', 'type': 'nearby', 'ip': ip, 'hostname': hostname}
                        )
                        findings.append(finding)
            
            logger.info(f"Fierce: Parsed {len(findings)} DNS findings")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing Fierce file {file_path}: {e}")
            return findings


