"""
Parser para SNMPWalk - SNMP enumeration.
Formato: TXT con OIDs y valores.
"""

from pathlib import Path
from typing import List
import re
from ...base_parser import BaseParser, ParsedFinding


class SNMPWalkParser(BaseParser):
    """Parser para archivos de SNMPWalk."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return 'snmpwalk' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de SNMPWalk.
        
        Formato:
        SNMPv2-MIB::sysDescr.0 = STRING: Linux server 5.4.0
        SNMPv2-MIB::sysContact.0 = STRING: admin@example.com
        IF-MIB::ifDescr.1 = STRING: eth0
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            system_info = {}
            interfaces = []
            sensitive_info = []
            
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                
                # Parsear formato: OID = TYPE: VALUE
                match = re.match(r'^([^\s]+)\s+=\s+(\w+):\s+(.+)', line_stripped)
                if match:
                    oid = match.group(1)
                    value_type = match.group(2)
                    value = match.group(3)
                    
                    # Extraer info del sistema
                    if 'sysDescr' in oid:
                        system_info['description'] = value
                    elif 'sysContact' in oid:
                        system_info['contact'] = value
                        if '@' in value:
                            sensitive_info.append(('email', value))
                    elif 'sysName' in oid:
                        system_info['hostname'] = value
                    elif 'sysLocation' in oid:
                        system_info['location'] = value
                    elif 'ifDescr' in oid:
                        interfaces.append(value)
            
            # Finding para info del sistema
            if system_info:
                finding = ParsedFinding(
                    title=f"SNMP system information disclosed",
                    severity='low',
                    description=f"System information accessible via SNMP: {system_info.get('hostname', 'unknown')}",
                    category='snmp_enumeration',
                    affected_target=system_info.get('hostname', 'snmp_host'),
                    evidence=f"Description: {system_info.get('description', 'N/A')}, Contact: {system_info.get('contact', 'N/A')}",
                    remediation="Restrict SNMP access and use SNMPv3 with authentication",
                    raw_data={
                        'tool': 'snmpwalk',
                        'system_info': system_info,
                        'interface_count': len(interfaces)
                    }
                )
                findings.append(finding)
            
            # Finding para info sensible
            if sensitive_info:
                finding = ParsedFinding(
                    title=f"Sensitive information in SNMP",
                    severity='medium',
                    description=f"Sensitive information exposed via SNMP (emails, contacts)",
                    category='information_disclosure',
                    affected_target=system_info.get('hostname', 'snmp_host'),
                    evidence=f"Sensitive data: {', '.join([f'{t}: {v}' for t, v in sensitive_info])}",
                    remediation="Remove sensitive information from SNMP strings and restrict access",
                    raw_data={
                        'tool': 'snmpwalk',
                        'sensitive_info': sensitive_info
                    }
                )
                findings.append(finding)
            
            self.logger.info(f"SNMPWalk: Parsed SNMP enumeration with {len(findings)} findings")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing SNMPWalk file {file_path}: {e}")
            return findings
