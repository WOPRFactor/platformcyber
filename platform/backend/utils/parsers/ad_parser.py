"""
Active Directory Parsers
========================

Parsers para herramientas de Active Directory.
"""

import json
import re
from typing import Dict, List, Any, Optional


class KerbruteParser:
    """Parser para resultados de Kerbrute."""
    
    @staticmethod
    def parse_output(output: str) -> Dict[str, Any]:
        """Parsea salida de Kerbrute."""
        valid_users = []
        valid_passwords = []
        
        # [+] VALID USERNAME:       user@DOMAIN.COM
        user_matches = re.findall(
            r'\[\+\]\s+VALID USERNAME:\s+(\S+@\S+)',
            output,
            re.IGNORECASE
        )
        valid_users = list(set(user_matches))
        
        # [+] VALID LOGIN:  user@DOMAIN.COM:password
        login_matches = re.findall(
            r'\[\+\]\s+VALID LOGIN:\s+(\S+@\S+):(\S+)',
            output,
            re.IGNORECASE
        )
        for username, password in login_matches:
            valid_passwords.append({
                'username': username,
                'password': password
            })
        
        return {
            'tool': 'kerbrute',
            'valid_users': valid_users,
            'valid_passwords': valid_passwords,
            'total_users': len(valid_users),
            'total_valid_logins': len(valid_passwords)
        }


class RubeusParser:
    """Parser para resultados de Rubeus."""
    
    @staticmethod
    def parse_output(output: str) -> Dict[str, Any]:
        """Parsea salida de Rubeus."""
        tickets = []
        hashes = []
        
        # Extraer tickets Kerberos
        ticket_blocks = re.split(r'\[\*\]\s+Ticket', output)
        
        for block in ticket_blocks[1:]:
            # ServiceName
            service_match = re.search(r'ServiceName\s+:\s+(.+)', block)
            # UserName
            user_match = re.search(r'UserName\s+:\s+(.+)', block)
            # Hash
            hash_match = re.search(r'\$krb5tgs\$.*', block)
            
            if service_match and user_match:
                tickets.append({
                    'service': service_match.group(1).strip(),
                    'user': user_match.group(1).strip(),
                    'hash': hash_match.group(0).strip() if hash_match else None
                })
        
        # Extraer hashes
        hash_matches = re.findall(r'(\$krb5tgs\$\S+)', output)
        hashes = list(set(hash_matches))
        
        return {
            'tool': 'rubeus',
            'tickets_found': len(tickets),
            'hashes_found': len(hashes),
            'tickets': tickets,
            'hashes': hashes[:20]  # Primeros 20
        }


class LDAPDomainDumpParser:
    """Parser para ldapdomaindump."""
    
    @staticmethod
    def parse_json(json_path: str) -> Dict[str, Any]:
        """Parsea JSON de ldapdomaindump."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            users = data.get('users', [])
            computers = data.get('computers', [])
            groups = data.get('groups', [])
            
            # Extraer usuarios privilegiados
            admin_users = []
            for user in users:
                if user.get('adminCount', 0) > 0:
                    admin_users.append(user.get('sAMAccountName'))
            
            return {
                'tool': 'ldapdomaindump',
                'total_users': len(users),
                'total_computers': len(computers),
                'total_groups': len(groups),
                'admin_users': len(admin_users),
                'admin_users_list': admin_users[:20],
                'data': {
                    'users': users[:10],
                    'computers': computers[:10],
                    'groups': groups[:10]
                }
            }
        except Exception as e:
            return {
                'tool': 'ldapdomaindump',
                'error': str(e)
            }


class ADExplorerParser:
    """Parser para ADExplorer snapshots."""
    
    @staticmethod
    def parse_snapshot(snapshot_path: str) -> Dict[str, Any]:
        """
        Parsea snapshot de ADExplorer.
        
        Note: ADExplorer usa formato propietario.
        Aquí solo extraemos metadata básica.
        """
        try:
            # ADExplorer snapshots son binarios
            # Necesitaría parser específico
            return {
                'tool': 'adexplorer',
                'snapshot': snapshot_path,
                'message': 'ADExplorer parser not fully implemented. Use GUI for analysis.'
            }
        except Exception as e:
            return {
                'tool': 'adexplorer',
                'error': str(e)
            }


class GetNPUsersParser:
    """Parser para GetNPUsers.py (AS-REP Roasting)."""
    
    @staticmethod
    def parse_output(output: str) -> Dict[str, Any]:
        """Parsea salida de GetNPUsers.py."""
        vulnerable_users = []
        hashes = []
        
        # [-] User user doesn't have UF_DONT_REQUIRE_PREAUTH set
        # [+] User user has UF_DONT_REQUIRE_PREAUTH set
        vuln_matches = re.findall(
            r'\[\+\]\s+(\S+)\s+has\s+UF_DONT_REQUIRE_PREAUTH',
            output,
            re.IGNORECASE
        )
        vulnerable_users = list(set(vuln_matches))
        
        # Extraer hashes AS-REP
        hash_matches = re.findall(r'(\$krb5asrep\$\S+)', output)
        hashes = list(set(hash_matches))
        
        return {
            'tool': 'getnpusers',
            'vulnerable_users': vulnerable_users,
            'hashes_obtained': len(hashes),
            'hashes': hashes,
            'total_vulnerable': len(vulnerable_users)
        }


class ADIDNSDumpParser:
    """Parser para adidnsdump."""
    
    @staticmethod
    def parse_output(output: str) -> Dict[str, Any]:
        """Parsea salida de adidnsdump."""
        records = []
        
        # Extraer registros DNS
        # Formato: hostname,ip,type
        for line in output.split('\n'):
            if ',' in line and not line.startswith('#'):
                parts = line.split(',')
                if len(parts) >= 3:
                    records.append({
                        'hostname': parts[0].strip(),
                        'ip': parts[1].strip(),
                        'type': parts[2].strip()
                    })
        
        # Agrupar por tipo
        by_type = {}
        for record in records:
            record_type = record['type']
            if record_type not in by_type:
                by_type[record_type] = []
            by_type[record_type].append(record)
        
        return {
            'tool': 'adidnsdump',
            'total_records': len(records),
            'by_type': {k: len(v) for k, v in by_type.items()},
            'records': records[:100]  # Primeros 100
        }


class CrackMapExecADParser:
    """Parser específico para módulos AD de CrackMapExec."""
    
    @staticmethod
    def parse_enum_users(output: str) -> Dict[str, Any]:
        """Parsea enumeración de usuarios."""
        users = []
        
        for line in output.split('\n'):
            # Extraer usuarios del output de CME
            user_match = re.search(r'\\(\w+)\s+', line)
            if user_match:
                users.append(user_match.group(1))
        
        return {
            'tool': 'crackmapexec',
            'action': 'enum_users',
            'users': list(set(users)),
            'total_users': len(set(users))
        }
    
    @staticmethod
    def parse_enum_groups(output: str) -> Dict[str, Any]:
        """Parsea enumeración de grupos."""
        groups = []
        
        for line in output.split('\n'):
            if 'Domain Admins' in line or 'Enterprise Admins' in line or 'membercount' in line.lower():
                group_match = re.search(r'(\S+)\s+\(membercount:', line)
                if group_match:
                    groups.append(group_match.group(1))
        
        return {
            'tool': 'crackmapexec',
            'action': 'enum_groups',
            'groups': list(set(groups)),
            'total_groups': len(set(groups))
        }
    
    @staticmethod
    def parse_enum_shares(output: str) -> Dict[str, Any]:
        """Parsea enumeración de shares."""
        shares = []
        
        for line in output.split('\n'):
            # Share format: [+] SHARENAME  (READ|WRITE)
            share_match = re.search(r'\[\+\]\s+(\S+)\s+(READ|WRITE)', line)
            if share_match:
                shares.append({
                    'name': share_match.group(1),
                    'permission': share_match.group(2)
                })
        
        return {
            'tool': 'crackmapexec',
            'action': 'enum_shares',
            'shares': shares,
            'total_shares': len(shares),
            'writable_shares': len([s for s in shares if s['permission'] == 'WRITE'])
        }
