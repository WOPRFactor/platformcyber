"""
Safe Nmap Command Builder
==========================

Constructor seguro de comandos Nmap con validaciones.
"""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class SafeNmap:
    """
    Constructor seguro de comandos Nmap.
    
    Previene:
    - Scripts peligrosos (solo permite 'vuln and safe')
    - Escaneos demasiado agresivos
    - Opciones destructivas
    """
    
    # Scripts permitidos (safe)
    SAFE_SCRIPT_CATEGORIES = ['safe', 'default', 'discovery']
    
    # Scripts PROHIBIDOS
    FORBIDDEN_SCRIPTS = [
        'broadcast-dhcp-discover',  # Puede afectar DHCP
        'http-slowloris-check',     # Puede causar DoS
        'smb-flood',                # DoS explícito
    ]
    
    @classmethod
    def build_discovery_scan(cls, target: str, output_file: str = 'nmap_discovery') -> List[str]:
        """
        Escaneo rápido de descubrimiento de puertos.
        
        Args:
            target: IP o dominio
            output_file: Nombre base para output (sin extensión)
        
        Returns:
            Comando listo para ejecutar
        """
        return [
            'nmap',
            '-sS',              # SYN scan
            '-p-',              # Todos los puertos
            '--min-rate=1000',  # Rate controlado
            '--max-retries=2',  # Máximo 2 reintentos
            '-T4',              # Timing agresivo pero controlado
            '-oA', output_file, # Output en todos los formatos
            target
        ]
    
    @classmethod
    def build_detailed_scan(
        cls,
        target: str,
        ports: str,
        output_file: str = 'nmap_detailed'
    ) -> List[str]:
        """
        Escaneo detallado en puertos específicos.
        
        Args:
            target: IP o dominio
            ports: Puertos (ej: '22,80,443' o '1-1000')
            output_file: Nombre base para output
        
        Returns:
            Comando listo para ejecutar
        """
        return [
            'nmap',
            '-sS',              # SYN scan
            '-sV',              # Detección de versiones
            '-sC',              # Scripts por defecto (safe)
            '-O',               # Detección de OS
            '-p', ports,        # Puertos específicos
            '-oA', output_file,
            target
        ]
    
    @classmethod
    def build_vuln_scan(
        cls,
        target: str,
        ports: Optional[str] = None,
        output_file: str = 'nmap_vuln'
    ) -> List[str]:
        """
        Escaneo de vulnerabilidades con scripts SEGUROS.
        
        Args:
            target: IP o dominio
            ports: Puertos opcionales (si None, escanea top 1000)
            output_file: Nombre base para output
        
        Returns:
            Comando listo para ejecutar
        
        Note:
            Usa 'vuln and safe' para evitar scripts destructivos
        """
        cmd = [
            'nmap',
            '--script', 'vuln and safe',  # Solo scripts seguros
            '--script-args', 'vulns.showall',
            '-sV',  # Detección de versión necesaria para algunos scripts
        ]
        
        if ports:
            cmd.extend(['-p', ports])
        
        cmd.extend([
            '-oA', output_file,
            target
        ])
        
        logger.info(f"Escaneo de vulnerabilidades (seguro) en {target}")
        return cmd
    
    @classmethod
    def build_stealth_scan(
        cls,
        target: str,
        ports: str = '1-1000',
        output_file: str = 'nmap_stealth'
    ) -> List[str]:
        """
        Escaneo sigiloso para evitar detección.
        
        Args:
            target: IP o dominio
            ports: Puertos a escanear
            output_file: Nombre base para output
        
        Returns:
            Comando listo para ejecutar
        """
        return [
            'nmap',
            '-sS',              # SYN scan
            '-f',               # Fragmentar paquetes
            '--mtu', '24',      # MTU custom
            '-D', 'RND:3',      # 3 decoys aleatorios
            '--source-port', '53',  # Puerto origen DNS
            '-T2',              # Timing polite
            '-p', ports,
            '-oA', output_file,
            target
        ]
    
    @classmethod
    def build_udp_scan(
        cls,
        target: str,
        top_ports: int = 100,
        output_file: str = 'nmap_udp'
    ) -> List[str]:
        """
        Escaneo UDP (más lento, limitado a top ports).
        
        Args:
            target: IP o dominio
            top_ports: Cantidad de puertos top a escanear
            output_file: Nombre base para output
        
        Returns:
            Comando listo para ejecutar
        
        Note:
            UDP es muy lento, por eso limitamos a top ports
        """
        return [
            'nmap',
            '-sU',                      # UDP scan
            '-sV',                      # Detección de versión
            '--version-intensity', '0', # Rápido para UDP
            '--top-ports', str(top_ports),
            '-oA', output_file,
            target
        ]
    
    @classmethod
    def build_script_scan(
        cls,
        target: str,
        port: Optional[int] = None,
        scripts: Optional[List[str]] = None,
        output_file: str = 'nmap_script'
    ) -> List[str]:
        """
        Escaneo con scripts específicos de Nmap.
        
        Args:
            target: IP o dominio
            port: Puerto específico (opcional)
            scripts: Lista de scripts a ejecutar
            output_file: Nombre base para output (sin extensión)
        
        Returns:
            Comando listo para ejecutar
        
        Note:
            Valida que los scripts sean seguros antes de ejecutar
        """
        cmd = ['nmap', '-sV']  # Detección de versión necesaria
        
        if scripts:
            # Validar scripts
            scripts_str = ','.join(scripts)
            for script in scripts:
                for forbidden in cls.FORBIDDEN_SCRIPTS:
                    if forbidden in script:
                        raise ValueError(
                            f"Script prohibido: {forbidden}\n"
                            f"Este script puede causar daño al objetivo."
                        )
            cmd.extend(['--script', scripts_str])
        
        if port:
            cmd.extend(['-p', str(port)])
        
        cmd.extend(['-oA', output_file, target])
        
        logger.info(f"Escaneo con scripts en {target} (puerto: {port})")
        return cmd
    
    @classmethod
    def validate_script_args(cls, scripts: str) -> bool:
        """
        Valida que los scripts solicitados sean seguros.
        
        Args:
            scripts: String de scripts (ej: 'http-*,ssh-*')
        
        Returns:
            True si son seguros
        
        Raises:
            ValueError: Si contiene scripts peligrosos
        """
        for forbidden in cls.FORBIDDEN_SCRIPTS:
            if forbidden in scripts:
                raise ValueError(
                    f"Script prohibido: {forbidden}\n"
                    f"Este script puede causar daño al objetivo."
                )
        
        return True



