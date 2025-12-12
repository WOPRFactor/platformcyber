"""
Domain Validator
================

Validación de nombres de dominio.
"""

import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DomainValidator:
    """Validador de nombres de dominio."""
    
    # Pattern para dominios válidos
    DOMAIN_PATTERN = re.compile(
        r'^'
        r'(?:[a-zA-Z0-9]'  # Primer caracter
        r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)'  # Subdominios
        r'+[a-zA-Z]{2,}'  # TLD (mínimo 2 caracteres)
        r'$'
    )
    
    # Pattern para subdominio wildcard
    WILDCARD_PATTERN = re.compile(
        r'^\*\.'
        r'(?:[a-zA-Z0-9]'
        r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)'
        r'+[a-zA-Z]{2,}'
        r'$'
    )
    
    @classmethod
    def is_valid_domain(cls, domain: str) -> bool:
        """
        Valida si es un dominio válido.
        
        Args:
            domain: Dominio a validar
        
        Returns:
            True si es válido
        
        Examples:
            >>> DomainValidator.is_valid_domain('example.com')
            True
            >>> DomainValidator.is_valid_domain('sub.example.com')
            True
            >>> DomainValidator.is_valid_domain('invalid..com')
            False
            >>> DomainValidator.is_valid_domain('-example.com')
            False
        """
        if not domain or len(domain) > 253:
            return False
        
        # Convertir a minúsculas
        domain = domain.lower().strip()
        
        # Validar con regex
        return bool(cls.DOMAIN_PATTERN.match(domain))
    
    @classmethod
    def is_valid_wildcard_domain(cls, domain: str) -> bool:
        """
        Valida si es un dominio wildcard válido (*.example.com).
        
        Args:
            domain: Dominio wildcard
        
        Returns:
            True si es válido
        """
        if not domain:
            return False
        
        domain = domain.lower().strip()
        return bool(cls.WILDCARD_PATTERN.match(domain))
    
    @classmethod
    def extract_root_domain(cls, domain: str) -> Optional[str]:
        """
        Extrae el dominio raíz de un subdominio.
        
        Args:
            domain: Dominio completo
        
        Returns:
            Dominio raíz o None
        
        Examples:
            >>> DomainValidator.extract_root_domain('sub.example.com')
            'example.com'
            >>> DomainValidator.extract_root_domain('api.v2.service.example.com')
            'example.com'
        """
        if not cls.is_valid_domain(domain):
            return None
        
        parts = domain.split('.')
        
        # Si tiene 2 partes, ya es el root
        if len(parts) == 2:
            return domain
        
        # Tomar las últimas 2 partes
        return '.'.join(parts[-2:])
    
    @classmethod
    def validate_url(cls, url: str) -> bool:
        """
        Valida si es una URL válida.
        
        Args:
            url: URL completa
        
        Returns:
            True si es válida
        
        Examples:
            >>> DomainValidator.validate_url('https://example.com')
            True
            >>> DomainValidator.validate_url('http://sub.example.com:8080/path')
            True
        """
        url_pattern = re.compile(
            r'^https?://'  # Protocolo
            r'(?:[a-zA-Z0-9-]+\.)*[a-zA-Z0-9-]+\.[a-zA-Z]{2,}'  # Dominio
            r'(?::\d{1,5})?'  # Puerto opcional
            r'(?:/[^\s]*)?$'  # Path opcional
        )
        
        return bool(url_pattern.match(url))



