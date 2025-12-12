"""
Parser Manager
==============

Gestiona la selección y ejecución de parsers.
Registra parsers disponibles y selecciona el apropiado para cada archivo.
"""

from pathlib import Path
from typing import List, Optional
from .base_parser import BaseParser, ParsedFinding
import logging

# Importar parsers implementados
from .scanning.nmap_parser import NmapParser
from .scanning.rustscan_parser import RustScanParser
from .scanning.masscan_parser import MasscanParser
from .scanning.naabu_parser import NaabuParser
from .vulnerability.nuclei_parser import NucleiParser
from .vulnerability.nikto_parser import NiktoParser
from .vulnerability.sqlmap_parser import SQLMapParser
from .vulnerability.owasp_zap_parser import OWASPZAPParser
from .vulnerability.wpscan_parser import WPScanParser
from .reconnaissance.subfinder_parser import SubfinderParser
from .reconnaissance.amass_parser import AmassParser

# Subdomain parsers
from .reconnaissance.subdomain.assetfinder_parser import AssetfinderParser
from .reconnaissance.subdomain.sublist3r_parser import Sublist3rParser
from .reconnaissance.subdomain.findomain_parser import FindomainParser
from .reconnaissance.subdomain.crtsh_parser import CrtshParser

# DNS parsers
from .reconnaissance.dns.dnsrecon_parser import DNSReconParser
from .reconnaissance.dns.fierce_parser import FierceParser
from .reconnaissance.dns.dnsenum_parser import DNSEnumParser
from .reconnaissance.dns.traceroute_parser import TracerouteParser

# OSINT parsers
from .reconnaissance.osint.shodan_parser import ShodanParser
from .reconnaissance.osint.censys_parser import CensysParser
from .reconnaissance.osint.theharvester_parser import TheHarvesterParser
from .reconnaissance.osint.hunterio_parser import HunterioParser
from .reconnaissance.osint.wayback_parser import WaybackParser

# Web parsers
from .reconnaissance.web.whatweb_parser import WhatWebParser
from .reconnaissance.web.webcrawler_parser import WebCrawlerParser

# Other parsers
from .reconnaissance.other.whois_parser import WhoisParser
from .reconnaissance.other.googledorks_parser import GoogleDorksParser
from .reconnaissance.other.secrets_parser import SecretsParser

# SSL Enumeration parsers
from .enumeration.ssl.testssl_parser import TestSSLParser
from .enumeration.ssl.sslscan_parser import SSLScanParser
from .enumeration.ssl.sslyze_parser import SSLyzeParser

# SMB Enumeration parsers
from .enumeration.smb.enum4linux_parser import Enum4linuxParser
from .enumeration.smb.smbmap_parser import SMBMapParser
from .enumeration.smb.smbclient_parser import SMBClientParser

# Network Services Enumeration parsers
from .enumeration.network.ssh_audit_parser import SSHAuditParser
from .enumeration.network.smtp_enum_parser import SMTPEnumParser
from .enumeration.network.dns_zone_parser import DNSZoneParser
from .enumeration.network.snmpwalk_parser import SNMPWalkParser
from .enumeration.network.onesixtyone_parser import OneSixtyOneParser
from .enumeration.network.ldapsearch_parser import LDAPSearchParser

# Database Enumeration parsers
from .enumeration.database.mysql_enum_parser import MySQLEnumParser
from .enumeration.database.postgresql_enum_parser import PostgreSQLEnumParser
from .enumeration.database.redis_enum_parser import RedisEnumParser


class ParserManager:
    """
    Gestiona la selección y ejecución de parsers.
    
    Mantiene un registro de todos los parsers disponibles y selecciona
    automáticamente el parser apropiado para cada archivo.
    """
    
    def __init__(self):
        """Inicializa el manager y registra parsers por defecto."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.parsers: List[BaseParser] = []
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """Registra los parsers por defecto implementados."""
        default_parsers = [
            # Port Scanning parsers
            NmapParser(),
            RustScanParser(),
            MasscanParser(),
            NaabuParser(),
            # Vulnerability parsers
            NucleiParser(),
            NiktoParser(),
            SQLMapParser(),
            OWASPZAPParser(),
            WPScanParser(),
            # SSL Enumeration parsers
            TestSSLParser(),
            SSLScanParser(),
            SSLyzeParser(),
            # SMB Enumeration parsers
            Enum4linuxParser(),
            SMBMapParser(),
            SMBClientParser(),
            # Network Services Enumeration parsers
            SSHAuditParser(),
            SMTPEnumParser(),
            DNSZoneParser(),
            SNMPWalkParser(),
            OneSixtyOneParser(),
            LDAPSearchParser(),
            # Database Enumeration parsers
            MySQLEnumParser(),
            PostgreSQLEnumParser(),
            RedisEnumParser(),
            # Reconnaissance parsers
            SubfinderParser(),
            AmassParser(),
            # Subdomain parsers
            AssetfinderParser(),
            Sublist3rParser(),
            FindomainParser(),
            CrtshParser(),
            # DNS parsers
            DNSReconParser(),
            FierceParser(),
            DNSEnumParser(),
            TracerouteParser(),
            # OSINT parsers
            ShodanParser(),
            CensysParser(),
            TheHarvesterParser(),
            HunterioParser(),
            WaybackParser(),
            # Web parsers
            WhatWebParser(),
            WebCrawlerParser(),
            # Other parsers
            WhoisParser(),
            GoogleDorksParser(),
            SecretsParser(),
            # Agregar más parsers aquí según se implementen
        ]
        
        for parser in default_parsers:
            self.register_parser(parser)
        
        self.logger.info(f"Registered {len(self.parsers)} parsers")
    
    def register_parser(self, parser: BaseParser):
        """
        Registra un nuevo parser.
        
        Args:
            parser: Instancia del parser a registrar
        """
        self.parsers.append(parser)
        self.logger.debug(f"Registered parser: {parser.__class__.__name__}")
    
    def get_parser(self, file_path: Path) -> Optional[BaseParser]:
        """
        Obtiene el parser apropiado para un archivo.
        
        Itera sobre todos los parsers registrados y retorna el primero
        que puede procesar el archivo (según can_parse()).
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Parser capaz de procesar el archivo, o None si no hay ninguno
        """
        for parser in self.parsers:
            if parser.can_parse(file_path):
                self.logger.debug(
                    f"Selected {parser.__class__.__name__} for {file_path.name}"
                )
                return parser
        
        self.logger.warning(f"No parser found for {file_path}")
        return None
    
    def parse_file(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea un archivo usando el parser apropiado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings parseados (vacía si no hay parser o falla)
        """
        findings, _ = self.parse_file_with_parser(file_path)
        return findings
    
    def parse_file_with_parser(self, file_path: Path) -> tuple[List[ParsedFinding], Optional[str]]:
        """
        Parsea un archivo usando el parser apropiado y retorna también el nombre del parser.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Tupla (findings, parser_name):
            - findings: Lista de findings parseados (vacía si no hay parser o falla)
            - parser_name: Nombre de la herramienta detectada (ej: 'nmap', 'nuclei') o None
        """
        parser = self.get_parser(file_path)
        
        if parser is None:
            self.logger.warning(
                f"Cannot parse {file_path}: no suitable parser"
            )
            # Intentar extraer del nombre del archivo como fallback
            parser_name = self._extract_tool_from_filename(file_path)
            return [], parser_name
        
        try:
            findings = parser.parse(file_path)
            parser_name = self._get_tool_name_from_parser(parser)
            self.logger.info(
                f"Parsed {len(findings)} findings from {file_path.name} using {parser_name}"
            )
            return findings, parser_name
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            parser_name = self._get_tool_name_from_parser(parser) if parser else None
            return [], parser_name
    
    def _get_tool_name_from_parser(self, parser: BaseParser) -> str:
        """
        Extrae el nombre de la herramienta del nombre de la clase del parser.
        
        Ejemplos:
        - NmapParser -> 'nmap'
        - NucleiParser -> 'nuclei'
        - Enum4linuxParser -> 'enum4linux'
        - SSHAuditParser -> 'ssh_audit'
        
        Args:
            parser: Instancia del parser
            
        Returns:
            Nombre de la herramienta en minúsculas
        """
        class_name = parser.__class__.__name__
        
        # Remover 'Parser' del final
        if class_name.endswith('Parser'):
            tool_name = class_name[:-6]  # Remover 'Parser'
        else:
            tool_name = class_name
        
        # Convertir PascalCase a snake_case y luego a minúsculas simples
        # Ej: Enum4linuxParser -> Enum4linux -> enum4linux
        # Ej: SSHAuditParser -> SSHAudit -> ssh_audit
        import re
        # Insertar guión bajo antes de mayúsculas seguidas de minúsculas
        tool_name = re.sub(r'(?<!^)(?=[A-Z][a-z])', '_', tool_name)
        # Convertir a minúsculas
        tool_name = tool_name.lower()
        
        # Casos especiales conocidos
        tool_mapping = {
            'ssh_audit': 'ssh-audit',
            'dns_zone': 'dns-zone-transfer',
            'smtp_enum': 'smtp-enum',
            'ldap_search': 'ldapsearch',
            'one_sixty_one': 'onesixtyone',
            'snmp_walk': 'snmpwalk',
            'mysql_enum': 'mysql-enum',
            'postgresql_enum': 'postgresql-enum',
            'redis_enum': 'redis-enum',
            'enum4linux': 'enum4linux',
            'smb_map': 'smbmap',
            'smb_client': 'smbclient',
            'ssl_scan': 'sslscan',
            'ssl_yze': 'sslyze',
            'test_ssl': 'testssl',
            'dns_recon': 'dnsrecon',
            'dns_enum': 'dnsenum',
            'the_harvester': 'theharvester',
            'google_dorks': 'googledorks',
            'web_crawler': 'webcrawler',
            'what_web': 'whatweb',
            'sub_list3r': 'sublist3r',
            'crt_sh': 'crtsh',
            'owasp_zap': 'owasp-zap',
            'wp_scan': 'wpscan',
            'sql_map': 'sqlmap',
        }
        
        return tool_mapping.get(tool_name, tool_name)
    
    def _extract_tool_from_filename(self, file_path: Path) -> Optional[str]:
        """
        Intenta extraer el nombre de la herramienta del nombre del archivo.
        
        Ejemplos:
        - nmap_scan.xml -> 'nmap'
        - nuclei_results.jsonl -> 'nuclei'
        - nikto_output.json -> 'nikto'
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Nombre de la herramienta detectado o None
        """
        filename = file_path.name.lower()
        
        # Lista de herramientas conocidas y patrones
        tool_patterns = {
            'nmap': ['nmap', 'nmap_scan', 'nmap_result'],
            'nuclei': ['nuclei', 'nuclei_result', 'nuclei_output'],
            'nikto': ['nikto', 'nikto_result', 'nikto_output'],
            'subfinder': ['subfinder', 'subfinder_result'],
            'amass': ['amass', 'amass_result'],
            'masscan': ['masscan', 'masscan_result'],
            'rustscan': ['rustscan', 'rustscan_result'],
            'naabu': ['naabu', 'naabu_result'],
            'sqlmap': ['sqlmap', 'sqlmap_result'],
            'wpscan': ['wpscan', 'wp_scan'],
            'enum4linux': ['enum4linux', 'enum4linux_result'],
            'smbmap': ['smbmap', 'smbmap_result'],
            'sslscan': ['sslscan', 'sslscan_result'],
            'sslyze': ['sslyze', 'sslyze_result'],
            'testssl': ['testssl', 'testssl_result'],
            'ssh-audit': ['ssh_audit', 'ssh-audit'],
            'dnsrecon': ['dnsrecon', 'dns_recon'],
            'theharvester': ['theharvester', 'the_harvester'],
            'shodan': ['shodan', 'shodan_result'],
            'censys': ['censys', 'censys_result'],
        }
        
        for tool_name, patterns in tool_patterns.items():
            for pattern in patterns:
                if pattern in filename:
                    return tool_name
        
        return None
