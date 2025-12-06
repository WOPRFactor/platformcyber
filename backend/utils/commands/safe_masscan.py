"""
Safe Masscan Command Builder
=============================

Constructor seguro de comandos Masscan con rate limiting.
"""

from typing import List
import logging

logger = logging.getLogger(__name__)


class SafeMasscan:
    """
    Constructor seguro de comandos Masscan.
    
    PREVIENE:
    - Rate > 1000 pps (puede causar DoS)
    - Escaneos sin límite de rate
    """
    
    # Límites de rate según entorno
    RATE_LIMITS = {
        'internal': 1000,   # Red interna (controlada)
        'external': 500,    # Internet / Red cliente
        'stealth': 100,     # Modo sigiloso
        'slow': 50          # Muy lento / producción crítica
    }
    
    # Rate máximo absoluto
    MAX_RATE = 1000
    
    @classmethod
    def build_scan(
        cls,
        target: str,
        ports: str = '1-65535',
        environment: str = 'internal',
        output_file: str = 'masscan_output.json'
    ) -> List[str]:
        """
        Construye comando Masscan con rate limiting.
        
        Args:
            target: IP o rango CIDR
            ports: Puertos a escanear (ej: '1-65535', '80,443,8080')
            environment: Tipo de entorno (internal/external/stealth/slow)
            output_file: Archivo de salida JSON
        
        Returns:
            Comando listo para ejecutar
        
        Raises:
            ValueError: Si el environment no es válido
        """
        if environment not in cls.RATE_LIMITS:
            raise ValueError(
                f"Environment '{environment}' no válido. "
                f"Opciones: {', '.join(cls.RATE_LIMITS.keys())}"
            )
        
        rate = cls.RATE_LIMITS[environment]
        
        # Validar y resolver target si es necesario
        import re
        import socket
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$'
        
        # Si no es IP o CIDR, intentar resolver como dominio
        if not re.match(ip_pattern, target):
            try:
                # Intentar resolver el dominio a IP
                resolved_ip = socket.gethostbyname(target)
                logger.info(f"Dominio '{target}' resuelto a IP: {resolved_ip}")
                target = resolved_ip
            except socket.gaierror:
                raise ValueError(
                    f"Masscan solo acepta IPs o rangos CIDR. "
                    f"Target recibido: '{target}' no es una IP válida ni se pudo resolver como dominio. "
                    f"Resuelve el dominio a IP primero o usa un rango CIDR."
                )
            except Exception as e:
                raise ValueError(
                    f"Error al resolver dominio '{target}': {str(e)}. "
                    f"Usa una IP o rango CIDR directamente."
                )
        
        # El target debe estar al final del comando (después de todas las opciones)
        # Masscan requiere permisos de root o capabilities.
        # ESTRATEGIA: Intentar sin sudo primero (si tiene capabilities configuradas)
        # Si falla, el servicio intentará con sudo -n (sin contraseña si está configurado)
        masscan_executable = 'masscan'
        
        # Intentar sin sudo primero (si masscan tiene capabilities configuradas funcionará)
        cmd = [
            masscan_executable,
            '-p', ports,
            '--rate', str(rate),
            '--max-rate', str(rate),  # Hard limit
            '--wait', '2',            # Esperar 2 segs al final
            '--banners',              # Capturar banners
            '--open-only',            # Solo puertos abiertos
            '-oJ', output_file,       # Output JSON
            target                     # Target al final (requerido por Masscan)
        ]
        
        logger.info(f"Masscan en {target} con rate {rate} pps (modo: {environment})")
        return cmd
    
    @classmethod
    def build_custom_rate_scan(
        cls,
        target: str,
        ports: str,
        rate: int,
        output_file: str = 'masscan_output.json'
    ) -> List[str]:
        """
        Escaneo con rate personalizado (limitado a MAX_RATE).
        
        Args:
            target: IP o rango CIDR
            ports: Puertos a escanear
            rate: Rate en paquetes/segundo
            output_file: Archivo de salida
        
        Returns:
            Comando listo para ejecutar
        
        Raises:
            ValueError: Si rate > MAX_RATE
        """
        if rate > cls.MAX_RATE:
            raise ValueError(
                f"Rate {rate} pps excede el máximo permitido ({cls.MAX_RATE} pps).\n"
                f"Para seguridad, el rate máximo es {cls.MAX_RATE} pps."
            )
        
        if rate < 1:
            raise ValueError("Rate debe ser >= 1 pps")
        
        # Validar y resolver target si es necesario
        import re
        import socket
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$'
        
        # Si no es IP o CIDR, intentar resolver como dominio
        if not re.match(ip_pattern, target):
            try:
                # Intentar resolver el dominio a IP
                resolved_ip = socket.gethostbyname(target)
                logger.info(f"Dominio '{target}' resuelto a IP: {resolved_ip}")
                target = resolved_ip
            except socket.gaierror:
                raise ValueError(
                    f"Masscan solo acepta IPs o rangos CIDR. "
                    f"Target recibido: '{target}' no es una IP válida ni se pudo resolver como dominio. "
                    f"Resuelve el dominio a IP primero o usa un rango CIDR."
                )
            except Exception as e:
                raise ValueError(
                    f"Error al resolver dominio '{target}': {str(e)}. "
                    f"Usa una IP o rango CIDR directamente."
                )
        
        # El target debe estar al final del comando (después de todas las opciones)
        # Masscan requiere permisos de root o capabilities. Intentar con sudo si está disponible
        import shutil
        sudo_path = shutil.which('sudo')
        masscan_executable = 'masscan'
        
        # Si sudo está disponible, usarlo (Masscan requiere root para raw sockets)
        if sudo_path:
            cmd = [
                sudo_path,
                masscan_executable,
                '-p', ports,
                '--rate', str(rate),
                '--max-rate', str(rate),
                '--wait', '2',
                '--banners',
                '--open-only',
                '-oJ', output_file,
                target                     # Target al final (requerido por Masscan)
            ]
        else:
            # Si no hay sudo, intentar sin él (puede fallar si no tiene capabilities)
            cmd = [
                masscan_executable,
                '-p', ports,
                '--rate', str(rate),
                '--max-rate', str(rate),
                '--wait', '2',
                '--banners',
                '--open-only',
                '-oJ', output_file,
                target                     # Target al final (requerido por Masscan)
            ]
        
        logger.info(f"Masscan en {target} con rate custom {rate} pps")
        return cmd
    
    @classmethod
    def build_top_ports_scan(
        cls,
        target: str,
        top_count: int = 1000,
        environment: str = 'internal',
        output_file: str = 'masscan_top_ports.json'
    ) -> List[str]:
        """
        Escaneo de top N puertos más comunes.
        
        Args:
            target: IP o rango CIDR
            top_count: Cantidad de top ports (100, 1000, etc)
            environment: Tipo de entorno
            output_file: Archivo de salida
        
        Returns:
            Comando listo para ejecutar
        """
        # Top ports comunes
        if top_count == 100:
            ports = '21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5900,8080'
        elif top_count == 1000:
            ports = '1-1000'
        else:
            ports = f'1-{top_count}'
        
        return cls.build_scan(target, ports, environment, output_file)



