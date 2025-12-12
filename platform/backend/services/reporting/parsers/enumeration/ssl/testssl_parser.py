"""
Parser para testssl.sh - Comprehensive SSL/TLS scanner.
Formato: JSON con protocols, ciphers, vulnerabilities.
"""

from pathlib import Path
from typing import List
from ...base_parser import BaseParser, ParsedFinding


class TestSSLParser(BaseParser):
    """Parser para archivos JSON de testssl.sh."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return 'testssl' in filename and file_path.suffix == '.json'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo JSON de testssl.sh.
        """
        findings = []
        
        try:
            data = self._safe_parse_json(file_path)
            if not data:
                return findings
            
            target = data.get('target', 'unknown')
            protocols = data.get('protocols', {})
            ciphers = data.get('ciphers', [])
            
            # Check for weak protocols
            weak_protocols = []
            for protocol, status in protocols.items():
                if status == 'offered':
                    if any(weak in protocol for weak in ['SSLv2', 'SSLv3', 'TLSv1.0', 'TLSv1.1']):
                        weak_protocols.append(protocol)
            
            if weak_protocols:
                finding = ParsedFinding(
                    title=f"Weak SSL/TLS protocols supported",
                    severity='high',
                    description=f"Server supports weak SSL/TLS protocols: {', '.join(weak_protocols)}",
                    category='ssl_vulnerability',
                    affected_target=target,
                    evidence=f"Weak protocols: {', '.join(weak_protocols)}",
                    remediation="Disable SSLv2, SSLv3, TLSv1.0, and TLSv1.1. Use TLSv1.2 and TLSv1.3 only",
                    raw_data={
                        'tool': 'testssl',
                        'weak_protocols': weak_protocols,
                        'all_protocols': protocols
                    }
                )
                findings.append(finding)
            
            # Check for weak ciphers
            weak_ciphers = []
            for cipher in ciphers:
                cipher_name = cipher.get('cipher', '')
                if any(weak in cipher_name.upper() for weak in ['DES', 'RC4', 'MD5', 'NULL', 'EXPORT']):
                    weak_ciphers.append(cipher_name)
            
            if weak_ciphers:
                finding = ParsedFinding(
                    title=f"Weak cipher suites detected",
                    severity='medium',
                    description=f"{len(weak_ciphers)} weak cipher suites are supported",
                    category='ssl_vulnerability',
                    affected_target=target,
                    evidence=f"Weak ciphers: {', '.join(weak_ciphers[:5])}{'...' if len(weak_ciphers) > 5 else ''}",
                    remediation="Disable weak cipher suites and use strong encryption algorithms",
                    raw_data={
                        'tool': 'testssl',
                        'weak_ciphers': weak_ciphers
                    }
                )
                findings.append(finding)
            
            self.logger.info(f"testssl.sh: Parsed {len(findings)} SSL/TLS issues")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing testssl file {file_path}: {e}")
            return findings

