"""
Parser para PostgreSQL Enumeration.
Formato: TXT con secciones de version, databases, users/roles, schemas.
"""

from pathlib import Path
from typing import List
import re
from ...base_parser import BaseParser, ParsedFinding


class PostgreSQLEnumParser(BaseParser):
    """Parser para archivos de PostgreSQL enumeration."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return ('psql' in filename or 'postgresql' in filename or 'postgres' in filename) and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de PostgreSQL enumeration.
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            pg_version = None
            databases = []
            superusers = []
            current_section = None
            
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                
                # Extraer versión
                if 'PostgreSQL version:' in line or 'Server version:' in line:
                    match = re.search(r'(\d+\.\d+)', line)
                    if match:
                        pg_version = match.group(1)
                    continue
                
                # Detectar secciones
                if 'Databases:' in line:
                    current_section = 'databases'
                    continue
                elif 'Users/Roles:' in line:
                    current_section = 'users'
                    continue
                elif 'Schemas' in line:
                    current_section = 'schemas'
                    continue
                
                # Parsear databases
                if current_section == 'databases':
                    if not line_stripped.startswith('template') and line_stripped != 'postgres':
                        databases.append(line_stripped)
                
                # Parsear users/roles
                elif current_section == 'users':
                    if '(Superuser)' in line_stripped:
                        match = re.match(r'^(\w+)\s+\(Superuser\)', line_stripped)
                        if match:
                            superusers.append(match.group(1))
            
            # Finding para databases
            if databases:
                finding = ParsedFinding(
                    title=f"PostgreSQL databases enumerated",
                    severity='info',
                    description=f"{len(databases)} user databases discovered",
                    category='database_enumeration',
                    affected_target='postgresql_server',
                    evidence=f"Databases: {', '.join(databases[:10])}{'...' if len(databases) > 10 else ''}",
                    raw_data={
                        'tool': 'postgresql_enum',
                        'version': pg_version,
                        'databases': databases
                    }
                )
                findings.append(finding)
            
            # Finding para superusers
            if superusers:
                finding = ParsedFinding(
                    title=f"PostgreSQL superusers detected",
                    severity='low',
                    description=f"{len(superusers)} PostgreSQL superuser accounts found",
                    category='database_enumeration',
                    affected_target='postgresql_server',
                    evidence=f"Superusers: {', '.join(superusers)}",
                    remediation="Review superuser accounts and grant privileges following principle of least privilege",
                    raw_data={
                        'tool': 'postgresql_enum',
                        'superusers': superusers
                    }
                )
                findings.append(finding)
            
            self.logger.info(f"PostgreSQL Enum: Parsed {len(databases)} databases, {len(superusers)} superusers")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing PostgreSQL enum file {file_path}: {e}")
            return findings
