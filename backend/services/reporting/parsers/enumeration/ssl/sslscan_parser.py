"""
Parser para SSLScan - SSL/TLS scanner.
Formato: TXT con secciones de ciphers y certificado.
"""

from pathlib import Path
from typing import List
import re
from ...base_parser import BaseParser, ParsedFinding


class SSLScanParser(BaseParser):
    """Parser para archivos de SSLScan."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return 'sslscan' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de SSLScan.
        
        Secciones:
        - Supported Server Cipher(s)
        - SSL Certificate
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            target = None
            weak_ciphers = []
            strong_ciphers = []
            cert_info = {}
            
            for line in lines:
                line_stripped = line.strip()
                
                # Extraer target
                if 'Testing SSL server' in line:
                    match = re.search(r'server\s+([\d\.]+)\s+on port\s+(\d+)', line)
                    if match:
                        target = f"{match.group(1)}:{match.group(2)}"
                
                # Parsear ciphers: Accepted  TLSv1.2  256 bits  ECDHE-RSA-AES256-GCM-SHA384
                if line_stripped.startswith('Accepted'):
                    parts = line_stripped.split()
                    if len(parts) >= 5:
                        protocol = parts[1]
                        bits = parts[2]
                        cipher = parts[4]
                        
                        # Identificar ciphers débiles
                        if 'SSLv' in protocol or 'TLSv1.0' in protocol or 'TLSv1.1' in protocol:
                            weak_ciphers.append(f"{protocol} {cipher}")
                        else:
                            strong_ciphers.append(f"{protocol} {cipher}")
                
                # Extraer info del certificado
                if 'Subject:' in line:
                    match = re.search(r'Subject:\s+(.+)', line)
                    if match:
                        cert_info['subject'] = match.group(1)
                elif 'Issuer:' in line:
                    match = re.search(r'Issuer:\s+(.+)', line)
                    if match:
                        cert_info['issuer'] = match.group(1)
                elif 'Not valid before:' in line:
                    match = re.search(r'Not valid before:\s+(.+)', line)
                    if match:
                        cert_info['valid_from'] = match.group(1)
                elif 'Not valid after:' in line:
                    match = re.search(r'Not valid after:\s+(.+)', line)
                    if match:
                        cert_info['valid_until'] = match.group(1)
            
            # Finding para ciphers débiles
            if weak_ciphers:
                finding = ParsedFinding(
                    title=f"Weak SSL/TLS ciphers supported",
                    severity='medium',
                    description=f"{len(weak_ciphers)} weak cipher suites are supported",
                    category='ssl_enumeration',
                    affected_target=target or 'unknown',
                    evidence=f"Weak ciphers: {', '.join(weak_ciphers[:3])}{'...' if len(weak_ciphers) > 3 else ''}",
                    remediation="Disable weak protocols (SSLv2, SSLv3, TLSv1.0, TLSv1.1) and weak cipher suites",
                    raw_data={
                        'tool': 'sslscan',
                        'type': 'weak_ciphers',
                        'weak_ciphers': weak_ciphers,
                        'target': target
                    }
                )
                findings.append(finding)
            
            # Finding para certificado
            if cert_info:
                finding = ParsedFinding(
                    title=f"SSL Certificate information",
                    severity='info',
                    description=f"Certificate for {cert_info.get('subject', 'unknown')}",
                    category='ssl_enumeration',
                    affected_target=target or 'unknown',
                    evidence=f"Issuer: {cert_info.get('issuer', 'N/A')}, Valid until: {cert_info.get('valid_until', 'N/A')}",
                    raw_data={
                        'tool': 'sslscan',
                        'type': 'certificate',
                        'certificate': cert_info,
                        'target': target
                    }
                )
                findings.append(finding)
            
            # Finding general con resumen
            if strong_ciphers or weak_ciphers:
                finding = ParsedFinding(
                    title=f"SSL/TLS Configuration",
                    severity='info',
                    description=f"SSL/TLS scan completed: {len(strong_ciphers)} strong ciphers, {len(weak_ciphers)} weak ciphers",
                    category='ssl_enumeration',
                    affected_target=target or 'unknown',
                    evidence=f"Total ciphers: {len(strong_ciphers) + len(weak_ciphers)}",
                    raw_data={
                        'tool': 'sslscan',
                        'strong_cipher_count': len(strong_ciphers),
                        'weak_cipher_count': len(weak_ciphers),
                        'target': target
                    }
                )
                findings.append(finding)
            
            self.logger.info(f"SSLScan: Parsed SSL/TLS configuration with {len(weak_ciphers)} weak ciphers")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing SSLScan file {file_path}: {e}")
            return findings



