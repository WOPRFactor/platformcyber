"""
Parser para Masscan - Fast port scanner.
Formato: JSON con estructura de IPs y puertos.
"""

from pathlib import Path
from typing import List
from ..base_parser import BaseParser, ParsedFinding


class MasscanParser(BaseParser):
    """Parser para archivos JSON de Masscan."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return 'masscan' in filename and file_path.suffix == '.json'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo JSON de Masscan.
        
        Formato esperado:
        [
          {
            "ip": "192.168.1.1",
            "timestamp": 1702214400,
            "ports": [
              {"port": 22, "proto": "tcp"},
              {"port": 80, "proto": "tcp"}
            ]
          }
        ]
        """
        findings = []
        
        try:
            data = self._safe_parse_json(file_path)
            if not data or not isinstance(data, list):
                self.logger.warning(f"Invalid Masscan JSON format: {file_path}")
                return findings
            
            for host_entry in data:
                ip = host_entry.get('ip', 'unknown')
                ports = host_entry.get('ports', [])
                timestamp = host_entry.get('timestamp')
                
                for port_info in ports:
                    port = port_info.get('port', 0)
                    protocol = port_info.get('proto', 'tcp')
                    
                    finding = ParsedFinding(
                        title=f"Open port: {port}/{protocol}",
                        severity='info',
                        description=f"Port {port}/{protocol} is open on {ip}",
                        category='port_scanning',
                        affected_target=f"{ip}:{port}",
                        evidence=f"Discovered via Masscan at timestamp {timestamp}" if timestamp else None,
                        raw_data={
                            'tool': 'masscan',
                            'ip': ip,
                            'port': port,
                            'protocol': protocol,
                            'timestamp': timestamp
                        }
                    )
                    findings.append(finding)
            
            self.logger.info(f"Masscan: Parsed {len(findings)} open ports")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing Masscan file {file_path}: {e}")
            return findings

