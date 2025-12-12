"""
Parser para SMBMap - SMB share enumeration.
Formato: TXT con tabla de shares y permisos.
"""

from pathlib import Path
from typing import List
import re
from ...base_parser import BaseParser, ParsedFinding


class SMBMapParser(BaseParser):
    """Parser para archivos de SMBMap."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return 'smbmap' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de SMBMap.
        
        Formato:
        [+] IP: 192.168.1.100:445	Name: TARGET-PC
        	Disk		Permissions	Comment
        	----		-----------	-------
        	ADMIN$		READ, WRITE	Remote Admin
        	Shared		READ ONLY	Public Share
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            current_ip = None
            in_table = False
            
            for line in lines:
                line_stripped = line.strip()
                
                # Extraer IP: [+] IP: 192.168.1.100:445
                if line_stripped.startswith('[+] IP:'):
                    match = re.search(r'IP:\s+([\d\.]+)', line_stripped)
                    if match:
                        current_ip = match.group(1)
                    in_table = True
                    continue
                
                # Saltar headers de tabla
                if 'Disk' in line and 'Permissions' in line:
                    continue
                if '----' in line:
                    continue
                
                # Parsear líneas de shares si estamos en tabla
                if in_table and line_stripped and current_ip:
                    # Formato: ADMIN$		READ, WRITE	Remote Admin
                    parts = re.split(r'\s{2,}', line_stripped)
                    if len(parts) >= 2:
                        share_name = parts[0].strip()
                        permissions = parts[1].strip() if len(parts) > 1 else 'UNKNOWN'
                        comment = parts[2].strip() if len(parts) > 2 else ''
                        
                        # Ignorar shares de sistema
                        if share_name in ['Disk', 'IPC$']:
                            continue
                        
                        # Determinar severidad
                        if 'WRITE' in permissions.upper():
                            severity = 'medium'  # Escritura es riesgo
                        elif 'READ' in permissions.upper() and share_name not in ['ADMIN$', 'C$']:
                            severity = 'low'
                        else:
                            severity = 'info'
                        
                        finding = ParsedFinding(
                            title=f"SMB Share: {share_name} ({permissions})",
                            severity=severity,
                            description=f"Share '{share_name}' accessible with {permissions} permissions",
                            category='smb_enumeration',
                            affected_target=f"{current_ip}",
                            evidence=f"Permissions: {permissions}, Comment: {comment}",
                            remediation="Review share permissions and restrict access to authorized users only" if severity != 'info' else None,
                            raw_data={
                                'tool': 'smbmap',
                                'share_name': share_name,
                                'permissions': permissions,
                                'comment': comment,
                                'target': current_ip
                            }
                        )
                        findings.append(finding)
                
                # Nueva IP reinicia la tabla
                if line_stripped.startswith('[+] IP:') or not line_stripped:
                    in_table = False
            
            self.logger.info(f"SMBMap: Parsed {len(findings)} SMB shares")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing SMBMap file {file_path}: {e}")
            return findings
