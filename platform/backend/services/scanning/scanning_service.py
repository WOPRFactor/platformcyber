"""
Scanning Service (Refactorizado)
=================================

Servicio orquestador para escaneo de puertos y servicios.
Utiliza scanners modulares para cada herramienta.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from repositories import ScanRepository
from utils.workspace_logger import log_to_workspace
from utils.workspace_filesystem import get_workspace_output_dir_from_scan
from .tools import NmapScanner, RustScanScanner, MasscanScanner, NaabuScanner
from utils.parsers.nmap_parser import NmapParser, RustScanParser, MasscanParser
from services.enumeration import (
    SMBEnumerationService,
    NetworkServicesEnumerationService,
    DatabaseEnumerationService,
    SSLEnumerationService
)

logger = logging.getLogger(__name__)


class ScanningService:
    """Servicio completo de escaneo de puertos y servicios."""
    
    def __init__(self, scan_repository: ScanRepository = None):
        """Inicializa el servicio."""
        self.scan_repo = scan_repository or ScanRepository()
        
        # Inicializar scanners modulares
        self.nmap_scanner = NmapScanner(scan_repository)
        self.rustscan_scanner = RustScanScanner(scan_repository)
        self.masscan_scanner = MasscanScanner(scan_repository)
        self.naabu_scanner = NaabuScanner(scan_repository)
        
        # Parsers para resultados
        self.nmap_parser = NmapParser()
        self.rustscan_parser = RustScanParser()
        self.masscan_parser = MasscanParser()
        
        # Inicializar servicios de enumeración
        from utils.workspace_filesystem import PROJECT_TMP_DIR
        enum_output_dir = PROJECT_TMP_DIR / 'enumeration'
        self.smb_enum = SMBEnumerationService(self.scan_repo, enum_output_dir)
        self.network_enum = NetworkServicesEnumerationService(self.scan_repo, enum_output_dir)
        self.database_enum = DatabaseEnumerationService(self.scan_repo, enum_output_dir)
        self.ssl_enum = SSLEnumerationService(self.scan_repo, enum_output_dir)
    
    # ============================================
    # NMAP SCANS
    # ============================================
    
    def start_nmap_scan(
        self,
        target: str,
        scan_type: str,
        workspace_id: int,
        user_id: int,
        ports: Optional[str] = None,
        scripts: Optional[List[str]] = None,
        os_detection: bool = False,
        version_detection: bool = False
    ) -> Dict[str, Any]:
        """Inicia un escaneo Nmap completo."""
        return self.nmap_scanner.start_scan(
            target=target,
            scan_type=scan_type,
            workspace_id=workspace_id,
            user_id=user_id,
            ports=ports,
            scripts=scripts,
            os_detection=os_detection,
            version_detection=version_detection
        )
    
    def preview_nmap_scan(
        self,
        target: str,
        scan_type: str,
        workspace_id: int,
        ports: Optional[str] = None,
        scripts: Optional[List[str]] = None,
        os_detection: bool = False,
        version_detection: bool = False
    ) -> Dict[str, Any]:
        """Preview del comando Nmap."""
        return self.nmap_scanner.preview_scan(
            target=target,
            scan_type=scan_type,
            workspace_id=workspace_id,
            ports=ports,
            scripts=scripts,
            os_detection=os_detection,
            version_detection=version_detection
        )
    
    # ============================================
    # RUSTSCAN
    # ============================================
    
    def start_rustscan(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        batch_size: int = 4000,
        timeout: int = 1500,
        ulimit: int = 5000
    ) -> Dict[str, Any]:
        """Inicia RustScan (escaneo ultra-rápido)."""
        return self.rustscan_scanner.start_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            batch_size=batch_size,
            timeout=timeout,
            ulimit=ulimit
        )
    
    def preview_rustscan(
        self,
        target: str,
        workspace_id: int,
        batch_size: int = 4000,
        timeout: int = 1500,
        ulimit: int = 5000
    ) -> Dict[str, Any]:
        """Preview del comando RustScan."""
        return self.rustscan_scanner.preview_scan(
            target=target,
            workspace_id=workspace_id,
            batch_size=batch_size,
            timeout=timeout,
            ulimit=ulimit
        )
    
    # ============================================
    # MASSCAN
    # ============================================
    
    def start_masscan(
        self,
        target: str,
        ports: str,
        workspace_id: int,
        user_id: int,
        rate: int = 1000,
        environment: str = 'internal'
    ) -> Dict[str, Any]:
        """Inicia Masscan (scan masivo)."""
        return self.masscan_scanner.start_scan(
            target=target,
            ports=ports,
            workspace_id=workspace_id,
            user_id=user_id,
            rate=rate,
            environment=environment
        )
    
    def start_masscan_scan(self, *args, **kwargs):
        """Alias para start_masscan para compatibilidad."""
        return self.start_masscan(*args, **kwargs)
    
    def preview_masscan(
        self,
        target: str,
        ports: str,
        workspace_id: int,
        rate: int = 1000,
        environment: str = 'internal'
    ) -> Dict[str, Any]:
        """Preview del comando Masscan."""
        return self.masscan_scanner.preview_scan(
            target=target,
            ports=ports,
            workspace_id=workspace_id,
            rate=rate,
            environment=environment
        )
    
    # ============================================
    # NAABU
    # ============================================
    
    def start_naabu(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        top_ports: Optional[int] = None,
        rate: int = 1000,
        verify: bool = True
    ) -> Dict[str, Any]:
        """Inicia Naabu (port discovery rápido)."""
        return self.naabu_scanner.start_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            top_ports=top_ports,
            rate=rate,
            verify=verify
        )
    
    def preview_naabu(
        self,
        target: str,
        workspace_id: int,
        top_ports: Optional[int] = None,
        rate: int = 1000,
        verify: bool = True
    ) -> Dict[str, Any]:
        """Preview del comando Naabu."""
        return self.naabu_scanner.preview_scan(
            target=target,
            workspace_id=workspace_id,
            top_ports=top_ports,
            rate=rate,
            verify=verify
        )
    
    # ============================================
    # GET RESULTS
    # ============================================
    
    def get_scan_status(self, scan_id: int) -> Dict[str, Any]:
        """Obtiene estado del scan."""
        scan = self.scan_repo.find_by_id(scan_id)
        
        if not scan:
            raise ValueError(f'Scan {scan_id} not found')
        
        return {
            'scan_id': scan.id,
            'status': scan.status,
            'progress': scan.progress,
            'target': scan.target,
            'scan_type': scan.scan_type,
            'tool': scan.options.get('tool'),
            'started_at': scan.started_at.isoformat() if scan.started_at else None,
            'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
            'error': scan.error
        }
    
    def get_scan_results(self, scan_id: int) -> Dict[str, Any]:
        """
        Obtiene y parsea resultados del scan.
        
        Args:
            scan_id: ID del escaneo
        
        Returns:
            Dict con resultados parseados
        """
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
        
        try:
            workspace_output_dir = get_workspace_output_dir_from_scan(scan_id, 'scans')
            
            if tool == 'nmap':
                xml_file = workspace_output_dir / f'nmap_{scan_id}.xml'
                if xml_file.exists():
                    results = self.nmap_parser.parse_xml(str(xml_file))
                    vulnerabilities = self.nmap_parser.extract_vulnerabilities(results)
                    if vulnerabilities:
                        results['vulnerabilities'] = vulnerabilities
                else:
                    results = {}
            
            elif tool == 'rustscan':
                output_file = workspace_output_dir / f'rustscan_{scan_id}.txt'
                if output_file.exists():
                    with open(output_file, 'r') as f:
                        output = f.read()
                    results = self.rustscan_parser.parse_output(output)
                else:
                    results = {}
            
            elif tool == 'masscan':
                output_file = workspace_output_dir / f'masscan_{scan_id}.json'
                if output_file.exists():
                    with open(output_file, 'r') as f:
                        output = f.read()
                    results = self.masscan_parser.parse_output(output)
                else:
                    results = {}
            
            elif tool == 'naabu':
                output_file = workspace_output_dir / f'naabu_{scan_id}.txt'
                if output_file.exists():
                    with open(output_file, 'r') as f:
                        output = f.read()
                    results = json.loads(output) if output else {}
                else:
                    results = {}
            
            else:
                results = {'error': f'Unknown tool: {tool}'}
            
            return {
                'scan_id': scan_id,
                'status': 'completed',
                'tool': tool,
                'results': results,
                'scan_info': {
                    'target': scan.target,
                    'started_at': scan.started_at.isoformat() if scan.started_at else None,
                    'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
                }
            }
            
        except Exception as e:
            log_to_workspace(
                workspace_id=scan.workspace_id,
                source='BACKEND',
                level='WARNING',
                message=f"Error parsing scan results {scan_id}: {str(e)}",
                metadata={'scan_id': scan_id}
            )
            return {
                'scan_id': scan_id,
                'error': f'Failed to parse results: {str(e)}'
            }
    
    # ============================================
    # ENUMERACIÓN SMB/CIFS - Delegación
    # ============================================
    
    def start_enum4linux(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a SMBEnumerationService."""
        return self.smb_enum.start_enum4linux(target, workspace_id, user_id, **kwargs)
    
    def start_smbmap(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a SMBEnumerationService."""
        return self.smb_enum.start_smbmap(target, workspace_id, user_id, **kwargs)
    
    def start_smbclient(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a SMBEnumerationService."""
        return self.smb_enum.start_smbclient(target, workspace_id, user_id, **kwargs)
    
    # ============================================
    # ENUMERACIÓN SERVICIOS DE RED - Delegación
    # ============================================
    
    def start_ssh_enum(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a NetworkServicesEnumerationService."""
        return self.network_enum.start_ssh_enum(target, workspace_id, user_id, **kwargs)
    
    def start_ftp_enum(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a NetworkServicesEnumerationService."""
        return self.network_enum.start_ftp_enum(target, workspace_id, user_id, **kwargs)
    
    def start_smtp_enum(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a NetworkServicesEnumerationService."""
        return self.network_enum.start_smtp_enum(target, workspace_id, user_id, **kwargs)
    
    def start_dns_enum(self, target: str, workspace_id: int, user_id: int, domain: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Delega a NetworkServicesEnumerationService."""
        return self.network_enum.start_dns_enum(target, workspace_id, user_id, domain=domain, **kwargs)
    
    def start_snmp_enum(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a NetworkServicesEnumerationService."""
        return self.network_enum.start_snmp_enum(target, workspace_id, user_id, **kwargs)
    
    def start_ldap_enum(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a NetworkServicesEnumerationService."""
        return self.network_enum.start_ldap_enum(target, workspace_id, user_id, **kwargs)
    
    def start_rdp_enum(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a NetworkServicesEnumerationService."""
        return self.network_enum.start_rdp_enum(target, workspace_id, user_id, **kwargs)
    
    # ============================================
    # PREVIEW METHODS - ENUMERATION
    # ============================================
    
    def preview_ftp_enum(self, target: str, workspace_id: int, port: int = 21) -> Dict[str, Any]:
        """Preview del comando FTP enum."""
        return self.network_enum.preview_ftp_enum(target, workspace_id, port)
    
    def preview_dns_enum(self, target: str, workspace_id: int, domain: Optional[str] = None, tool: str = 'nmap', port: int = 53) -> Dict[str, Any]:
        """Preview del comando DNS enum."""
        return self.network_enum.preview_dns_enum(target, workspace_id, domain, tool, port)
    
    def preview_rdp_enum(self, target: str, workspace_id: int, port: int = 3389) -> Dict[str, Any]:
        """Preview del comando RDP enum."""
        return self.network_enum.preview_rdp_enum(target, workspace_id, port)
    
    def preview_ssh_enum(self, target: str, workspace_id: int, tool: str = 'nmap', port: int = 22) -> Dict[str, Any]:
        """Preview del comando SSH enum."""
        return self.network_enum.preview_ssh_enum(target, workspace_id, tool, port)
    
    def preview_smtp_enum(self, target: str, workspace_id: int, tool: str = 'nmap', port: int = 25, userlist: Optional[str] = None) -> Dict[str, Any]:
        """Preview del comando SMTP enum."""
        return self.network_enum.preview_smtp_enum(target, workspace_id, tool, port, userlist)
    
    def preview_snmp_enum(self, target: str, workspace_id: int, tool: str = 'nmap', port: int = 161, community: str = 'public', community_file: Optional[str] = None) -> Dict[str, Any]:
        """Preview del comando SNMP enum."""
        return self.network_enum.preview_snmp_enum(target, workspace_id, tool, port, community, community_file)
    
    def preview_ldap_enum(self, target: str, workspace_id: int, tool: str = 'nmap', port: int = 389, base_dn: Optional[str] = None) -> Dict[str, Any]:
        """Preview del comando LDAP enum."""
        return self.network_enum.preview_ldap_enum(target, workspace_id, tool, port, base_dn)
    
    def preview_enum4linux(self, target: str, workspace_id: int, use_ng: bool = True, all: bool = False) -> Dict[str, Any]:
        """Preview del comando enum4linux."""
        return self.smb_enum.preview_enum4linux(target, workspace_id, use_ng, all)
    
    def preview_smbmap(self, target: str, workspace_id: int, username: Optional[str] = None,
                       password: Optional[str] = None, hash: Optional[str] = None,
                       recursive: bool = False, share: Optional[str] = None) -> Dict[str, Any]:
        """Preview del comando smbmap."""
        return self.smb_enum.preview_smbmap(target, workspace_id, username, password, hash, recursive, share)
    
    def preview_smbclient(self, target: str, workspace_id: int, share: str,
                          username: Optional[str] = None, password: Optional[str] = None,
                          command: Optional[str] = None) -> Dict[str, Any]:
        """Preview del comando smbclient."""
        return self.smb_enum.preview_smbclient(target, workspace_id, share, username, password, command)
    
    def preview_mysql_enum(self, target: str, workspace_id: int, tool: str = 'nmap', port: int = 3306, username: Optional[str] = None) -> Dict[str, Any]:
        """Preview del comando MySQL enum."""
        return self.database_enum.preview_mysql_enum(target, workspace_id, tool, port, username)
    
    def preview_postgresql_enum(self, target: str, workspace_id: int, tool: str = 'nmap', port: int = 5432, username: str = 'postgres') -> Dict[str, Any]:
        """Preview del comando PostgreSQL enum."""
        return self.database_enum.preview_postgresql_enum(target, workspace_id, tool, port, username)
    
    def preview_redis_enum(self, target: str, workspace_id: int, tool: str = 'nmap', port: int = 6379) -> Dict[str, Any]:
        """Preview del comando Redis enum."""
        return self.database_enum.preview_redis_enum(target, workspace_id, tool, port)
    
    def preview_mongodb_enum(self, target: str, workspace_id: int, port: int = 27017) -> Dict[str, Any]:
        """Preview del comando MongoDB enum."""
        return self.database_enum.preview_mongodb_enum(target, workspace_id, port)
    
    def preview_sslscan(self, target: str, workspace_id: int, port: int = 443, show_certificate: bool = False) -> Dict[str, Any]:
        """Preview del comando sslscan."""
        return self.ssl_enum.preview_sslscan(target, workspace_id, port, show_certificate)
    
    def preview_sslyze(self, target: str, workspace_id: int, port: int = 443, regular: bool = True) -> Dict[str, Any]:
        """Preview del comando sslyze."""
        return self.ssl_enum.preview_sslyze(target, workspace_id, port, regular)
    
    # ============================================
    # ENUMERACIÓN BASES DE DATOS - Delegación
    # ============================================
    
    def start_mysql_enum(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a DatabaseEnumerationService."""
        return self.database_enum.start_mysql_enum(target, workspace_id, user_id, **kwargs)
    
    def start_postgresql_enum(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a DatabaseEnumerationService."""
        return self.database_enum.start_postgresql_enum(target, workspace_id, user_id, **kwargs)
    
    def start_redis_enum(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a DatabaseEnumerationService."""
        return self.database_enum.start_redis_enum(target, workspace_id, user_id, **kwargs)
    
    def start_mongodb_enum(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a DatabaseEnumerationService."""
        return self.database_enum.start_mongodb_enum(target, workspace_id, user_id, **kwargs)
    
    # ============================================
    # ANÁLISIS SSL/TLS - Delegación
    # ============================================
    
    def start_sslscan(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a SSLEnumerationService."""
        return self.ssl_enum.start_sslscan(target, workspace_id, user_id, **kwargs)
    
    def start_sslyze(self, target: str, workspace_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """Delega a SSLEnumerationService."""
        return self.ssl_enum.start_sslyze(target, workspace_id, user_id, **kwargs)


