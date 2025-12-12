"""
Parser para LDAPSearch - LDAP enumeration.
Formato: TXT en formato LDIF (LDAP Data Interchange Format).
"""

from pathlib import Path
from typing import List
import re
from ...base_parser import BaseParser, ParsedFinding


class LDAPSearchParser(BaseParser):
    """Parser para archivos de LDAPSearch (formato LDIF)."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return ('ldapsearch' in filename or 'ldap' in filename) and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo LDIF de LDAPSearch.
        
        Formato:
        dn: cn=john.doe,ou=users,dc=example,dc=com
        objectClass: person
        cn: john.doe
        mail: john.doe@example.com
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            # Dividir en entradas (separadas por línea en blanco)
            entries = re.split(r'\n\s*\n', content)
            
            users = []
            groups = []
            emails = []
            
            for entry in entries:
                lines = entry.strip().split('\n')
                if not lines:
                    continue
                
                entry_data = {}
                dn = None
                
                for line in lines:
                    line_stripped = line.strip()
                    if not line_stripped or line_stripped.startswith('#'):
                        continue
                    
                    # Parsear atributo: valor
                    if ':' in line_stripped:
                        parts = line_stripped.split(':', 1)
                        attr = parts[0].strip().lower()
                        value = parts[1].strip()
                        
                        if attr == 'dn':
                            dn = value
                        else:
                            entry_data[attr] = value
                
                # Clasificar entradas
                object_class = entry_data.get('objectclass', '').lower()
                
                if 'person' in object_class or 'inetorgperson' in object_class:
                    cn = entry_data.get('cn', 'unknown')
                    mail = entry_data.get('mail')
                    users.append({'cn': cn, 'dn': dn, 'mail': mail})
                    if mail:
                        emails.append(mail)
                
                elif 'group' in object_class or 'organizationalunit' in object_class:
                    ou = entry_data.get('ou') or entry_data.get('cn', 'unknown')
                    groups.append({'name': ou, 'dn': dn})
            
            # Finding para usuarios
            if users:
                finding = ParsedFinding(
                    title=f"LDAP users enumerated",
                    severity='medium',
                    description=f"{len(users)} user accounts enumerated via LDAP",
                    category='ldap_enumeration',
                    affected_target='ldap_server',
                    evidence=f"Users: {', '.join([u['cn'] for u in users[:10]])}{'...' if len(users) > 10 else ''}",
                    remediation="Restrict anonymous LDAP binds and implement proper access controls",
                    raw_data={
                        'tool': 'ldapsearch',
                        'users': users,
                        'user_count': len(users)
                    }
                )
                findings.append(finding)
            
            # Finding para emails
            if emails:
                finding = ParsedFinding(
                    title=f"Email addresses exposed via LDAP",
                    severity='low',
                    description=f"{len(emails)} email addresses discovered",
                    category='information_disclosure',
                    affected_target='ldap_server',
                    evidence=f"Emails: {', '.join(emails[:5])}{'...' if len(emails) > 5 else ''}",
                    remediation="Restrict LDAP queries or remove email addresses from public attributes",
                    raw_data={
                        'tool': 'ldapsearch',
                        'emails': emails
                    }
                )
                findings.append(finding)
            
            # Finding para grupos
            if groups:
                finding = ParsedFinding(
                    title=f"LDAP groups/OUs enumerated",
                    severity='info',
                    description=f"{len(groups)} organizational units/groups discovered",
                    category='ldap_enumeration',
                    affected_target='ldap_server',
                    evidence=f"Groups: {', '.join([g['name'] for g in groups[:10]])}{'...' if len(groups) > 10 else ''}",
                    raw_data={
                        'tool': 'ldapsearch',
                        'groups': groups
                    }
                )
                findings.append(finding)
            
            self.logger.info(f"LDAPSearch: Parsed {len(users)} users, {len(groups)} groups")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing LDAPSearch file {file_path}: {e}")
            return findings
