"""
Parser para Naabu - Fast port scanner.
Formato: TXT con formato simple IP:PUERTO por línea.
"""

from pathlib import Path
from typing import List
from ..base_parser import BaseParser, ParsedFinding


class NaabuParser(BaseParser):
    """Parser para archivos de Naabu."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return 'naabu' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de Naabu.
        
        Formato esperado (TXT):
        192.168.1.1:22
        192.168.1.1:80
        192.168.1.1:443
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or ':' not in line:
                    continue
                
                # Formato: IP:PUERTO
                parts = line.split(':')
                if len(parts) == 2:
                    ip = parts[0].strip()
                    try:
                        port = int(parts[1].strip())
                    except ValueError:
                        continue
                    
                    finding = ParsedFinding(
                        title=f"Open port: {port}/tcp",
                        severity='info',
                        description=f"Port {port}/tcp is open on {ip}",
                        category='port_scanning',
                        affected_target=f"{ip}:{port}",
                        evidence="Discovered via Naabu fast scan",
                        raw_data={
                            'tool': 'naabu',
                            'ip': ip,
                            'port': port,
                            'protocol': 'tcp'
                        }
                    )
                    findings.append(finding)
            
            self.logger.info(f"Naabu: Parsed {len(findings)} open ports")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing Naabu file {file_path}: {e}")
            return findings

