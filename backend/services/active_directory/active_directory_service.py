"""
Active Directory Service
========================

Servicio completo para pentesting de Active Directory.

Herramientas integradas:
- Kerbrute (user enumeration & password spraying)
- GetNPUsers.py (AS-REP Roasting)
- ldapdomaindump (LDAP enumeration)
- adidnsdump (DNS enumeration)
- CrackMapExec AD modules
"""

import logging
from typing import Dict, Any, Optional

from utils.workspace_logger import log_to_workspace
from repositories import ScanRepository
from services.active_directory.tools import (
    KerbruteScanner,
    GetNPUsersScanner,
    LDAPDomainDumpScanner,
    ADIDNSDumpScanner,
    CrackMapExecADScanner
)

logger = logging.getLogger(__name__)


class ActiveDirectoryService:
    """Servicio completo para pentesting de AD."""

    def __init__(self, scan_repository: ScanRepository = None):
        """Inicializa el servicio."""
        self.scan_repo = scan_repository or ScanRepository()
        self.kerbrute = KerbruteScanner(self.scan_repo)
        self.getnpusers = GetNPUsersScanner(self.scan_repo)
        self.ldapdump = LDAPDomainDumpScanner(self.scan_repo)
        self.adidns = ADIDNSDumpScanner(self.scan_repo)
        self.cme = CrackMapExecADScanner(self.scan_repo)

    # ============================================
    # KERBRUTE
    # ============================================

    def start_kerbrute_userenum(
        self,
        domain: str,
        dc_ip: str,
        userlist: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Enumera usuarios válidos con Kerbrute."""
        result = self.kerbrute.start_userenum(domain, dc_ip, userlist, workspace_id, user_id)
        
        # Log inicial
        log_to_workspace(
            workspace_id=workspace_id,
            source='KERBRUTE',
            level='INFO',
            message=f"Iniciando Kerbrute: user enumeration en {domain}",
            metadata={'scan_id': result.get('scan_id'), 'domain': domain, 'dc_ip': dc_ip, 'action': 'userenum'}
        )
        
        return result

    def start_kerbrute_passwordspray(
        self,
        domain: str,
        dc_ip: str,
        userlist: str,
        password: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Password spraying con Kerbrute."""
        result = self.kerbrute.start_passwordspray(domain, dc_ip, userlist, password, workspace_id, user_id)
        
        # Log inicial
        log_to_workspace(
            workspace_id=workspace_id,
            source='KERBRUTE',
            level='INFO',
            message=f"Iniciando Kerbrute: password spraying en {domain}",
            metadata={'scan_id': result.get('scan_id'), 'domain': domain, 'dc_ip': dc_ip, 'action': 'passwordspray'}
        )
        
        return result

    # ============================================
    # GetNPUsers (AS-REP Roasting)
    # ============================================

    def start_getnpusers(
        self,
        domain: str,
        workspace_id: int,
        user_id: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        dc_ip: Optional[str] = None,
        usersfile: Optional[str] = None,
        no_pass: bool = True
    ) -> Dict[str, Any]:
        """AS-REP Roasting con GetNPUsers.py."""
        result = self.getnpusers.start_scan(
            domain, workspace_id, user_id, username, password, dc_ip, usersfile, no_pass
        )
        
        # Log inicial
        log_to_workspace(
            workspace_id=workspace_id,
            source='GETNPUSERS',
            level='INFO',
            message=f"Iniciando GetNPUsers: AS-REP Roasting en {domain}",
            metadata={'scan_id': result.get('scan_id'), 'domain': domain, 'dc_ip': dc_ip}
        )
        
        return result

    # ============================================
    # LDAP Domain Dump
    # ============================================

    def start_ldapdomaindump(
        self,
        dc_ip: str,
        username: str,
        password: str,
        domain: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Dump de información LDAP."""
        result = self.ldapdump.start_scan(dc_ip, username, password, domain, workspace_id, user_id)
        
        # Log inicial
        log_to_workspace(
            workspace_id=workspace_id,
            source='LDAPDOMAINDUMP',
            level='INFO',
            message=f"Iniciando LDAP Domain Dump: {domain}",
            metadata={'scan_id': result.get('scan_id'), 'domain': domain, 'dc_ip': dc_ip}
        )
        
        return result

    # ============================================
    # ADIDNS Dump
    # ============================================

    def start_adidnsdump(
        self,
        dc_ip: str,
        username: str,
        password: str,
        domain: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Dump de registros DNS de AD."""
        result = self.adidns.start_scan(dc_ip, username, password, domain, workspace_id, user_id)
        
        # Log inicial
        log_to_workspace(
            workspace_id=workspace_id,
            source='ADIDNSDUMP',
            level='INFO',
            message=f"Iniciando ADIDNS Dump: {domain}",
            metadata={'scan_id': result.get('scan_id'), 'domain': domain, 'dc_ip': dc_ip}
        )
        
        return result

    # ============================================
    # CrackMapExec AD Enumeration
    # ============================================

    def start_cme_enum_users(
        self,
        dc_ip: str,
        username: str,
        password: str,
        domain: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Enumera usuarios AD con CrackMapExec."""
        result = self.cme.start_enum_users(dc_ip, username, password, domain, workspace_id, user_id)
        
        # Log inicial
        log_to_workspace(
            workspace_id=workspace_id,
            source='CRACKMAPEXEC',
            level='INFO',
            message=f"Iniciando CrackMapExec: enumeración de usuarios en {domain}",
            metadata={'scan_id': result.get('scan_id'), 'domain': domain, 'dc_ip': dc_ip, 'action': 'enum_users'}
        )
        
        return result

    def start_cme_enum_groups(
        self,
        dc_ip: str,
        username: str,
        password: str,
        domain: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Enumera grupos AD con CrackMapExec."""
        result = self.cme.start_enum_groups(dc_ip, username, password, domain, workspace_id, user_id)
        
        # Log inicial
        log_to_workspace(
            workspace_id=workspace_id,
            source='CRACKMAPEXEC',
            level='INFO',
            message=f"Iniciando CrackMapExec: enumeración de grupos en {domain}",
            metadata={'scan_id': result.get('scan_id'), 'domain': domain, 'dc_ip': dc_ip, 'action': 'enum_groups'}
        )
        
        return result

    # ============================================
    # PREVIEW METHODS
    # ============================================
    
    def preview_kerbrute_userenum(
        self,
        domain: str,
        dc_ip: str,
        userlist: str,
        workspace_id: int
    ) -> Dict[str, Any]:
        """Preview del comando Kerbrute userenum."""
        output_file = f'/workspaces/workspace_{workspace_id}/active_directory/kerbrute_userenum_{{scan_id}}.txt'
        
        command = [
            'kerbrute', 'userenum',
            '--dc', dc_ip,
            '--domain', domain,
            userlist
        ]
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'domain': domain,
                'dc_ip': dc_ip,
                'userlist': userlist
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_kerbrute_passwordspray(
        self,
        domain: str,
        dc_ip: str,
        userlist: str,
        password: str,
        workspace_id: int
    ) -> Dict[str, Any]:
        """Preview del comando Kerbrute passwordspray."""
        output_file = f'/workspaces/workspace_{workspace_id}/active_directory/kerbrute_passwordspray_{{scan_id}}.txt'
        
        command = [
            'kerbrute', 'passwordspray',
            '--dc', dc_ip,
            '--domain', domain,
            userlist,
            password
        ]
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'domain': domain,
                'dc_ip': dc_ip,
                'userlist': userlist,
                'password': '***'
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_getnpusers(
        self,
        domain: str,
        workspace_id: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        dc_ip: Optional[str] = None,
        usersfile: Optional[str] = None,
        no_pass: bool = True
    ) -> Dict[str, Any]:
        """Preview del comando GetNPUsers."""
        output_file = f'/workspaces/workspace_{workspace_id}/active_directory/getnpusers_{{scan_id}}.txt'
        
        command = [
            'python3', '/opt/impacket/examples/GetNPUsers.py',
            domain + '/'
        ]
        
        if username:
            command.append(f'{username}:{password or ""}')
        elif usersfile:
            command.extend(['-usersfile', usersfile])
        
        if dc_ip:
            command.extend(['-dc-ip', dc_ip])
        
        if no_pass:
            command.append('-no-pass')
        
        command.extend(['-outputfile', output_file])
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'domain': domain,
                'username': username,
                'password': '***' if password else None,
                'dc_ip': dc_ip,
                'usersfile': usersfile,
                'no_pass': no_pass
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_ldapdomaindump(
        self,
        dc_ip: str,
        username: str,
        password: str,
        domain: str,
        workspace_id: int
    ) -> Dict[str, Any]:
        """Preview del comando ldapdomaindump."""
        output_dir = f'/workspaces/workspace_{workspace_id}/active_directory/ldapdomaindump_{{scan_id}}'
        
        command = [
            'ldapdomaindump',
            '-u', f'{domain}\\{username}',
            '-p', '***',
            dc_ip,
            '--output-path', output_dir
        ]
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'domain': domain,
                'dc_ip': dc_ip,
                'username': username,
                'password': '***'
            },
            'estimated_timeout': 600,
            'output_file': output_dir,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_adidnsdump(
        self,
        dc_ip: str,
        username: str,
        password: str,
        domain: str,
        workspace_id: int
    ) -> Dict[str, Any]:
        """Preview del comando adidnsdump."""
        output_file = f'/workspaces/workspace_{workspace_id}/active_directory/adidnsdump_{{scan_id}}.txt'
        
        command = [
            'adidnsdump',
            '-u', f'{domain}\\{username}',
            '-p', '***',
            '-r', domain,
            '-d', dc_ip,
            '-o', output_file
        ]
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'domain': domain,
                'dc_ip': dc_ip,
                'username': username,
                'password': '***'
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_cme_enum_users(
        self,
        dc_ip: str,
        username: str,
        password: str,
        domain: str,
        workspace_id: int
    ) -> Dict[str, Any]:
        """Preview del comando CrackMapExec enum users."""
        output_file = f'/workspaces/workspace_{workspace_id}/active_directory/cme_enum_users_{{scan_id}}.txt'
        
        command = [
            'crackmapexec', 'ldap', dc_ip,
            '-u', username,
            '-p', '***',
            '-d', domain,
            '--users',
            '--log', output_file
        ]
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'domain': domain,
                'dc_ip': dc_ip,
                'username': username,
                'password': '***'
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_cme_enum_groups(
        self,
        dc_ip: str,
        username: str,
        password: str,
        domain: str,
        workspace_id: int
    ) -> Dict[str, Any]:
        """Preview del comando CrackMapExec enum groups."""
        output_file = f'/workspaces/workspace_{workspace_id}/active_directory/cme_enum_groups_{{scan_id}}.txt'
        
        command = [
            'crackmapexec', 'ldap', dc_ip,
            '-u', username,
            '-p', '***',
            '-d', domain,
            '--groups',
            '--log', output_file
        ]
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'domain': domain,
                'dc_ip': dc_ip,
                'username': username,
                'password': '***'
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    # ============================================
    # OBTENER RESULTADOS
    # ============================================

    def get_scan_results(self, scan_id: int) -> Dict[str, Any]:
        """Obtiene y parsea resultados."""
        scan = self.scan_repo.find_by_id(scan_id)

        if not scan:
            raise ValueError(f'Scan {scan_id} not found')

        if scan.status != 'completed':
            return {
                'scan_id': scan_id,
                'status': scan.status,
                'message': 'Scan not completed yet'
            }

        tool = scan.options.get('tool')
        action = scan.options.get('action', '')

        try:
            if tool == 'kerbrute':
                return self.kerbrute.get_results(scan_id, action)
            elif tool == 'getnpusers':
                return self.getnpusers.get_results(scan_id)
            elif tool == 'ldapdomaindump':
                return self.ldapdump.get_results(scan_id)
            elif tool == 'adidnsdump':
                return self.adidns.get_results(scan_id)
            elif tool == 'crackmapexec':
                return self.cme.get_results(scan_id, action)
            else:
                return {'error': f'Unknown tool: {tool}'}

        except Exception as e:
            logger.error(f"Error getting AD scan results {scan_id}: {e}")
            return {
                'scan_id': scan_id,
                'error': f'Failed to get results: {str(e)}'
            }

