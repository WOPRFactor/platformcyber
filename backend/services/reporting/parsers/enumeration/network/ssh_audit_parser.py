"""
Parser para SSH-Audit - SSH configuration auditor.
Formato: TXT con categorías y niveles [info], [warn], [fail].
"""

from pathlib import Path
from typing import List
import re
from ...base_parser import BaseParser, ParsedFinding


class SSHAuditParser(BaseParser):
    """Parser para archivos de SSH-Audit."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return ('ssh-audit' in filename or 'ssh_audit' in filename) and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de SSH-Audit.
        
        Formato:
        (kex) diffie-hellman-group1-sha1  -- [fail] removed (in server)
        (enc) 3des-cbc                     -- [fail] removed (in server)
        (mac) hmac-sha1                    -- [warn] using weak hashing algorithm
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            target = None
            ssh_version = None
            
            for line in lines:
                line_stripped = line.strip()
                
                # Extraer versión SSH
                if 'banner:' in line_stripped.lower():
                    match = re.search(r'banner:\s+(.+)', line_stripped, re.IGNORECASE)
                    if match:
                        ssh_version = match.group(1)
                
                # Parsear líneas con niveles: (cat) algorithm -- [level] message
                match = re.match(r'\((\w+)\)\s+([^\s]+)\s+--\s+\[(\w+)\]\s+(.+)', line_stripped)
                if match:
                    category = match.group(1)
                    algorithm = match.group(2)
                    level = match.group(3)
                    message = match.group(4)
                    
                    # Mapear categorías
                    category_map = {
                        'kex': 'Key Exchange',
                        'key': 'Host Key',
                        'enc': 'Encryption',
                        'mac': 'MAC Algorithm',
                        'gen': 'General'
                    }
                    category_name = category_map.get(category, category)
                    
                    # Mapear niveles a severidad
                    if level == 'fail':
                        severity = 'high'
                    elif level == 'warn':
                        severity = 'medium'
                    else:
                        severity = 'info'
                    
                    # Solo crear findings para warn y fail
                    if level in ['warn', 'fail']:
                        finding = ParsedFinding(
                            title=f"SSH {category_name}: {algorithm}",
                            severity=severity,
                            description=f"{category_name} algorithm '{algorithm}': {message}",
                            category='ssh_configuration',
                            affected_target=target or 'ssh_server',
                            evidence=f"Algorithm: {algorithm}, Issue: {message}",
                            remediation=f"Disable {algorithm} and use modern alternatives",
                            raw_data={
                                'tool': 'ssh-audit',
                                'category': category,
                                'algorithm': algorithm,
                                'level': level,
                                'message': message,
                                'ssh_version': ssh_version
                            }
                        )
                        findings.append(finding)
            
            self.logger.info(f"SSH-Audit: Parsed {len(findings)} SSH configuration issues")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing SSH-Audit file {file_path}: {e}")
            return findings


