"""
Evil-WinRM Service
==================

Servicio para Evil-WinRM (Windows Remote Management).
"""

import subprocess
import os
from typing import Dict, Optional, Any
from datetime import datetime

from utils.validators import CommandSanitizer, DomainValidator
import logging

logger = logging.getLogger(__name__)


class EvilWinRMService:
    """Servicio para Evil-WinRM."""
    
    def __init__(self):
        """Inicializa el servicio de Evil-WinRM."""
        self.output_dir = os.path.join(os.getcwd(), 'scan_results', 'evil-winrm')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def execute(
        self,
        target: str,
        username: str,
        password: Optional[str] = None,
        hash: Optional[str] = None,
        command: Optional[str] = None,
        script: Optional[str] = None,
        port: int = 5985,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta Evil-WinRM para PowerShell remoto.
        
        Args:
            target: Host objetivo
            username: Usuario
            password: Contraseña
            hash: Hash NTLM
            command: Comando a ejecutar
            script: Script de PowerShell a ejecutar
            port: Puerto WinRM (default: 5985)
            options: Opciones adicionales
        
        Returns:
            Resultado de la ejecución
        """
        logger.info(f"Ejecutando Evil-WinRM contra {target}")
        
        # Validar target
        if not DomainValidator.is_valid_domain(target):
            raise ValueError(f"Target inválido: {target}")
        
        # Validar credenciales
        if not password and not hash:
            raise ValueError("Debe proporcionar password o hash")
        
        # Construir comando
        cmd = ['evil-winrm', '-i', target, '-u', username]
        
        # Credenciales
        if password:
            cmd.extend(['-p', password])
        elif hash:
            cmd.extend(['-H', hash])
        
        # Puerto
        if port != 5985:
            cmd.extend(['-P', str(port)])
        
        # SSL
        options = options or {}
        if options.get('ssl', False):
            cmd.append('-S')
        
        # Comando
        if command:
            cmd.extend(['-c', command])
        
        # Script
        if script:
            if not os.path.exists(script):
                raise ValueError(f"Script no encontrado: {script}")
            cmd.extend(['-s', script])
        
        # Output
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(
            self.output_dir,
            f'evilwinrm_{target.replace(".", "_")}_{timestamp}.txt'
        )
        
        # Sanitizar
        try:
            sanitized = CommandSanitizer.sanitize_command(cmd[0], cmd[1:])
        except ValueError as e:
            logger.error(f"Error sanitizando comando Evil-WinRM: {e}")
            raise
        
        logger.info(f"Comando Evil-WinRM: {' '.join(sanitized)}")
        
        # Ejecutar
        try:
            result = subprocess.run(
                sanitized,
                capture_output=True,
                text=True,
                timeout=options.get('timeout', 300)
            )
            
            output = result.stdout + result.stderr
            
            # Guardar output
            with open(output_file, 'w') as f:
                f.write(output)
            
            return {
                'status': 'completed' if result.returncode == 0 else 'failed',
                'target': target,
                'command': command,
                'output': output[:5000],
                'output_file': output_file,
                'timestamp': timestamp
            }
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout en Evil-WinRM")
            return {
                'status': 'timeout',
                'target': target,
                'error': 'Timeout alcanzado',
                'timestamp': timestamp
            }
        except Exception as e:
            logger.error(f"Error ejecutando Evil-WinRM: {e}")
            return {
                'status': 'error',
                'target': target,
                'error': str(e),
                'timestamp': timestamp
            }
    
    def check_installed(self) -> bool:
        """
        Verifica si Evil-WinRM está instalado.
        
        Returns:
            True si está instalado
        """
        try:
            result = subprocess.run(
                ['which', 'evil-winrm'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False



