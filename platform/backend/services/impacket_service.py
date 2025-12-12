"""
Impacket Service
================

Servicio para herramientas de Impacket Suite.
"""

import subprocess
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from utils.validators import CommandSanitizer, DomainValidator
import logging

logger = logging.getLogger(__name__)


class ImpacketService:
    """Servicio para Impacket Suite."""
    
    def __init__(self):
        """Inicializa el servicio de Impacket."""
        self.output_dir = os.path.join(os.getcwd(), 'scan_results', 'impacket')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def psexec(
        self,
        target: str,
        username: str,
        password: Optional[str] = None,
        hash: Optional[str] = None,
        domain: Optional[str] = None,
        command: str = 'whoami',
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta psexec.py para ejecución remota.
        
        Args:
            target: Host objetivo
            username: Usuario
            password: Contraseña
            hash: Hash NTLM (LM:NT)
            domain: Dominio
            command: Comando a ejecutar
            options: Opciones adicionales
        
        Returns:
            Resultado de la ejecución
        """
        logger.info(f"Ejecutando psexec contra {target}")
        
        # Validar target
        if not DomainValidator.is_valid_domain(target):
            raise ValueError(f"Target inválido: {target}")
        
        # Validar que se proporcione password o hash
        if not password and not hash:
            raise ValueError("Debe proporcionar password o hash")
        
        # Construir comando
        cmd = ['psexec.py']
        
        # Credenciales
        if domain:
            credential = f"{domain}/{username}"
        else:
            credential = username
        
        if password:
            credential += f":{password}"
        elif hash:
            credential += f"@{target}"
            cmd.extend(['-hashes', hash])
        
        if not hash:
            credential += f"@{target}"
        
        cmd.append(credential)
        
        # Comando a ejecutar
        cmd.append(command)
        
        # Opciones
        options = options or {}
        
        # Archivo de salida
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(
            self.output_dir,
            f'psexec_{target.replace(".", "_")}_{timestamp}.txt'
        )
        
        # Sanitizar
        try:
            sanitized = CommandSanitizer.sanitize_command(cmd[0], cmd[1:])
        except ValueError as e:
            logger.error(f"Error sanitizando comando psexec: {e}")
            raise
        
        logger.info(f"Comando psexec: {' '.join(sanitized)}")
        
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
            logger.warning(f"Timeout en psexec")
            return {
                'status': 'timeout',
                'target': target,
                'error': 'Timeout alcanzado',
                'timestamp': timestamp
            }
        except Exception as e:
            logger.error(f"Error ejecutando psexec: {e}")
            return {
                'status': 'error',
                'target': target,
                'error': str(e),
                'timestamp': timestamp
            }
    
    def secretsdump(
        self,
        target: str,
        username: str,
        password: Optional[str] = None,
        hash: Optional[str] = None,
        domain: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta secretsdump.py para extraer secretos.
        
        Args:
            target: Host objetivo
            username: Usuario
            password: Contraseña
            hash: Hash NTLM
            domain: Dominio
            options: Opciones adicionales
        
        Returns:
            Resultado de la extracción
        """
        logger.info(f"Ejecutando secretsdump contra {target}")
        
        # Validar target
        if not DomainValidator.is_valid_domain(target):
            raise ValueError(f"Target inválido: {target}")
        
        # Construir comando
        cmd = ['secretsdump.py']
        
        # Credenciales
        if domain:
            credential = f"{domain}/{username}"
        else:
            credential = username
        
        if password:
            credential += f":{password}@{target}"
        elif hash:
            credential += f"@{target}"
            cmd.extend(['-hashes', hash])
        else:
            raise ValueError("Debe proporcionar password o hash")
        
        cmd.append(credential)
        
        # Opciones
        options = options or {}
        
        # Just DC
        if options.get('just_dc', False):
            cmd.append('-just-dc')
        
        # Just DC NTLM
        if options.get('just_dc_ntlm', False):
            cmd.append('-just-dc-ntlm')
        
        # Just DC User
        if 'just_dc_user' in options:
            cmd.extend(['-just-dc-user', options['just_dc_user']])
        
        # Output files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_base = os.path.join(
            self.output_dir,
            f'secretsdump_{target.replace(".", "_")}_{timestamp}'
        )
        cmd.extend(['-outputfile', output_base])
        
        # Sanitizar
        try:
            sanitized = CommandSanitizer.sanitize_command(cmd[0], cmd[1:])
        except ValueError as e:
            logger.error(f"Error sanitizando comando secretsdump: {e}")
            raise
        
        logger.info(f"Comando secretsdump: {' '.join(sanitized)}")
        
        # Ejecutar
        try:
            result = subprocess.run(
                sanitized,
                capture_output=True,
                text=True,
                timeout=options.get('timeout', 600)
            )
            
            output = result.stdout + result.stderr
            
            # Parsear hashes
            hashes = self._parse_secretsdump_output(output)
            
            return {
                'status': 'completed' if result.returncode == 0 else 'failed',
                'target': target,
                'hashes_found': len(hashes),
                'hashes': hashes[:100],  # Primeros 100
                'output': output[:5000],
                'output_files': {
                    'sam': f"{output_base}.sam",
                    'secrets': f"{output_base}.secrets",
                    'cached': f"{output_base}.cached"
                },
                'timestamp': timestamp
            }
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout en secretsdump")
            return {
                'status': 'timeout',
                'target': target,
                'error': 'Timeout alcanzado',
                'timestamp': timestamp
            }
        except Exception as e:
            logger.error(f"Error ejecutando secretsdump: {e}")
            return {
                'status': 'error',
                'target': target,
                'error': str(e),
                'timestamp': timestamp
            }
    
    def get_user_spns(
        self,
        target: str,
        username: str,
        password: Optional[str] = None,
        hash: Optional[str] = None,
        domain: Optional[str] = None,
        dc_ip: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta GetUserSPNs.py para Kerberoasting.
        
        Args:
            target: Dominio objetivo
            username: Usuario
            password: Contraseña
            hash: Hash NTLM
            domain: Dominio
            dc_ip: IP del Domain Controller
            options: Opciones adicionales
        
        Returns:
            Resultado de la extracción de SPNs
        """
        logger.info(f"Ejecutando GetUserSPNs contra {target}")
        
        # Construir comando
        cmd = ['GetUserSPNs.py']
        
        # Credenciales
        if domain:
            credential = f"{domain}/{username}"
        else:
            credential = f"{target}/{username}"
        
        if password:
            credential += f":{password}"
        elif hash:
            cmd.extend(['-hashes', hash])
        else:
            raise ValueError("Debe proporcionar password o hash")
        
        cmd.append(credential)
        
        # DC IP
        if dc_ip:
            cmd.extend(['-dc-ip', dc_ip])
        
        # Opciones
        options = options or {}
        
        # Request TGS
        if options.get('request', True):
            cmd.append('-request')
        
        # Output file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(
            self.output_dir,
            f'user_spns_{target.replace(".", "_")}_{timestamp}.txt'
        )
        cmd.extend(['-outputfile', output_file])
        
        # Sanitizar
        try:
            sanitized = CommandSanitizer.sanitize_command(cmd[0], cmd[1:])
        except ValueError as e:
            logger.error(f"Error sanitizando comando GetUserSPNs: {e}")
            raise
        
        logger.info(f"Comando GetUserSPNs: {' '.join(sanitized)}")
        
        # Ejecutar
        try:
            result = subprocess.run(
                sanitized,
                capture_output=True,
                text=True,
                timeout=options.get('timeout', 300)
            )
            
            output = result.stdout + result.stderr
            
            # Parsear SPNs
            spns = self._parse_spns_output(output)
            
            return {
                'status': 'completed' if result.returncode == 0 else 'failed',
                'target': target,
                'spns_found': len(spns),
                'spns': spns,
                'output': output[:5000],
                'output_file': output_file,
                'timestamp': timestamp
            }
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout en GetUserSPNs")
            return {
                'status': 'timeout',
                'target': target,
                'error': 'Timeout alcanzado',
                'timestamp': timestamp
            }
        except Exception as e:
            logger.error(f"Error ejecutando GetUserSPNs: {e}")
            return {
                'status': 'error',
                'target': target,
                'error': str(e),
                'timestamp': timestamp
            }
    
    def get_np_users(
        self,
        target: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        domain: Optional[str] = None,
        dc_ip: Optional[str] = None,
        usersfile: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta GetNPUsers.py para ASREPRoasting.
        
        Args:
            target: Dominio objetivo
            username: Usuario (opcional para modo sin auth)
            password: Contraseña
            domain: Dominio
            dc_ip: IP del Domain Controller
            usersfile: Archivo con lista de usuarios
            options: Opciones adicionales
        
        Returns:
            Resultado de la extracción
        """
        logger.info(f"Ejecutando GetNPUsers contra {target}")
        
        # Construir comando
        cmd = ['GetNPUsers.py']
        
        # Modo: con credenciales o sin auth
        if username and password:
            credential = f"{domain or target}/{username}:{password}"
            cmd.append(credential)
        else:
            # Modo sin autenticación
            cmd.append(f"{domain or target}/")
            cmd.append('-no-pass')
        
        # DC IP
        if dc_ip:
            cmd.extend(['-dc-ip', dc_ip])
        
        # Users file
        if usersfile:
            if not os.path.exists(usersfile):
                raise ValueError(f"Archivo de usuarios no encontrado: {usersfile}")
            cmd.extend(['-usersfile', usersfile])
        
        # Opciones
        options = options or {}
        
        # Request TGT
        if options.get('request', True):
            cmd.append('-request')
        
        # Format
        format_type = options.get('format', 'hashcat')
        cmd.extend(['-format', format_type])
        
        # Output file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(
            self.output_dir,
            f'np_users_{target.replace(".", "_")}_{timestamp}.txt'
        )
        cmd.extend(['-outputfile', output_file])
        
        # Sanitizar
        try:
            sanitized = CommandSanitizer.sanitize_command(cmd[0], cmd[1:])
        except ValueError as e:
            logger.error(f"Error sanitizando comando GetNPUsers: {e}")
            raise
        
        logger.info(f"Comando GetNPUsers: {' '.join(sanitized)}")
        
        # Ejecutar
        try:
            result = subprocess.run(
                sanitized,
                capture_output=True,
                text=True,
                timeout=options.get('timeout', 300)
            )
            
            output = result.stdout + result.stderr
            
            # Parsear hashes
            hashes = self._parse_np_users_output(output)
            
            return {
                'status': 'completed' if result.returncode == 0 else 'failed',
                'target': target,
                'hashes_found': len(hashes),
                'hashes': hashes,
                'output': output[:5000],
                'output_file': output_file,
                'timestamp': timestamp
            }
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout en GetNPUsers")
            return {
                'status': 'timeout',
                'target': target,
                'error': 'Timeout alcanzado',
                'timestamp': timestamp
            }
        except Exception as e:
            logger.error(f"Error ejecutando GetNPUsers: {e}")
            return {
                'status': 'error',
                'target': target,
                'error': str(e),
                'timestamp': timestamp
            }
    
    def _parse_secretsdump_output(self, output: str) -> List[Dict[str, str]]:
        """Parsea salida de secretsdump para extraer hashes."""
        hashes = []
        
        lines = output.split('\n')
        for line in lines:
            # Formato: DOMAIN\user:RID:LM:NT:::
            if ':' in line and ':::' in line:
                parts = line.split(':')
                if len(parts) >= 4:
                    try:
                        user_part = parts[0]
                        rid = parts[1]
                        lm_hash = parts[2]
                        nt_hash = parts[3]
                        
                        hashes.append({
                            'user': user_part,
                            'rid': rid,
                            'lm_hash': lm_hash,
                            'nt_hash': nt_hash
                        })
                    except (IndexError, ValueError):
                        continue
        
        return hashes
    
    def _parse_spns_output(self, output: str) -> List[Dict[str, str]]:
        """Parsea salida de GetUserSPNs para extraer SPNs."""
        spns = []
        
        lines = output.split('\n')
        for line in lines:
            if 'ServicePrincipalName' in line or '@' in line:
                # Formato varía, intentar extraer lo relevante
                spns.append({'raw': line.strip()})
        
        return spns
    
    def _parse_np_users_output(self, output: str) -> List[str]:
        """Parsea salida de GetNPUsers para extraer hashes."""
        hashes = []
        
        lines = output.split('\n')
        for line in lines:
            # Formato hashcat: $krb5asrep$23$...
            if line.startswith('$krb5asrep$'):
                hashes.append(line.strip())
        
        return hashes
    
    def check_impacket_installed(self) -> Dict[str, bool]:
        """
        Verifica si las herramientas de Impacket están instaladas.
        
        Returns:
            Dict con estado de cada herramienta
        """
        tools = ['psexec.py', 'secretsdump.py', 'GetUserSPNs.py', 'GetNPUsers.py']
        status = {}
        
        for tool in tools:
            try:
                result = subprocess.run(
                    ['which', tool],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                status[tool] = result.returncode == 0
            except Exception:
                status[tool] = False
        
        return status



