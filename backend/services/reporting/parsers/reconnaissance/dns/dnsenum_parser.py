"""
DNSEnum Parser
==============

Parser para DNSEnum - DNS enumeration.
Formato: TXT con secciones (Host's addresses, Name Servers, MX records).
"""

from pathlib import Path
from typing import List
import re
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class DNSEnumParser(BaseParser):
    """Parser para archivos de DNSEnum."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return 'dnsenum' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de DNSEnum.
        
        Formato:
        Host's addresses:
        example.com.    5    IN    A    192.0.2.1
        
        Name Servers:
        ns1.example.com.    5    IN    A    192.0.2.10
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con registros DNS encontrados
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detectar secciones
                if "Host's addresses:" in line:
                    current_section = 'A_RECORDS'
                    continue
                elif "Name Servers:" in line:
                    current_section = 'NS_RECORDS'
                    continue
                elif "Mail" in line and "Servers:" in line:
                    current_section = 'MX_RECORDS'
                    continue
                
                # Parsear registros DNS (formato: domain.com. 5 IN A 192.0.2.1)
                match = re.search(r'([\w\.\-]+)\.\s+\d+\s+IN\s+(A|AAAA|NS|MX)\s+([\d\.\w\-]+)', line)
                if match:
                    domain = match.group(1)
                    record_type = match.group(2)
                    value = match.group(3)
                    
                    if current_section == 'A_RECORDS':
                        description = f"Host address: {domain} → {value}"
                    elif current_section == 'NS_RECORDS':
                        description = f"Name server: {domain} → {value}"
                    elif current_section == 'MX_RECORDS':
                        description = f"Mail server: {domain} → {value}"
                    else:
                        description = f"{record_type} record: {domain} → {value}"
                    
                    finding = ParsedFinding(
                        title=f"DNS {record_type}: {domain}",
                        severity='info',
                        description=description,
                        category='dns_enumeration',
                        affected_target=domain,
                        evidence=f"Value: {value}",
                        raw_data={
                            'tool': 'dnsenum',
                            'type': record_type,
                            'domain': domain,
                            'value': value,
                            'section': current_section
                        }
                    )
                    findings.append(finding)
            
            logger.info(f"DNSEnum: Parsed {len(findings)} DNS records")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing DNSEnum file {file_path}: {e}")
            return findings


