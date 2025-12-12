"""
Parser para SMTP User Enumeration.
Formato: TXT simple IP:PORT username STATUS.
"""

from pathlib import Path
from typing import List
import re
from ...base_parser import BaseParser, ParsedFinding


class SMTPEnumParser(BaseParser):
    """Parser para archivos de SMTP user enumeration."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return 'smtp' in filename and 'enum' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de SMTP enumeration.
        
        Formato:
        192.168.1.1:25     admin exists
        192.168.1.1:25     user exists
        192.168.1.1:25     guest doesn't exist
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.strip().split('\n')
            valid_users = []
            ip = None
            port = None
            
            for line in lines:
                line_stripped = line.strip()
                
                # Formato: IP:PORT    USERNAME STATUS
                match = re.match(r'^([\d\.]+):(\d+)\s+(\S+)\s+(exists|doesn\'t exist)', line_stripped)
                if match:
                    ip = match.group(1)
                    port = int(match.group(2))
                    username = match.group(3)
                    exists = match.group(4) == 'exists'
                    
                    if exists:
                        valid_users.append(username)
            
            # Crear finding con usuarios válidos encontrados
            if valid_users:
                finding = ParsedFinding(
                    title=f"SMTP User enumeration successful",
                    severity='medium',
                    description=f"{len(valid_users)} valid email users enumerated via SMTP",
                    category='smtp_enumeration',
                    affected_target=f"{ip}:{port}" if ip else 'smtp_server',
                    evidence=f"Valid users: {', '.join(valid_users[:10])}{'...' if len(valid_users) > 10 else ''}",
                    remediation="Disable VRFY and EXPN commands on SMTP server to prevent user enumeration",
                    raw_data={
                        'tool': 'smtp-user-enum',
                        'valid_users': valid_users,
                        'user_count': len(valid_users)
                    }
                )
                findings.append(finding)
            
            self.logger.info(f"SMTP Enumeration: Found {len(valid_users)} valid users")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing SMTP enum file {file_path}: {e}")
            return findings


