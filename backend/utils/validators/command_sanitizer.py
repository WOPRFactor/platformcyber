"""
Command Sanitizer
=================

Previene command injection validando comandos antes de ejecutarlos.

CRÍTICO: Todos los subprocess.run() deben pasar por aquí.
"""

import re
from typing import List, Optional, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CommandSanitizer:
    """
    Sanitizador de comandos para prevenir command injection.
    
    Ejemplo:
        >>> cmd = CommandSanitizer.sanitize_command('nmap', ['-sS', '192.168.1.1'])
        >>> # Retorna: ['nmap', '-sS', '192.168.1.1']
        
        >>> cmd = CommandSanitizer.sanitize_command('nmap', ['-sS', '127.0.0.1; rm -rf /'])
        >>> # Lanza: ValueError (patrón peligroso detectado)
    """
    
    # Whitelist de comandos permitidos
    ALLOWED_COMMANDS = {
        # Reconnaissance
        'whois', 'dig', 'host', 'nslookup', 'dnsrecon', 'dnsenum',
        'subfinder', 'amass', 'assetfinder', 'theHarvester', 'sublist3r',
        'waybackurls', 'shodan', 'findomain', 'traceroute', 'fierce',
        'censys', 'gitleaks', 'trufflehog', 'katana', 'gospider', 'hakrawler',
        'crosslinked', 'linkedin2username',
        
        # Scanning
        'nmap', 'rustscan', 'masscan', 'naabu',
        
        # Enumeration
        'enum4linux', 'enum4linux-ng', 'smbmap', 'smbclient',
        'ssh-audit', 'smtp-user-enum', 'snmpwalk', 'onesixtyone',
        'ldapsearch', 'mysql', 'psql', 'redis-cli',
        
        # Vulnerability Assessment
        'nuclei', 'nikto', 'wpscan', 'sqlmap', 'testssl.sh', 'sslscan',
        'feroxbuster', 'gobuster', 'ffuf', 'dirb',
        'dalfox', 'commix', 'tplmap', 'arjun', 'whatweb',
        'zap-baseline.py', 'zap-full-scan.py', 'zap-api-scan.py', 'zap-cli',
        
        # Exploitation
        'msfconsole', 'msfvenom', 'hydra', 'john', 'hashcat',
        'crackmapexec', 'evil-winrm', 'responder',
        
        # Post-Exploitation
        'mimikatz', 'lazagne', 'bloodhound', 'sharphound',
        
        # Active Directory
        'kerbrute', 'rubeus', 'powerview', 'impacket-psexec',
        'impacket-wmiexec', 'impacket-secretsdump', 'impacket-GetUserSPNs',
        
        # Cloud
        'aws', 'az', 'gcloud', 'pacu', 'prowler', 'scoutsuite',
        
        # Network Utilities (básicos)
        'ping', 'ping6', 'arp', 'netstat', 'ss', 'ifconfig', 'ip',
        'route', 'tcpdump', 'tshark', 'tcpflow', 'ngrep',
        
        # Utilities
        'curl', 'wget', 'nc', 'ssh', 'scp',
        
        # System commands (para herramientas que requieren root)
        'sudo'
    }
    
    # Patterns peligrosos que indican command injection
    DANGEROUS_PATTERNS = [
        r';',                    # Command separator
        r'\|',                   # Pipe
        r'&',                    # Background/AND
        r'`',                    # Command substitution
        r'\$\(',                 # Command substitution
        r'>',                    # Redirect output
        r'<',                    # Redirect input
        r'\n',                   # Newline
        r'\r',                   # Carriage return
        r'rm\s+-rf',            # Dangerous rm
        r'dd\s+if=',            # Disk operations
        r'mkfs',                # Format filesystem
        r':\(\)\{.*\|.*&\s*\};:', # Fork bomb
    ]
    
    # Opciones PROHIBIDAS por herramienta
    FORBIDDEN_OPTIONS = {
        'sqlmap': ['--dump-all', '--os-shell', '--os-cmd', '--sql-shell'],
        'nmap': ['--script=*vuln*'],  # Solo 'vuln and safe' permitido
        'hydra': [],  # Se validará rate limiting en otro lugar
        'masscan': [],  # Se validará rate en otro lugar
    }
    
    @classmethod
    def sanitize_command(
        cls,
        command: str,
        args: List[str],
        allow_unsafe: bool = False
    ) -> List[str]:
        """
        Valida y sanitiza un comando antes de ejecutarlo.
        
        Args:
            command: Comando base (ej: 'nmap')
            args: Lista de argumentos
            allow_unsafe: Si True, permite comandos no en whitelist (usar con cuidado)
        
        Returns:
            Lista [command, arg1, arg2, ...] validada
        
        Raises:
            ValueError: Si el comando o argumentos son peligrosos
        """
        # Validar comando base
        # Extraer nombre base del comando (último componente de la ruta)
        command_base = Path(command).name if '/' in command else command
        
        if not allow_unsafe and command_base not in cls.ALLOWED_COMMANDS:
            logger.error(f"Comando no permitido: {command}")
            raise ValueError(
                f"Comando '{command_base}' no está en la whitelist. "
                f"Comandos permitidos: {', '.join(sorted(cls.ALLOWED_COMMANDS))}"
            )
        
        # Validar argumentos
        full_command = ' '.join([command] + args)
        
        # Comandos que pueden tener URLs con caracteres especiales (como & en query strings)
        url_safe_commands = ['curl', 'wget']
        is_url_command = command_base in url_safe_commands
        
        for pattern in cls.DANGEROUS_PATTERNS:
            # Para comandos de URL (curl, wget), permitir & solo si está dentro de una URL válida
            if pattern == r'&' and is_url_command:
                # Verificar si el & está dentro de una URL (http:// o https://)
                url_pattern = r'https?://[^\s&]+&[^\s]*'
                if re.search(url_pattern, full_command):
                    # El & está dentro de una URL, es seguro
                    continue
            
            if re.search(pattern, full_command):
                logger.error(f"Patrón peligroso detectado: {pattern} en {full_command}")
                raise ValueError(
                    f"Patrón peligroso detectado: {pattern}\n"
                    f"Comando rechazado: {full_command}"
                )
        
        # Validar opciones prohibidas por herramienta
        if command in cls.FORBIDDEN_OPTIONS:
            for forbidden in cls.FORBIDDEN_OPTIONS[command]:
                if forbidden in args:
                    logger.error(f"Opción prohibida: {forbidden} para {command}")
                    raise ValueError(
                        f"Opción '{forbidden}' está prohibida para {command}"
                    )
        
        logger.info(f"Comando sanitizado: {command} {' '.join(args)}")
        return [command] + args
    
    @classmethod
    def validate_target(cls, target: str) -> bool:
        """
        Valida que el target sea una IP o dominio válido.
        
        Args:
            target: IP, dominio o rango de red
        
        Returns:
            True si es válido
        
        Raises:
            ValueError: Si el target es inválido
        """
        from .ip_validator import IPValidator
        from .domain_validator import DomainValidator
        
        # Intentar validar como IP
        if IPValidator.is_valid_ip(target):
            return True
        
        # Intentar validar como rango CIDR
        if IPValidator.is_valid_cidr(target):
            return True
        
        # Intentar validar como dominio
        if DomainValidator.is_valid_domain(target):
            return True
        
        logger.error(f"Target inválido: {target}")
        raise ValueError(
            f"Target '{target}' no es una IP, CIDR o dominio válido"
        )
    
    @classmethod
    def get_safe_env(cls) -> Dict[str, str]:
        """
        Retorna variables de entorno seguras para subprocess.
        
        Limita PATH y elimina variables peligrosas.
        """
        import os
        
        safe_env = {
            'PATH': '/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin',
            'HOME': os.environ.get('HOME', '/tmp'),
            'LANG': 'en_US.UTF-8',
        }
        
        return safe_env



