"""
Network Services Enumeration Service
====================================

Servicios para enumeración de servicios de red:
- SSH (ssh-audit, Nmap scripts)
- FTP (Nmap scripts)
- SMTP (smtp-user-enum, Nmap scripts)
- DNS (Zone transfer, Nmap scripts)
- SNMP (snmpwalk, onesixtyone, Nmap scripts)
- LDAP (ldapsearch, Nmap scripts)
- RDP (Nmap scripts)
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
from repositories import ScanRepository
from .base import BaseEnumerationService
from .network_services import (
    SSHEnumeration,
    FTPEnumeration,
    SMTPEnumeration,
    DNSEnumeration,
    SNMPEnumeration,
    LDAPEnumeration,
    RDPEnumeration
)

logger = logging.getLogger(__name__)


class NetworkServicesEnumerationService(BaseEnumerationService):
    """Servicio para enumeración de servicios de red."""

    def __init__(self, scan_repository: ScanRepository = None, output_dir: Path = None):
        """Inicializa el servicio."""
        super().__init__(scan_repository, output_dir)
        self.ssh = SSHEnumeration(self.scan_repo)
        self.ftp = FTPEnumeration(self.scan_repo)
        self.smtp = SMTPEnumeration(self.scan_repo)
        self.dns = DNSEnumeration(self.scan_repo)
        self.snmp = SNMPEnumeration(self.scan_repo)
        self.ldap = LDAPEnumeration(self.scan_repo)
        self.rdp = RDPEnumeration(self.scan_repo)

    # ============================================
    # SSH
    # ============================================

    def start_ssh_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'nmap',
        port: int = 22
    ) -> Dict[str, Any]:
        """Enumeración SSH."""
        return self.ssh.start_enum(target, workspace_id, user_id, tool, port)

    # ============================================
    # FTP
    # ============================================

    def start_ftp_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        port: int = 21
    ) -> Dict[str, Any]:
        """Enumeración FTP."""
        return self.ftp.start_enum(target, workspace_id, user_id, port)

    def preview_ftp_enum(
        self,
        target: str,
        workspace_id: int,
        port: int = 21
    ) -> Dict[str, Any]:
        """Preview del comando FTP enum."""
        return self.ftp.preview_enum(target, workspace_id, port)

    # ============================================
    # SMTP
    # ============================================

    def start_smtp_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'nmap',
        port: int = 25,
        userlist: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enumeración SMTP."""
        return self.smtp.start_enum(target, workspace_id, user_id, tool, port, userlist)

    # ============================================
    # DNS
    # ============================================

    def start_dns_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        domain: Optional[str] = None,
        tool: str = 'nmap',
        port: int = 53
    ) -> Dict[str, Any]:
        """Enumeración DNS."""
        return self.dns.start_enum(target, workspace_id, user_id, domain, tool, port)

    def preview_dns_enum(
        self,
        target: str,
        workspace_id: int,
        domain: Optional[str] = None,
        tool: str = 'nmap',
        port: int = 53
    ) -> Dict[str, Any]:
        """Preview del comando DNS enum."""
        return self.dns.preview_enum(target, workspace_id, domain, tool, port)

    # ============================================
    # SNMP
    # ============================================

    def start_snmp_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'nmap',
        port: int = 161,
        community: str = 'public',
        community_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enumeración SNMP."""
        return self.snmp.start_enum(target, workspace_id, user_id, tool, port, community, community_file)

    # ============================================
    # LDAP
    # ============================================

    def start_ldap_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'nmap',
        port: int = 389,
        base_dn: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enumeración LDAP."""
        return self.ldap.start_enum(target, workspace_id, user_id, tool, port, base_dn)

    # ============================================
    # RDP
    # ============================================

    def start_rdp_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        port: int = 3389
    ) -> Dict[str, Any]:
        """Enumeración RDP."""
        return self.rdp.start_enum(target, workspace_id, user_id, port)

    def preview_rdp_enum(
        self,
        target: str,
        workspace_id: int,
        port: int = 3389
    ) -> Dict[str, Any]:
        """Preview del comando RDP enum."""
        return self.rdp.preview_enum(target, workspace_id, port)

    def preview_ssh_enum(
        self,
        target: str,
        workspace_id: int,
        tool: str = 'nmap',
        port: int = 22
    ) -> Dict[str, Any]:
        """Preview del comando SSH enum."""
        return self.ssh.preview_enum(target, workspace_id, tool, port)

    def preview_smtp_enum(
        self,
        target: str,
        workspace_id: int,
        tool: str = 'nmap',
        port: int = 25,
        userlist: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando SMTP enum."""
        return self.smtp.preview_enum(target, workspace_id, tool, port, userlist)

    def preview_snmp_enum(
        self,
        target: str,
        workspace_id: int,
        tool: str = 'nmap',
        port: int = 161,
        community: str = 'public',
        community_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando SNMP enum."""
        return self.snmp.preview_enum(target, workspace_id, tool, port, community, community_file)

    def preview_ldap_enum(
        self,
        target: str,
        workspace_id: int,
        tool: str = 'nmap',
        port: int = 389,
        base_dn: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando LDAP enum."""
        return self.ldap.preview_enum(target, workspace_id, tool, port, base_dn)
