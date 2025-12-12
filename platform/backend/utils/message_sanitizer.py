"""
Message Sanitizer
=================

Sanitiza mensajes de log para remover información sensible.
"""

import re
from typing import Optional, Dict, Any


class MessageSanitizer:
    """Sanitizador de mensajes para remover credenciales y tokens."""
    
    # Patrones a buscar y reemplazar
    SENSITIVE_PATTERNS = [
        # Passwords
        (r'password\s*=\s*["\']?([^"\'\s]+)["\']?', 'password=[REDACTED]'),
        (r'pwd\s*=\s*["\']?([^"\'\s]+)["\']?', 'pwd=[REDACTED]'),
        (r'pass\s*=\s*["\']?([^"\'\s]+)["\']?', 'pass=[REDACTED]'),
        (r'--password\s+["\']?([^"\'\s]+)["\']?', '--password [REDACTED]'),
        (r'-p\s+["\']?([^"\'\s]+)["\']?', '-p [REDACTED]'),
        (r'-P\s+["\']?([^"\'\s]+)["\']?', '-P [REDACTED]'),
        
        # Tokens y API keys
        (r'token\s*=\s*["\']?([^"\'\s]+)["\']?', 'token=[REDACTED]'),
        (r'api_key\s*=\s*["\']?([^"\'\s]+)["\']?', 'api_key=[REDACTED]'),
        (r'api-key\s*=\s*["\']?([^"\'\s]+)["\']?', 'api-key=[REDACTED]'),
        (r'secret\s*=\s*["\']?([^"\'\s]+)["\']?', 'secret=[REDACTED]'),
        (r'apikey\s*=\s*["\']?([^"\'\s]+)["\']?', 'apikey=[REDACTED]'),
        
        # Authorization headers
        (r'Authorization:\s*Bearer\s+([^\s]+)', 'Authorization: Bearer [REDACTED]'),
        (r'Authorization:\s*Basic\s+([^\s]+)', 'Authorization: Basic [REDACTED]'),
        (r'X-API-Key:\s*([^\s]+)', 'X-API-Key: [REDACTED]'),
        
        # URLs con credenciales
        (r'://([^:]+):([^@]+)@', '://[REDACTED]:[REDACTED]@'),
        
        # SSH keys y certificados (patrones comunes)
        (r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----.*?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----', 
         '[REDACTED: PRIVATE KEY]'),
        (r'ssh-rsa\s+[A-Za-z0-9+/=]+', '[REDACTED: SSH KEY]'),
        
        # JWT tokens (formato típico)
        (r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', '[REDACTED: JWT TOKEN]'),
    ]
    
    @classmethod
    def sanitize(cls, message: str) -> str:
        """
        Sanitiza un mensaje removiendo información sensible.
        
        Args:
            message: Mensaje original
            
        Returns:
            Mensaje sanitizado
        """
        if not message:
            return message
        
        sanitized = message
        
        # Aplicar cada patrón
        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            try:
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
            except re.error:
                # Si hay error en el regex, continuar con el siguiente
                continue
        
        return sanitized
    
    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza un diccionario recursivamente.
        
        Args:
            data: Diccionario con datos
            
        Returns:
            Diccionario sanitizado
        """
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            # Sanitizar keys sensibles
            if any(sensitive in key.lower() for sensitive in ['password', 'pwd', 'pass', 'token', 'secret', 'key', 'auth']):
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, str):
                sanitized[key] = cls.sanitize(value)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [cls.sanitize_dict(item) if isinstance(item, dict) 
                                 else cls.sanitize(item) if isinstance(item, str) 
                                 else item for item in value]
            else:
                sanitized[key] = value
        
        return sanitized

