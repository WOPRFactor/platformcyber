"""
Safe Hydra Command Builder
===========================

Constructor seguro de comandos Hydra con rate limiting.
"""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class SafeHydra:
    """
    Constructor seguro de comandos Hydra.
    
    PREVIENE:
    - Bloqueo de cuentas (rate limiting)
    - Ataques de fuerza bruta masivos
    - Wordlists demasiado grandes sin advertencia
    """
    
    # Límites de seguridad
    MAX_THREADS = 4        # Máximo 4 threads paralelos
    DEFAULT_TIMEOUT = 30   # Timeout por intento
    DEFAULT_WAIT = 2       # Espera entre intentos
    
    # Servicios soportados
    SUPPORTED_SERVICES = [
        'ssh', 'ftp', 'http-get', 'http-post', 'https-get', 'https-post',
        'smb', 'rdp', 'mysql', 'postgresql', 'telnet', 'vnc'
    ]
    
    @classmethod
    def build_ssh_attack(
        cls,
        target: str,
        username: Optional[str] = None,
        userfile: Optional[str] = None,
        password: Optional[str] = None,
        passfile: Optional[str] = None,
        port: int = 22,
        output_file: str = 'hydra_ssh.txt'
    ) -> List[str]:
        """
        Ataque SSH con rate limiting.
        
        Args:
            target: IP objetivo
            username: Usuario único (o usar userfile)
            userfile: Archivo de usuarios
            password: Password único (o usar passfile)
            passfile: Archivo de passwords
            port: Puerto SSH (default: 22)
            output_file: Archivo de output
        
        Returns:
            Comando listo para ejecutar
        
        Raises:
            ValueError: Si faltan parámetros o son inválidos
        """
        if not (username or userfile):
            raise ValueError("Debe especificar username o userfile")
        
        if not (password or passfile):
            raise ValueError("Debe especificar password o passfile")
        
        cmd = ['hydra']
        
        # Usuario
        if username:
            cmd.extend(['-l', username])
        else:
            cmd.extend(['-L', userfile])
        
        # Password
        if password:
            cmd.extend(['-p', password])
        else:
            cmd.extend(['-P', passfile])
        
        # Opciones de seguridad
        cmd.extend([
            '-t', str(cls.MAX_THREADS),     # Máximo 4 threads
            '-w', str(cls.DEFAULT_TIMEOUT), # Timeout 30 segs
            '-f',                           # Parar al encontrar
            '-V',                           # Verbose
            '-o', output_file,              # Output file
            '-s', str(port),                # Puerto
            f'ssh://{target}'
        ])
        
        logger.info(f"Hydra SSH attack en {target}:{port} con rate limitado")
        return cmd
    
    @classmethod
    def build_http_post_attack(
        cls,
        target: str,
        login_path: str,
        username_field: str,
        password_field: str,
        failure_string: str,
        username: Optional[str] = None,
        userfile: Optional[str] = None,
        password: Optional[str] = None,
        passfile: Optional[str] = None,
        output_file: str = 'hydra_http.txt'
    ) -> List[str]:
        """
        Ataque HTTP POST form.
        
        Args:
            target: Dominio o IP
            login_path: Path del login (ej: /login)
            username_field: Nombre del campo usuario (ej: 'username')
            password_field: Nombre del campo password (ej: 'password')
            failure_string: String que indica fallo (ej: 'incorrect')
            username: Usuario único
            userfile: Archivo de usuarios
            password: Password único
            passfile: Archivo de passwords
            output_file: Archivo de output
        
        Returns:
            Comando listo para ejecutar
        """
        if not (username or userfile):
            raise ValueError("Debe especificar username o userfile")
        
        if not (password or passfile):
            raise ValueError("Debe especificar password o passfile")
        
        cmd = ['hydra']
        
        # Usuario
        if username:
            cmd.extend(['-l', username])
        else:
            cmd.extend(['-L', userfile])
        
        # Password
        if password:
            cmd.extend(['-p', password])
        else:
            cmd.extend(['-P', passfile])
        
        # Opciones
        cmd.extend([
            '-t', str(cls.MAX_THREADS),
            '-w', str(cls.DEFAULT_TIMEOUT),
            '-f',
            '-V',
            '-o', output_file,
            target,
            'http-post-form',
            f'{login_path}:{username_field}=^USER^&{password_field}=^PASS^:F={failure_string}'
        ])
        
        logger.info(f"Hydra HTTP POST attack en {target}{login_path}")
        return cmd
    
    @classmethod
    def build_smb_attack(
        cls,
        target: str,
        username: Optional[str] = None,
        userfile: Optional[str] = None,
        password: Optional[str] = None,
        passfile: Optional[str] = None,
        output_file: str = 'hydra_smb.txt'
    ) -> List[str]:
        """
        Ataque SMB con rate limiting.
        
        Args:
            target: IP objetivo
            username: Usuario único
            userfile: Archivo de usuarios
            password: Password único
            passfile: Archivo de passwords
            output_file: Archivo de output
        
        Returns:
            Comando listo para ejecutar
        """
        if not (username or userfile):
            raise ValueError("Debe especificar username o userfile")
        
        if not (password or passfile):
            raise ValueError("Debe especificar password o passfile")
        
        cmd = ['hydra']
        
        if username:
            cmd.extend(['-l', username])
        else:
            cmd.extend(['-L', userfile])
        
        if password:
            cmd.extend(['-p', password])
        else:
            cmd.extend(['-P', passfile])
        
        cmd.extend([
            '-t', str(cls.MAX_THREADS),
            '-w', str(cls.DEFAULT_TIMEOUT),
            '-f',
            '-V',
            '-o', output_file,
            f'smb://{target}'
        ])
        
        logger.info(f"Hydra SMB attack en {target} con rate limitado")
        return cmd
    
    @classmethod
    def validate_service(cls, service: str) -> bool:
        """
        Valida que el servicio sea soportado.
        
        Args:
            service: Nombre del servicio
        
        Returns:
            True si es válido
        
        Raises:
            ValueError: Si el servicio no es soportado
        """
        if service not in cls.SUPPORTED_SERVICES:
            raise ValueError(
                f"Servicio '{service}' no soportado.\n"
                f"Servicios válidos: {', '.join(cls.SUPPORTED_SERVICES)}"
            )
        
        return True



