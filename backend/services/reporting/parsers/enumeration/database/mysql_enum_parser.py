"""
Parser para MySQL Enumeration.
Formato: TXT con secciones de version, databases, users, tables.
"""

from pathlib import Path
from typing import List
import re
from ...base_parser import BaseParser, ParsedFinding


class MySQLEnumParser(BaseParser):
    """Parser para archivos de MySQL enumeration."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return 'mysql' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de MySQL enumeration.
        
        Secciones:
        - MySQL version
        - Databases
        - Users
        - Tables
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            mysql_version = None
            databases = []
            users = []
            current_section = None
            
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                
                # Extraer versión
                if 'MySQL version:' in line or 'Server version:' in line:
                    match = re.search(r'(\d+\.\d+\.\d+)', line)
                    if match:
                        mysql_version = match.group(1)
                    continue
                
                # Detectar secciones
                if 'Databases:' in line:
                    current_section = 'databases'
                    continue
                elif 'Users:' in line:
                    current_section = 'users'
                    continue
                elif 'Tables' in line:
                    current_section = 'tables'
                    continue
                
                # Parsear databases
                if current_section == 'databases':
                    if not line_stripped.startswith('information_schema'):
                        databases.append(line_stripped)
                
                # Parsear users
                elif current_section == 'users':
                    if '@' in line_stripped:
                        users.append(line_stripped)
            
            # Finding para databases
            if databases:
                user_databases = [db for db in databases if db not in ['information_schema', 'mysql', 'performance_schema', 'sys']]
                
                if user_databases:
                    finding = ParsedFinding(
                        title=f"MySQL databases enumerated",
                        severity='info',
                        description=f"{len(user_databases)} user databases discovered",
                        category='database_enumeration',
                        affected_target='mysql_server',
                        evidence=f"Databases: {', '.join(user_databases[:10])}{'...' if len(user_databases) > 10 else ''}",
                        raw_data={
                            'tool': 'mysql_enum',
                            'version': mysql_version,
                            'databases': user_databases
                        }
                    )
                    findings.append(finding)
            
            # Finding para usuarios remotos
            if users:
                remote_users = [u for u in users if '%' in u or not u.endswith('@localhost')]
                
                if remote_users:
                    finding = ParsedFinding(
                        title=f"MySQL remote users detected",
                        severity='medium',
                        description=f"{len(remote_users)} MySQL users with remote access",
                        category='database_misconfiguration',
                        affected_target='mysql_server',
                        evidence=f"Remote users: {', '.join(remote_users[:5])}{'...' if len(remote_users) > 5 else ''}",
                        remediation="Review and restrict MySQL user access to localhost where possible",
                        raw_data={
                            'tool': 'mysql_enum',
                            'users': users,
                            'remote_users': remote_users
                        }
                    )
                    findings.append(finding)
            
            self.logger.info(f"MySQL Enum: Parsed {len(databases)} databases, {len(users)} users")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing MySQL enum file {file_path}: {e}")
            return findings
