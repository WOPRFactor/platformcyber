"""
Censys Parser
=============

Parser para Censys - Internet-wide certificate and service scanning.
Formato: JSON con certificados SSL/TLS y servicios.
"""

from pathlib import Path
from typing import List
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class CensysParser(BaseParser):
    """Parser para archivos JSON de Censys."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return 'censys' in filename and file_path.suffix == '.json'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo JSON de Censys.
        
        Formato:
        {
          "status": "ok",
          "results": [
            {
              "ip": "192.0.2.1",
              "protocols": ["443/https", "80/http"],
              "services": [
                {
                  "port": 443,
                  "certificate": {
                    "parsed": {
                      "subject_dn": "CN=example.com"
                    }
                  }
                }
              ]
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
            
            results = data.get('results', [])
            
            for result in results:
                ip = result.get('ip', 'unknown')
                protocols = result.get('protocols', [])
                services = result.get('services', [])
                
                # Finding por cada servicio
                for service in services:
                    port = service.get('port', 0)
                    
                    # Extraer info de certificado si existe
                    cert_info = service.get('certificate', {}).get('parsed', {})
                    subject_dn = cert_info.get('subject_dn', '')
                    
                    if subject_dn:
                        title = f"Censys: {ip}:{port} - Certificate for {subject_dn}"
                        description = f"SSL/TLS certificate found: {subject_dn}"
                        evidence = f"Subject DN: {subject_dn}"
                    else:
                        title = f"Censys: {ip}:{port} - Service discovered"
                        description = f"Service running on {ip}:{port}"
                        evidence = None
                    
                    finding = ParsedFinding(
                        title=title,
                        severity='info',
                        description=description,
                        category='osint',
                        affected_target=f"{ip}:{port}",
                        evidence=evidence,
                        raw_data={
                            'tool': 'censys',
                            'ip': ip,
                            'port': port,
                            'certificate': cert_info,
                            'protocols': protocols
                        }
                    )
                    findings.append(finding)
            
            logger.info(f"Censys: Parsed {len(findings)} service discoveries")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing Censys file {file_path}: {e}")
            return findings


