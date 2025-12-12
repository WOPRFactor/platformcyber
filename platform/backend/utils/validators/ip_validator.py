"""
IP Validator
============

Validación de direcciones IP y rangos de red.
"""

import re
import ipaddress
from typing import Union
import logging

logger = logging.getLogger(__name__)


class IPValidator:
    """Validador de direcciones IP y rangos de red."""
    
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """
        Valida si es una dirección IP válida (IPv4 o IPv6).
        
        Args:
            ip: Dirección IP a validar
        
        Returns:
            True si es válida
        
        Examples:
            >>> IPValidator.is_valid_ip('192.168.1.1')
            True
            >>> IPValidator.is_valid_ip('256.1.1.1')
            False
            >>> IPValidator.is_valid_ip('2001:db8::1')
            True
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_ipv4(ip: str) -> bool:
        """Valida si es una dirección IPv4 válida."""
        try:
            ipaddress.IPv4Address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_ipv6(ip: str) -> bool:
        """Valida si es una dirección IPv6 válida."""
        try:
            ipaddress.IPv6Address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_cidr(cidr: str) -> bool:
        """
        Valida si es un rango CIDR válido.
        
        Args:
            cidr: Rango en notación CIDR (ej: 192.168.1.0/24)
        
        Returns:
            True si es válido
        
        Examples:
            >>> IPValidator.is_valid_cidr('192.168.1.0/24')
            True
            >>> IPValidator.is_valid_cidr('10.0.0.0/8')
            True
            >>> IPValidator.is_valid_cidr('192.168.1.1/33')
            False
        """
        try:
            ipaddress.ip_network(cidr, strict=False)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_private_ip(ip: str) -> bool:
        """
        Verifica si la IP es privada (RFC1918).
        
        Returns:
            True si es IP privada (10.x.x.x, 172.16-31.x.x, 192.168.x.x)
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except ValueError:
            return False
    
    @staticmethod
    def is_public_ip(ip: str) -> bool:
        """Verifica si la IP es pública (no privada, no loopback, no reserved)."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return not (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved)
        except ValueError:
            return False
    
    @staticmethod
    def validate_port(port: Union[int, str]) -> bool:
        """
        Valida si el puerto está en rango válido (1-65535).
        
        Args:
            port: Número de puerto
        
        Returns:
            True si es válido
        """
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_port_range(port_range: str) -> bool:
        """
        Valida un rango de puertos (ej: '80-443', '1-65535').
        
        Args:
            port_range: Rango en formato 'inicio-fin'
        
        Returns:
            True si es válido
        """
        try:
            if '-' in port_range:
                start, end = port_range.split('-', 1)
                start_port = int(start)
                end_port = int(end)
                
                return (
                    1 <= start_port <= 65535 and
                    1 <= end_port <= 65535 and
                    start_port <= end_port
                )
            else:
                # Puerto único
                return IPValidator.validate_port(port_range)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate(ip: str) -> None:
        """
        Valida que el target sea una IP o rango CIDR válido.
        Lanza ValueError si no es válido.
        
        Args:
            ip: IP o rango CIDR a validar
        
        Raises:
            ValueError: Si la IP o rango CIDR no es válido
        
        Examples:
            >>> IPValidator.validate('192.168.1.1')  # OK
            >>> IPValidator.validate('192.168.1.0/24')  # OK
            >>> IPValidator.validate('invalid')  # ValueError
        """
        # Intentar validar como IP
        if IPValidator.is_valid_ip(ip):
            return
        
        # Intentar validar como rango CIDR
        if IPValidator.is_valid_cidr(ip):
            return
        
        # Si no es válido, lanzar excepción
        raise ValueError(f"IP o rango CIDR inválido: {ip}")



