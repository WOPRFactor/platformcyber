"""
SMB/CIFS Enumeration Service
=============================

Servicios para enumeración SMB/CIFS:
- enum4linux / enum4linux-ng
- smbmap
- smbclient
- Nmap SMB scripts
"""

import logging
import shutil
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from utils.commands import SafeNmap
from .base import BaseEnumerationService

logger = logging.getLogger(__name__)


class SMBEnumerationService(BaseEnumerationService):
    """Servicio para enumeración SMB/CIFS."""
    
    def start_enum4linux(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        use_ng: bool = True,
        all: bool = False
    ) -> Dict[str, Any]:
        """
        Enumeración SMB con enum4linux o enum4linux-ng.
        
        Args:
            target: IP objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            use_ng: Usar enum4linux-ng (moderno) o enum4linux (clásico)
            all: Ejecutar todas las opciones (-A)
        
        Returns:
            Dict con información del escaneo
        """
        # Validar target (acepta IP, CIDR o dominio)
        CommandSanitizer.validate_target(target)
        
        # Detectar herramienta disponible
        if use_ng:
            if shutil.which('enum4linux-ng'):
                tool = 'enum4linux-ng'
            elif shutil.which('enum4linux'):
                tool = 'enum4linux'
                logger.warning("enum4linux-ng no encontrado, usando enum4linux")
            else:
                raise ValueError("Ni enum4linux-ng ni enum4linux están instalados. Instala uno de ellos.")
        else:
            if shutil.which('enum4linux'):
                tool = 'enum4linux'
            else:
                raise ValueError("enum4linux no está instalado. Instálalo con: apt install enum4linux")
        
        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool=tool,
            options={'all': all}
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = str(workspace_output_dir / f'{tool}_{scan.id}.txt')
            
            if tool == 'enum4linux-ng':
                command = ['enum4linux-ng', target]
                if all:
                    command.append('-A')
            else:  # enum4linux
                command = ['enum4linux', '-a', target] if all else ['enum4linux', target]
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting {tool} {scan.id}")
            
            self._start_scan_thread(scan.id, sanitized_cmd, output_file, tool)
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': tool,
                'target': target
            }
            
        except Exception as e:
            logger.error(f"Error starting {tool}: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def start_smbmap(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        hash: Optional[str] = None,
        recursive: bool = False,
        share: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mapeo de shares SMB con smbmap.
        
        Args:
            target: IP objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            username: Usuario (opcional)
            password: Password (opcional)
            hash: NTLM hash (opcional)
            recursive: Recursivo (-r)
            share: Share específico a mapear
        
        Returns:
            Dict con información del escaneo
        """
        CommandSanitizer.validate_target(target)
        
        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='smbmap',
            options={'recursive': recursive, 'share': share}
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = str(workspace_output_dir / f'smbmap_{scan.id}.txt')
            
            command = ['smbmap', '-H', target]
            
            if username:
                command.extend(['-u', username])
            if password:
                command.extend(['-p', password])
            if hash:
                command.extend(['--hash', hash])  # smbmap usa --hash para hash NTLM, no -H
            if recursive and share:
                command.extend(['-r', '-d', share])
            elif share:
                command.extend(['-d', share])
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting smbmap {scan.id}")
            
            self._start_scan_thread(scan.id, sanitized_cmd, output_file, 'smbmap')
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'smbmap',
                'target': target
            }
            
        except Exception as e:
            logger.error(f"Error starting smbmap: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def start_smbclient(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        share: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        command: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Conexión SMB con smbclient.
        
        Args:
            target: IP objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            share: Share a conectar (ej: "IPC$", "C$")
            username: Usuario (opcional)
            password: Password (opcional)
            command: Comando a ejecutar (opcional, ej: "ls", "dir")
        
        Returns:
            Dict con información del escaneo
        """
        CommandSanitizer.validate_target(target)
        
        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='smbclient',
            options={'share': share, 'command': command}
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = str(workspace_output_dir / f'smbclient_{scan.id}.txt')
            
            share_path = f'//{target}/{share}'
            command_list = ['smbclient', share_path, '-N']  # -N = no password
            
            # Agregar timeout de conexión para evitar esperas largas (30 segundos)
            # -t establece el timeout por operación
            command_list.extend(['-t', '30'])
            
            if username:
                command_list.extend(['-U', username])
            if password:
                # Si hay password, reemplazar -N y usar formato username%password
                command_list = [c for c in command_list if c != '-N']
                if username:
                    command_list.extend(['-U', f'{username}%{password}'])
                else:
                    command_list.extend(['-U', f'%{password}'])
            
            # IMPORTANTE: smbclient es interactivo, siempre necesita un comando -c
            # Si no se proporciona, usar 'exit' para que termine inmediatamente
            if command:
                command_list.extend(['-c', command])
            else:
                # Sin comando, solo listar y salir
                command_list.extend(['-c', 'ls; exit'])
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command_list[0], command_list[1:])
            
            logger.info(f"Starting smbclient {scan.id}")
            
            self._start_scan_thread(scan.id, sanitized_cmd, output_file, 'smbclient')
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'smbclient',
                'target': target,
                'share': share
            }
            
        except Exception as e:
            logger.error(f"Error starting smbclient: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def start_nmap_smb_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        scripts: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Enumeración SMB con Nmap scripts.
        
        Args:
            target: IP objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            scripts: Lista de scripts específicos (opcional)
                     Default: smb-enum-shares, smb-enum-users, smb-os-discovery
        
        Returns:
            Dict con información del escaneo
        """
        CommandSanitizer.validate_target(target)
        
        if not scripts:
            scripts = ['smb-enum-shares', 'smb-enum-users', 'smb-os-discovery', 'smb-protocols']
        
        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='nmap',
            options={'scripts': scripts, 'port': 445}
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = str(workspace_output_dir / f'nmap_smb_{scan.id}.xml')
            
            command = SafeNmap.build_script_scan(
                target=target,
                port=445,
                scripts=scripts,
                output_file=output_file
            )
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting Nmap SMB enum {scan.id}")
            
            self._start_scan_thread(scan.id, sanitized_cmd, output_file, 'nmap')
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'nmap',
                'target': target,
                'scripts': scripts
            }
            
        except Exception as e:
            logger.error(f"Error starting Nmap SMB enum: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # PREVIEW METHODS
    # ============================================
    
    def preview_enum4linux(
        self,
        target: str,
        workspace_id: int,
        use_ng: bool = True,
        all: bool = False
    ) -> Dict[str, Any]:
        """Preview del comando enum4linux."""
        CommandSanitizer.validate_target(target)
        
        # Detectar herramienta disponible
        if use_ng:
            if shutil.which('enum4linux-ng'):
                tool = 'enum4linux-ng'
            elif shutil.which('enum4linux'):
                tool = 'enum4linux'
            else:
                tool = 'enum4linux-ng'  # Default para preview
        else:
            tool = 'enum4linux'
        
        output_file = f'/workspaces/workspace_{workspace_id}/enumeration/{tool}_{{scan_id}}.txt'
        
        if tool == 'enum4linux-ng':
            command = ['enum4linux-ng', target]
            if all:
                command.append('-A')
        else:  # enum4linux
            command = ['enum4linux', '-a', target] if all else ['enum4linux', target]
        
        command_str = ' '.join([str(c) for c in command])
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': tool,
                'target': target,
                'use_ng': use_ng,
                'all': all
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_smbmap(
        self,
        target: str,
        workspace_id: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        hash: Optional[str] = None,
        recursive: bool = False,
        share: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando smbmap."""
        CommandSanitizer.validate_target(target)
        
        output_file = f'/workspaces/workspace_{workspace_id}/enumeration/smbmap_{{scan_id}}.txt'
        
        command = ['smbmap', '-H', target]
        
        if username:
            command.extend(['-u', username])
        if password:
            command.extend(['-p', password])
        if hash:
            command.extend(['--hash', hash])  # smbmap usa --hash para hash NTLM, no -H
        if recursive and share:
            command.extend(['-r', '-d', share])
        elif share:
            command.extend(['-d', share])
        
        command_str = ' '.join([str(c) for c in command])
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'smbmap',
                'target': target,
                'username': username,
                'password': '[PROVIDED]' if password else None,
                'hash': '[PROVIDED]' if hash else None,
                'recursive': recursive,
                'share': share
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_smbclient(
        self,
        target: str,
        workspace_id: int,
        share: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        command: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando smbclient."""
        CommandSanitizer.validate_target(target)
        
        output_file = f'/workspaces/workspace_{workspace_id}/enumeration/smbclient_{{scan_id}}.txt'
        
        share_path = f'//{target}/{share}'
        command_list = ['smbclient', share_path, '-N']
        
        if username:
            command_list.extend(['-U', username])
        if password:
            command_list[-1] = password  # Reemplazar -N con password
        
        if command:
            command_list.extend(['-c', command])
        
        command_str = ' '.join([str(c) for c in command_list])
        
        return {
            'command': command_list,
            'command_string': command_str,
            'parameters': {
                'tool': 'smbclient',
                'target': target,
                'share': share,
                'username': username,
                'password': '[PROVIDED]' if password else None,
                'command': command
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }

