"""
Parser para RustScan - Fast port scanner.
Formato: TXT con output similar a Nmap.
"""

from pathlib import Path
from typing import List
import re
from ..base_parser import BaseParser, ParsedFinding


class RustScanParser(BaseParser):
    """Parser para archivos de RustScan."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return 'rustscan' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de RustScan.
        
        Formato esperado (TXT):
        Nmap scan report for 192.168.1.1
        Host is up (0.05s latency).
        
        PORT   STATE SERVICE VERSION
        22/tcp open  ssh     OpenSSH 8.2p1
        80/tcp open  http    Apache httpd 2.4.41
        443/tcp open  ssl/http Apache httpd 2.4.41
        
        O formato grepeable:
        Host: 192.168.1.1 (up) Ports: 22/open/tcp//ssh///, 80/open/tcp//http///
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            current_host = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Extraer host target
                if 'Nmap scan report for' in line or 'scan report for' in line.lower():
                    match = re.search(r'for\s+([\d\.]+)', line)
                    if match:
                        current_host = match.group(1)
                    continue
                
                # Parsear formato tabla: PORT   STATE SERVICE VERSION
                port_match = re.match(r'^(\d+)/(tcp|udp)\s+(open|closed|filtered)\s+(\S+)(?:\s+(.+))?', line)
                if port_match:
                    port = int(port_match.group(1))
                    protocol = port_match.group(2)
                    state = port_match.group(3)
                    service = port_match.group(4)
                    version = port_match.group(5) if port_match.group(5) else ''
                    
                    if state == 'open':
                        severity = 'info'
                        title = f"Open port: {port}/{protocol} ({service})"
                        description = f"Port {port}/{protocol} is open running {service}"
                        if version:
                            description += f" {version}"
                        
                        finding = ParsedFinding(
                            title=title,
                            severity=severity,
                            description=description,
                            category='port_scanning',
                            affected_target=f"{current_host or 'unknown'}:{port}",
                            evidence=f"Service: {service}, Version: {version}" if version else f"Service: {service}",
                            raw_data={
                                'tool': 'rustscan',
                                'host': current_host,
                                'port': port,
                                'protocol': protocol,
                                'state': state,
                                'service': service,
                                'version': version
                            }
                        )
                        findings.append(finding)
                
                # Parsear formato grepeable: Host: IP (up) Ports: 22/open/tcp//ssh///
                elif line.startswith('Host:'):
                    match = re.search(r'Host:\s+([\d\.]+).*Ports:\s+(.+)', line)
                    if match:
                        host = match.group(1)
                        ports_str = match.group(2)
                        
                        # Parsear cada puerto: 22/open/tcp//ssh///
                        port_entries = ports_str.split(',')
                        for entry in port_entries:
                            parts = entry.strip().split('/')
                            if len(parts) >= 6:
                                port = int(parts[0])
                                state = parts[1]
                                protocol = parts[2]
                                service = parts[4] if parts[4] else 'unknown'
                                
                                if state == 'open':
                                    finding = ParsedFinding(
                                        title=f"Open port: {port}/{protocol} ({service})",
                                        severity='info',
                                        description=f"Port {port}/{protocol} is open running {service}",
                                        category='port_scanning',
                                        affected_target=f"{host}:{port}",
                                        evidence=f"Service: {service}",
                                        raw_data={
                                            'tool': 'rustscan',
                                            'host': host,
                                            'port': port,
                                            'protocol': protocol,
                                            'state': state,
                                            'service': service
                                        }
                                    )
                                    findings.append(finding)
            
            self.logger.info(f"RustScan: Parsed {len(findings)} open ports")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing RustScan file {file_path}: {e}")
            return findings

