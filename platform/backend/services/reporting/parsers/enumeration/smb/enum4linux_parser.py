"""
Parser para Enum4linux - SMB enumeration tool.
Formato: TXT con secciones delimitadas por ===.
"""

from pathlib import Path
from typing import List
import re
from ...base_parser import BaseParser, ParsedFinding


class Enum4linuxParser(BaseParser):
    """Parser para archivos de Enum4linux."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return 'enum4linux' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de Enum4linux.
        
        Secciones:
        - Target Information
        - Share Enumeration
        - Password Policy
        - Groups
        - Users
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            current_section = None
            target_ip = None
            
            for line in lines:
                line_stripped = line.strip()
                
                # Detectar target IP
                if 'Target' in line and not target_ip:
                    match = re.search(r'([\d\.]+)', line)
                    if match:
                        target_ip = match.group(1)
                
                # Detectar secciones
                if '===' in line:
                    if 'Share Enumeration' in line:
                        current_section = 'shares'
                    elif 'Password Policy' in line:
                        current_section = 'password_policy'
                    elif 'Groups' in line:
                        current_section = 'groups'
                    elif 'Users' in line:
                        current_section = 'users'
                    continue
                
                # Parsear shares: Share name       Type      Comment
                if current_section == 'shares' and line_stripped:
                    match = re.match(r'^([^\s]+)\s+(Disk|IPC|Printer)\s+(.+)', line_stripped)
                    if match and match.group(1) not in ['Share', 'ADMIN$', 'IPC$']:
                        share_name = match.group(1)
                        share_type = match.group(2)
                        comment = match.group(3)
                        
                        # Shares públicos son riesgo
                        if 'public' in comment.lower() or share_type == 'Disk':
                            severity = 'low'
                        else:
                            severity = 'info'
                        
                        finding = ParsedFinding(
                            title=f"SMB Share discovered: {share_name}",
                            severity=severity,
                            description=f"SMB share '{share_name}' ({share_type}): {comment}",
                            category='smb_enumeration',
                            affected_target=f"{target_ip or 'unknown'}",
                            evidence=f"Type: {share_type}, Comment: {comment}",
                            remediation="Review share permissions and restrict access if needed",
                            raw_data={
                                'tool': 'enum4linux',
                                'type': 'share',
                                'share_name': share_name,
                                'share_type': share_type,
                                'comment': comment,
                                'target': target_ip
                            }
                        )
                        findings.append(finding)
                
                # Parsear users: index: 0x1 RID: 0x3f2 acb: 0x00000010 Account: user1
                elif current_section == 'users' and 'Account:' in line_stripped:
                    match = re.search(r'Account:\s+(\S+)', line_stripped)
                    if match:
                        username = match.group(1)
                        
                        finding = ParsedFinding(
                            title=f"SMB User enumerated: {username}",
                            severity='info',
                            description=f"User account '{username}' enumerated via SMB",
                            category='smb_enumeration',
                            affected_target=f"{target_ip or 'unknown'}",
                            evidence=f"Username: {username}",
                            remediation="Review user accounts and disable unnecessary accounts",
                            raw_data={
                                'tool': 'enum4linux',
                                'type': 'user',
                                'username': username,
                                'target': target_ip
                            }
                        )
                        findings.append(finding)
                
                # Parsear groups: group:[Administrators] rid:[0x220]
                elif current_section == 'groups' and 'group:[' in line_stripped:
                    match = re.search(r'group:\[([^\]]+)\]', line_stripped)
                    if match:
                        group_name = match.group(1)
                        
                        finding = ParsedFinding(
                            title=f"SMB Group enumerated: {group_name}",
                            severity='info',
                            description=f"Group '{group_name}' enumerated via SMB",
                            category='smb_enumeration',
                            affected_target=f"{target_ip or 'unknown'}",
                            evidence=f"Group: {group_name}",
                            raw_data={
                                'tool': 'enum4linux',
                                'type': 'group',
                                'group_name': group_name,
                                'target': target_ip
                            }
                        )
                        findings.append(finding)
            
            self.logger.info(f"Enum4linux: Parsed {len(findings)} SMB findings")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing Enum4linux file {file_path}: {e}")
            return findings
