"""
Parser para OneSixtyOne - SNMP community string brute force.
Formato: TXT con IP [COMMUNITY] SYSTEM_INFO.
"""

from pathlib import Path
from typing import List
import re
from ...base_parser import BaseParser, ParsedFinding


class OneSixtyOneParser(BaseParser):
    """Parser para archivos de OneSixtyOne."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return 'onesixtyone' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de OneSixtyOne.
        
        Formato:
        192.168.1.1 [public] Linux server 5.4.0
        192.168.1.2 [private] Windows Server 2019
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.strip().split('\n')
            
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                
                # Formato: IP [COMMUNITY] SYSTEM_INFO
                match = re.match(r'^([\d\.]+)\s+\[([^\]]+)\]\s+(.+)', line_stripped)
                if match:
                    ip = match.group(1)
                    community = match.group(2)
                    system_info = match.group(3)
                    
                    # Severidad según community string
                    if community.lower() in ['public', 'private']:
                        severity = 'high'
                    else:
                        severity = 'medium'
                    
                    finding = ParsedFinding(
                        title=f"SNMP community string discovered: {community}",
                        severity=severity,
                        description=f"Valid SNMP community string '{community}' found on {ip}",
                        category='snmp_misconfiguration',
                        affected_target=ip,
                        evidence=f"Community: {community}, System: {system_info}",
                        remediation="Change default SNMP community strings and use SNMPv3 with strong authentication",
                        raw_data={
                            'tool': 'onesixtyone',
                            'ip': ip,
                            'community_string': community,
                            'system_info': system_info,
                            'is_default': community.lower() in ['public', 'private']
                        }
                    )
                    findings.append(finding)
            
            self.logger.info(f"OneSixtyOne: Found {len(findings)} valid SNMP community strings")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing OneSixtyOne file {file_path}: {e}")
            return findings
