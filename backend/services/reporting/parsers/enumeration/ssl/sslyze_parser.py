"""
Parser para SSLyze - Advanced SSL/TLS scanner.
Formato: TXT con secciones por protocolo TLS.
"""

from pathlib import Path
from typing import List
import re
from ...base_parser import BaseParser, ParsedFinding


class SSLyzeParser(BaseParser):
    """Parser para archivos de SSLyze."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return 'sslyze' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de SSLyze.
        
        Secciones:
        - TLS 1.3/1.2 Cipher Suites
        - Certificate Information
        - Session Renegotiation
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            target = None
            current_protocol = None
            weak_ciphers = []
            cert_info = {}
            renegotiation_secure = False
            
            for line in lines:
                line_stripped = line.strip()
                
                # Extraer target
                if 'SCAN RESULTS FOR' in line:
                    match = re.search(r'FOR\s+([\d\.]+:\d+)', line)
                    if match:
                        target = match.group(1)
                
                # Detectar protocolo
                if '* TLS' in line:
                    match = re.search(r'\* TLS ([\d\.]+)', line)
                    if match:
                        current_protocol = f"TLS {match.group(1)}"
                
                # Parsear ciphers aceptados
                if line_stripped.startswith('TLS_') or line_stripped.startswith('SSL_'):
                    cipher = line_stripped.split()[0]
                    
                    # Identificar ciphers débiles
                    if any(weak in cipher.upper() for weak in ['DES', 'RC4', 'MD5', 'EXPORT', 'NULL']):
                        weak_ciphers.append(f"{current_protocol} {cipher}")
                
                # Certificate info
                if 'Common Name:' in line:
                    match = re.search(r'Common Name:\s+(.+)', line)
                    if match:
                        cert_info['common_name'] = match.group(1)
                elif 'Issuer:' in line:
                    match = re.search(r'Issuer:\s+(.+)', line)
                    if match:
                        cert_info['issuer'] = match.group(1)
                elif 'Not After:' in line:
                    match = re.search(r'Not After:\s+(.+)', line)
                    if match:
                        cert_info['expiry'] = match.group(1)
                elif 'Key Size:' in line:
                    match = re.search(r'Key Size:\s+(\d+)', line)
                    if match:
                        cert_info['key_size'] = int(match.group(1))
                
                # Renegotiation
                if 'Secure Renegotiation:' in line:
                    renegotiation_secure = 'Supported' in line
            
            # Finding para weak ciphers
            if weak_ciphers:
                finding = ParsedFinding(
                    title=f"Weak SSL/TLS ciphers detected",
                    severity='high',
                    description=f"{len(weak_ciphers)} weak cipher suites supported",
                    category='ssl_vulnerability',
                    affected_target=target or 'unknown',
                    evidence=f"Weak ciphers: {', '.join(weak_ciphers)}",
                    remediation="Disable weak cipher suites containing DES, RC4, MD5, EXPORT, or NULL",
                    cve_id="CVE-2015-0204" if any('EXPORT' in c for c in weak_ciphers) else None,
                    raw_data={
                        'tool': 'sslyze',
                        'weak_ciphers': weak_ciphers,
                        'target': target
                    }
                )
                findings.append(finding)
            
            # Finding para key size débil
            if cert_info.get('key_size') and cert_info['key_size'] < 2048:
                finding = ParsedFinding(
                    title=f"Weak RSA key size: {cert_info['key_size']} bits",
                    severity='medium',
                    description=f"Certificate uses RSA key size of {cert_info['key_size']} bits (minimum recommended: 2048 bits)",
                    category='ssl_vulnerability',
                    affected_target=target or 'unknown',
                    evidence=f"Key size: {cert_info['key_size']} bits",
                    remediation="Replace certificate with one using at least 2048-bit RSA key",
                    raw_data={
                        'tool': 'sslyze',
                        'key_size': cert_info['key_size'],
                        'target': target
                    }
                )
                findings.append(finding)
            
            # Finding para insecure renegotiation
            if not renegotiation_secure:
                finding = ParsedFinding(
                    title=f"Insecure TLS renegotiation",
                    severity='medium',
                    description="Server does not support secure renegotiation",
                    category='ssl_vulnerability',
                    affected_target=target or 'unknown',
                    evidence="Secure renegotiation: Not supported",
                    remediation="Enable secure renegotiation on the server",
                    cve_id="CVE-2009-3555",
                    raw_data={
                        'tool': 'sslyze',
                        'secure_renegotiation': renegotiation_secure,
                        'target': target
                    }
                )
                findings.append(finding)
            
            self.logger.info(f"SSLyze: Parsed SSL/TLS scan with {len(findings)} findings")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing SSLyze file {file_path}: {e}")
            return findings


