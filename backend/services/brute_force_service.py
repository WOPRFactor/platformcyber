"""
Brute Force Service
===================

Servicio para ataques de fuerza bruta con Hydra.
"""

import subprocess
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from utils.validators import CommandSanitizer, DomainValidator
import logging

logger = logging.getLogger(__name__)


class BruteForceService:
    """Servicio para ataques de fuerza bruta."""
    
    def __init__(self):
        """Inicializa el servicio de brute force."""
        self.output_dir = os.path.join(os.getcwd(), 'scan_results', 'brute_force')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def hydra_attack(
        self,
        target: str,
        service: str,
        username: Optional[str] = None,
        username_list: Optional[str] = None,
        password: Optional[str] = None,
        password_list: Optional[str] = None,
        port: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta ataque de fuerza bruta con Hydra.
        
        Args:
            target: Host objetivo
            service: Servicio (ssh, ftp, http-get, etc.)
            username: Usuario único
            username_list: Archivo con lista de usuarios
            password: Contraseña única
            password_list: Archivo con lista de contraseñas
            port: Puerto (opcional)
            options: Opciones adicionales
        
        Returns:
            Resultado del ataque
        
        Raises:
            ValueError: Si la configuración es inválida
        """
        logger.info(f"Iniciando ataque Hydra contra {target}:{service}")
        
        # Validar target
        if not DomainValidator.is_valid_domain(target):
            raise ValueError(f"Target inválido: {target}")
        
        # Validar que se proporcione username o username_list
        if not username and not username_list:
            raise ValueError("Debe proporcionar username o username_list")
        
        # Validar que se proporcione password o password_list
        if not password and not password_list:
            raise ValueError("Debe proporcionar password o password_list")
        
        # Validar servicio
        valid_services = [
            'ssh', 'ftp', 'telnet', 'http-get', 'http-post', 'http-post-form',
            'https-get', 'https-post', 'https-post-form', 'mysql', 'mssql',
            'postgres', 'rdp', 'smb', 'vnc', 'pop3', 'imap', 'smtp'
        ]
        if service not in valid_services:
            raise ValueError(f"Servicio no soportado: {service}")
        
        # Construir comando
        command = ['hydra']
        
        # Target y servicio
        if port:
            command.extend(['-s', str(port)])
        
        # Usuario
        if username:
            command.extend(['-l', username])
        elif username_list:
            if not os.path.exists(username_list):
                raise ValueError(f"Archivo de usuarios no encontrado: {username_list}")
            command.extend(['-L', username_list])
        
        # Contraseña
        if password:
            command.extend(['-p', password])
        elif password_list:
            if not os.path.exists(password_list):
                raise ValueError(f"Archivo de contraseñas no encontrado: {password_list}")
            command.extend(['-P', password_list])
        
        # Opciones adicionales
        options = options or {}
        
        # Threads
        threads = options.get('threads', 4)
        command.extend(['-t', str(threads)])
        
        # Timeout
        timeout = options.get('timeout', 30)
        command.extend(['-w', str(timeout)])
        
        # Verbose
        if options.get('verbose', False):
            command.append('-V')
        
        # Show attempts
        if options.get('show_attempts', False):
            command.append('-v')
        
        # Exit on first valid
        if options.get('exit_on_first', False):
            command.append('-f')
        
        # Continue on errors
        if options.get('continue_on_error', True):
            command.append('-e')
            command.append('nsr')  # n=null, s=same as login, r=reverse
        
        # Output file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(
            self.output_dir,
            f'hydra_{target.replace(".", "_")}_{service}_{timestamp}.txt'
        )
        command.extend(['-o', output_file])
        
        # HTTP specific options
        if service.startswith('http'):
            if 'path' in options:
                command.extend(['-m', options['path']])
        
        # Target y servicio al final
        command.append(target)
        command.append(service)
        
        # Sanitizar comando
        try:
            sanitized_command = CommandSanitizer.sanitize_command(
                command[0],
                command[1:]
            )
        except ValueError as e:
            logger.error(f"Error sanitizando comando Hydra: {e}")
            raise
        
        logger.info(f"Comando Hydra: {' '.join(sanitized_command)}")
        
        # Ejecutar
        try:
            result = subprocess.run(
                sanitized_command,
                capture_output=True,
                text=True,
                timeout=options.get('max_timeout', 3600)  # 1 hora max
            )
            
            # Parsear resultados
            output = result.stdout + result.stderr
            
            # Extraer credenciales válidas
            valid_creds = self._parse_hydra_output(output)
            
            return {
                'status': 'completed' if result.returncode == 0 else 'failed',
                'target': target,
                'service': service,
                'port': port,
                'valid_credentials': valid_creds,
                'attempts': self._count_attempts(output),
                'output_file': output_file,
                'output': output[:5000],  # Primeros 5000 caracteres
                'timestamp': timestamp
            }
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout en Hydra contra {target}")
            return {
                'status': 'timeout',
                'target': target,
                'service': service,
                'error': 'Timeout alcanzado',
                'timestamp': timestamp
            }
        except Exception as e:
            logger.error(f"Error ejecutando Hydra: {e}")
            return {
                'status': 'error',
                'target': target,
                'service': service,
                'error': str(e),
                'timestamp': timestamp
            }
    
    def _parse_hydra_output(self, output: str) -> List[Dict[str, str]]:
        """
        Parsea la salida de Hydra para extraer credenciales válidas.
        
        Args:
            output: Salida de Hydra
        
        Returns:
            Lista de credenciales válidas
        """
        valid_creds = []
        
        # Formato: [PORT][SERVICE] host: HOST   login: USER   password: PASS
        lines = output.split('\n')
        for line in lines:
            if 'login:' in line and 'password:' in line:
                try:
                    # Extraer información
                    parts = line.split()
                    
                    login_idx = parts.index('login:')
                    password_idx = parts.index('password:')
                    
                    username = parts[login_idx + 1]
                    password = parts[password_idx + 1]
                    
                    # Extraer host si está presente
                    host = None
                    if 'host:' in line:
                        host_idx = parts.index('host:')
                        host = parts[host_idx + 1]
                    
                    valid_creds.append({
                        'username': username,
                        'password': password,
                        'host': host
                    })
                except (ValueError, IndexError):
                    continue
        
        return valid_creds
    
    def _count_attempts(self, output: str) -> int:
        """
        Cuenta el número de intentos en la salida de Hydra.
        
        Args:
            output: Salida de Hydra
        
        Returns:
            Número de intentos
        """
        # Hydra muestra cada intento en modo verbose
        # Contar líneas que contienen "attempt"
        count = 0
        for line in output.split('\n'):
            if '[ATTEMPT]' in line or 'attempt' in line.lower():
                count += 1
        
        return count if count > 0 else None
    
    def get_common_passwords(self, count: int = 100) -> List[str]:
        """
        Retorna lista de contraseñas comunes.
        
        Args:
            count: Número de contraseñas
        
        Returns:
            Lista de contraseñas
        """
        # Top 100 contraseñas comunes (para testing)
        common_passwords = [
            'password', '123456', '12345678', 'qwerty', 'abc123',
            'monkey', '1234567', 'letmein', 'trustno1', 'dragon',
            'baseball', '111111', 'iloveyou', 'master', 'sunshine',
            'ashley', 'bailey', 'passw0rd', 'shadow', '123123',
            '654321', 'superman', 'qazwsx', 'michael', 'football',
            'admin', 'root', 'administrator', 'password1', 'password123',
            'welcome', 'welcome1', 'P@ssw0rd', 'P@ssword', 'Password1',
            'Guest', 'guest', 'user', 'test', 'demo',
            'changeme', 'default', 'temp', 'temporal', 'secret',
            'passpass', '1qaz2wsx', 'zxcvbnm', 'qwertyuiop', 'asdfghjkl',
            'password!', 'Password!', 'Admin123', 'Root123', 'User123',
            '000000', '123321', '112233', '121212', '123abc',
            'pass', 'pass123', 'pass1234', 'admin123', 'root123',
            'test123', 'demo123', 'user123', 'temp123', 'guest123',
            '12345', '1234', '123', '12', '1',
            'a', 'aa', 'aaa', 'aaaa', 'aaaaa',
            'password12', 'password1234', 'qwerty123', 'abc12345', 'letmein123',
            'trustno123', 'dragon123', 'baseball123', '111111a', 'iloveyou123',
            'master123', 'sunshine123', 'ashley123', 'bailey123', 'shadow123',
            '123123a', '654321a', 'superman123', 'michael123', 'football123'
        ]
        
        return common_passwords[:count]
    
    def get_common_usernames(self, count: int = 50) -> List[str]:
        """
        Retorna lista de usuarios comunes.
        
        Args:
            count: Número de usuarios
        
        Returns:
            Lista de usuarios
        """
        # Usuarios comunes
        common_usernames = [
            'admin', 'administrator', 'root', 'user', 'test',
            'guest', 'demo', 'temp', 'info', 'support',
            'service', 'operator', 'supervisor', 'manager', 'webmaster',
            'postmaster', 'hostmaster', 'webadmin', 'sysadmin', 'netadmin',
            'ftpuser', 'www', 'www-data', 'apache', 'nginx',
            'mysql', 'postgres', 'oracle', 'sqlserver', 'mongodb',
            'backup', 'backupuser', 'administrator1', 'admin1', 'root1',
            'superuser', 'super', 'sa', 'dba', 'dbadmin',
            'student', 'teacher', 'staff', 'employee', 'hr',
            'accounting', 'finance', 'sales', 'marketing', 'it'
        ]
        
        return common_usernames[:count]
    
    def create_wordlist(
        self,
        output_path: str,
        words: List[str]
    ) -> str:
        """
        Crea un archivo wordlist.
        
        Args:
            output_path: Ruta del archivo
            words: Lista de palabras
        
        Returns:
            Ruta del archivo creado
        """
        try:
            with open(output_path, 'w') as f:
                f.write('\n'.join(words))
            
            logger.info(f"Wordlist creado: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creando wordlist: {e}")
            raise
    
    def get_hydra_modules(self) -> List[str]:
        """
        Retorna lista de módulos soportados por Hydra.
        
        Returns:
            Lista de módulos
        """
        try:
            result = subprocess.run(
                ['hydra', '-U'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Parsear módulos de la salida
            modules = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('Hydra') and not line.startswith('Help'):
                    # Extraer nombre del módulo
                    if ':' in line:
                        module = line.split(':')[0].strip()
                        if module:
                            modules.append(module)
            
            return sorted(set(modules))
            
        except Exception as e:
            logger.error(f"Error obteniendo módulos Hydra: {e}")
            # Retornar módulos comunes por defecto
            return [
                'ssh', 'ftp', 'telnet', 'http-get', 'http-post',
                'https-get', 'https-post', 'mysql', 'mssql',
                'postgres', 'rdp', 'smb', 'vnc'
            ]
    
    def check_hydra_installed(self) -> bool:
        """
        Verifica si Hydra está instalado.
        
        Returns:
            True si está instalado
        """
        try:
            result = subprocess.run(
                ['which', 'hydra'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False



