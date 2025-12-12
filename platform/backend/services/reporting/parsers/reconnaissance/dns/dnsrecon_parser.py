"""
DNSRecon Parser
================

Parser para DNSRecon - DNS enumeration.
Formato: JSON con registros DNS (SOA, NS, MX, A, TXT, CNAME).
"""

from pathlib import Path
from typing import List
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class DNSReconParser(BaseParser):
    """Parser para archivos JSON de DNSRecon."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return 'dnsrecon' in filename and file_path.suffix == '.json'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo JSON de DNSRecon.
        
        Formato esperado:
        [
            {
                "type": "SOA",
                "domain": "example.com",
                "address": "192.0.2.1",
                "mname": "ns1.example.com"
            },
            {
                "type": "A",
                "name": "example.com",
                "address": "192.0.2.1"
            }
        ]
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con registros DNS encontrados
        """
        findings = []
        
        try:
            data = self._safe_parse_json(file_path)
            if not data or not isinstance(data, list):
                logger.warning(f"Invalid DNSRecon JSON format: {file_path}")
                return findings
            
            for record in data:
                record_type = record.get('type', 'UNKNOWN')
                
                # Ignorar ScanInfo (metadata)
                if record_type == 'ScanInfo':
                    continue
                
                domain = record.get('domain') or record.get('name', 'unknown')
                address = record.get('address', '')
                
                # Construir descripción según tipo de registro
                if record_type == 'SOA':
                    description = f"SOA record: {domain} → {record.get('mname', 'N/A')}"
                elif record_type == 'NS':
                    description = f"Name server: {record.get('target', address)}"
                elif record_type == 'MX':
                    description = f"Mail server: {record.get('exchange', address)}"
                elif record_type == 'A' or record_type == 'AAAA':
                    description = f"DNS record: {domain} → {address}"
                elif record_type == 'TXT':
                    description = f"TXT record: {record.get('strings', 'N/A')}"
                elif record_type == 'CNAME':
                    description = f"CNAME: {domain} → {record.get('target', 'N/A')}"
                else:
                    description = f"{record_type} record for {domain}"
                
                finding = ParsedFinding(
                    title=f"DNS {record_type} record: {domain}",
                    severity='info',
                    description=description,
                    category='dns_enumeration',
                    affected_target=domain,
                    evidence=f"Address: {address}" if address else None,
                    raw_data={
                        'tool': 'dnsrecon',
                        'record_type': record_type,
                        'domain': domain,
                        'address': address,
                        'full_record': record
                    }
                )
                findings.append(finding)
            
            logger.info(f"DNSRecon: Parsed {len(findings)} DNS records")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing DNSRecon file {file_path}: {e}")
            return findings


