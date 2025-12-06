"""
DNS Enumeration Module
=======================

Módulo para enumeración y consultas DNS.
Herramientas: DNSRecon, DNS Lookup (host/nslookup), DNS Enum Alt (dnsenum/fierce), Traceroute
"""

import logging
import threading
from typing import Dict, Any, Optional, List

from utils.validators import CommandSanitizer, DomainValidator
from utils.workspace_logger import log_to_workspace
from .base import BaseReconnaissanceService

logger = logging.getLogger(__name__)


class DNSEnumerationService(BaseReconnaissanceService):
    """Servicio para enumeración DNS."""
    
    def start_dns_recon(
        self,
        domain: str,
        workspace_id: int,
        user_id: int,
        record_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Inicia reconocimiento DNS.
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            record_types: Tipos de registros (A, AAAA, MX, NS, TXT, SOA)
        
        Returns:
            Dict con información del escaneo
        """
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        if not record_types:
            record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
        
        scan = self.scan_repo.create(
            scan_type='reconnaissance',
            target=domain,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'dnsrecon',
                'recon_type': 'dns',
                'record_types': record_types
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
            output_file = str(workspace_output_dir / f'dnsrecon_{scan.id}.json')
            command = ['dnsrecon', '-d', domain, '-t', 'std', '-j', output_file]
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting DNS recon {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'dns')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'dnsrecon',
                'target': domain
            }
            
        except Exception as e:
            logger.error(f"Error starting DNS recon: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def preview_dns_recon(
        self,
        domain: str,
        workspace_id: int,
        record_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Preview del comando DNS recon (sin ejecutar).
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            record_types: Tipos de registros (A, AAAA, MX, NS, TXT, SOA)
        
        Returns:
            Dict con información del comando que se ejecutaría
        """
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        if not record_types:
            record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
        
        output_file = f'/workspaces/workspace_{workspace_id}/recon/dnsrecon_{{scan_id}}.json'
        command = ['dnsrecon', '-d', domain, '-t', 'std', '-j', output_file]
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'dnsrecon',
                'domain': domain,
                'record_types': record_types
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_dns_lookup(
        self,
        domain: str,
        workspace_id: int,
        tool: str = 'host',
        record_type: Optional[str] = None,
        dns_server: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Preview del comando DNS lookup (sin ejecutar).
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            tool: Herramienta ('host' o 'nslookup')
            record_type: Tipo de registro (A, MX, NS, TXT, SOA, etc.)
            dns_server: Servidor DNS específico (opcional)
        
        Returns:
            Dict con información del comando que se ejecutaría
        """
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        if tool not in ['host', 'nslookup']:
            raise ValueError(f'Invalid tool: {tool}. Must be "host" or "nslookup"')
        
        command = self._build_dns_lookup_command(tool, domain, record_type, dns_server)
        command_str = ' '.join(command)
        output_file = f'/workspaces/workspace_{workspace_id}/recon/{tool}_{{scan_id}}.txt'
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': tool,
                'domain': domain,
                'record_type': record_type,
                'dns_server': dns_server
            },
            'estimated_timeout': 30,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def start_dns_lookup(
        self,
        domain: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'host',
        record_type: Optional[str] = None,
        dns_server: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Consultas DNS simples con host o nslookup.
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            tool: Herramienta ('host' o 'nslookup')
            record_type: Tipo de registro (A, MX, NS, TXT, SOA, etc.)
            dns_server: Servidor DNS específico (opcional)
        
        Returns:
            Dict con información del escaneo
        """
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        if tool not in ['host', 'nslookup']:
            raise ValueError(f'Invalid tool: {tool}. Must be "host" or "nslookup"')
        
        scan = self.scan_repo.create(
            scan_type='reconnaissance',
            target=domain,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': tool,
                'recon_type': 'dns_lookup',
                'record_type': record_type
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
            output_file = str(workspace_output_dir / f'{tool}_{scan.id}.txt')
            command = self._build_dns_lookup_command(tool, domain, record_type, dns_server)
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            log_to_workspace(
                workspace_id=workspace_id,
                source=tool.upper(),
                level='INFO',
                message=f"Iniciando {tool} lookup para {domain}",
                metadata={'scan_id': scan.id, 'domain': domain, 'record_type': record_type}
            )
            
            logger.info(f"Starting {tool} lookup {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, tool)
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': tool,
                'domain': domain
            }
            
        except Exception as e:
            logger.error(f"Error starting {tool} lookup: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def _build_dns_lookup_command(
        self,
        tool: str,
        domain: str,
        record_type: Optional[str],
        dns_server: Optional[str]
    ) -> list:
        """Construye comando DNS lookup."""
        if tool == 'host':
            cmd = ['host', domain]
            if record_type:
                cmd.extend(['-t', record_type])
            if dns_server:
                cmd.append(dns_server)
            return cmd
        else:  # nslookup
            cmd = ['nslookup']
            if record_type:
                cmd.append(f'-type={record_type}')
            cmd.append(domain)
            if dns_server:
                cmd.append(dns_server)
            return cmd
    
    def preview_traceroute(
        self,
        target: str,
        workspace_id: int,
        protocol: str = 'icmp',
        max_hops: int = 30
    ) -> Dict[str, Any]:
        """
        Preview del comando traceroute (sin ejecutar).
        
        Args:
            target: IP o dominio objetivo
            workspace_id: ID del workspace
            protocol: Protocolo ('icmp', 'tcp', 'udp')
            max_hops: Número máximo de saltos
        
        Returns:
            Dict con información del comando que se ejecutaría
        """
        command = ['traceroute', '-m', str(max_hops), target]
        
        if protocol == 'tcp':
            command.append('-T')
        elif protocol == 'udp':
            command.append('-U')
        
        command_str = ' '.join(command)
        output_file = f'/workspaces/workspace_{workspace_id}/recon/traceroute_{{scan_id}}.txt'
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'target': target,
                'protocol': protocol,
                'max_hops': max_hops
            },
            'estimated_timeout': 120,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def start_traceroute(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        protocol: str = 'icmp',
        max_hops: int = 30
    ) -> Dict[str, Any]:
        """
        Mapeo de ruta de red con traceroute.
        
        Args:
            target: IP o dominio objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            protocol: Protocolo ('icmp', 'tcp', 'udp')
            max_hops: Número máximo de saltos
        
        Returns:
            Dict con información del escaneo
        """
        scan = self.scan_repo.create(
            scan_type='reconnaissance',
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'traceroute',
                'recon_type': 'network_mapping',
                'protocol': protocol
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
            output_file = str(workspace_output_dir / f'traceroute_{scan.id}.txt')
            command = ['traceroute', '-m', str(max_hops), target]
            
            if protocol == 'tcp':
                command.append('-T')
            elif protocol == 'udp':
                command.append('-U')
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            log_to_workspace(
                workspace_id=workspace_id,
                source='TRACEROUTE',
                level='INFO',
                message=f"Iniciando traceroute ({protocol}) para {target}",
                metadata={'scan_id': scan.id, 'target': target, 'protocol': protocol}
            )
            
            logger.info(f"Starting traceroute {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'traceroute')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'traceroute',
                'target': target
            }
            
        except Exception as e:
            logger.error(f"Error starting traceroute: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def preview_dns_enum_alt(
        self,
        domain: str,
        workspace_id: int,
        tool: str = 'dnsenum',
        wordlist: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Preview del comando DNS enum alt (sin ejecutar).
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            tool: Herramienta ('dnsenum' o 'fierce')
            wordlist: Archivo wordlist para bruteforce (opcional)
        
        Returns:
            Dict con información del comando que se ejecutaría
        """
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        if tool not in ['dnsenum', 'fierce']:
            raise ValueError(f'Invalid tool: {tool}. Must be "dnsenum" or "fierce"')
        
        command = self._build_dns_enum_command(tool, domain, wordlist)
        command_str = ' '.join(command)
        output_file = f'/workspaces/workspace_{workspace_id}/recon/{tool}_{{scan_id}}.txt'
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': tool,
                'domain': domain,
                'wordlist': wordlist
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def start_dns_enum_alt(
        self,
        domain: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'dnsenum',
        wordlist: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enumeración DNS con dnsenum o fierce.
        
        Args:
            domain: Dominio objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            tool: Herramienta ('dnsenum' o 'fierce')
            wordlist: Archivo wordlist para bruteforce (opcional)
        
        Returns:
            Dict con información del escaneo
        """
        if not DomainValidator.is_valid_domain(domain):
            raise ValueError(f'Invalid domain: {domain}')
        
        if tool not in ['dnsenum', 'fierce']:
            raise ValueError(f'Invalid tool: {tool}. Must be "dnsenum" or "fierce"')
        
        scan = self.scan_repo.create(
            scan_type='reconnaissance',
            target=domain,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': tool,
                'recon_type': 'dns_enum',
                'wordlist': wordlist
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id, 'recon')
            output_file = str(workspace_output_dir / f'{tool}_{scan.id}.txt')
            
            # Validar que wordlist sea un string o None (no un dict u otro tipo)
            if wordlist is not None and not isinstance(wordlist, str):
                logger.warning(f"Invalid wordlist type: {type(wordlist)}, value: {wordlist}, ignoring wordlist")
                wordlist = None
            
            command = self._build_dns_enum_command(tool, domain, wordlist)
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            log_to_workspace(
                workspace_id=workspace_id,
                source=tool.upper(),
                level='INFO',
                message=f"Iniciando {tool} para {domain}",
                metadata={'scan_id': scan.id, 'domain': domain}
            )
            
            logger.info(f"Starting {tool} {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, tool)
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': tool,
                'domain': domain
            }
            
        except Exception as e:
            logger.error(f"Error starting {tool}: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def _build_dns_enum_command(
        self,
        tool: str,
        domain: str,
        wordlist: Optional[str]
    ) -> list:
        """Construye comando DNS enum."""
        if tool == 'dnsenum':
            if wordlist:
                # Con wordlist: dnsenum -f wordlist domain
                cmd = ['dnsenum', '-f', wordlist, domain]
            else:
                # Sin wordlist: dnsenum --enum domain (usa wordlist por defecto)
                cmd = ['dnsenum', '--enum', domain]
            return cmd
        else:  # fierce
            cmd = ['fierce', '--domain', domain]
            if wordlist:
                cmd.extend(['-w', wordlist])
            return cmd


