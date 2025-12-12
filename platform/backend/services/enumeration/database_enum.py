"""
Database Enumeration Service
============================

Servicios para enumeración de bases de datos:
- MySQL (Nmap scripts, mysql client)
- PostgreSQL (Nmap scripts, psql)
- Redis (Nmap scripts, redis-cli)
- MongoDB (Nmap scripts)
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from utils.commands import SafeNmap
from .base import BaseEnumerationService

logger = logging.getLogger(__name__)


class DatabaseEnumerationService(BaseEnumerationService):
    """Servicio para enumeración de bases de datos."""
    
    def start_mysql_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'nmap',
        port: int = 3306,
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enumeración MySQL.
        
        Args:
            target: IP objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            tool: 'nmap' o 'mysql'
            port: Puerto MySQL (default: 3306)
            username: Usuario para mysql client (opcional)
        
        Returns:
            Dict con información del escaneo
        """
        CommandSanitizer.validate_target(target)
        
        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool=tool,
            options={'port': port, 'service': 'mysql'}
        )
        
        try:
            if tool == 'mysql':
                output_file = str(self.output_dir / f'mysql_{scan.id}.txt')
                command = ['mysql', '-h', target, '-u', username or 'root', '-e', 'SHOW DATABASES;']
            else:  # nmap
                output_file = str(self.output_dir / f'nmap_mysql_{scan.id}.xml')
                scripts = ['mysql-info', 'mysql-enum', 'mysql-empty-password']
                command = SafeNmap.build_script_scan(
                    target=target,
                    port=port,
                    scripts=scripts,
                    output_file=output_file
                )
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting {tool} MySQL enum {scan.id}")
            
            self._start_scan_thread(scan.id, sanitized_cmd, output_file, tool)
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': tool,
                'target': target,
                'port': port
            }
            
        except Exception as e:
            logger.error(f"Error starting MySQL enum: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def start_postgresql_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'nmap',
        port: int = 5432,
        username: str = 'postgres'
    ) -> Dict[str, Any]:
        """
        Enumeración PostgreSQL.
        
        Args:
            target: IP objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            tool: 'nmap' o 'psql'
            port: Puerto PostgreSQL (default: 5432)
            username: Usuario para psql (default: postgres)
        
        Returns:
            Dict con información del escaneo
        """
        CommandSanitizer.validate_target(target)
        
        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool=tool,
            options={'port': port, 'service': 'postgresql'}
        )
        
        try:
            if tool == 'psql':
                output_file = str(self.output_dir / f'psql_{scan.id}.txt')
                command = ['psql', '-h', target, '-U', username, '-c', '\\l']
            else:  # nmap
                output_file = str(self.output_dir / f'nmap_postgresql_{scan.id}.xml')
                scripts = ['pgsql-brute']
                command = SafeNmap.build_script_scan(
                    target=target,
                    port=port,
                    scripts=scripts,
                    output_file=output_file
                )
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting {tool} PostgreSQL enum {scan.id}")
            
            self._start_scan_thread(scan.id, sanitized_cmd, output_file, tool)
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': tool,
                'target': target,
                'port': port
            }
            
        except Exception as e:
            logger.error(f"Error starting PostgreSQL enum: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def start_redis_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'nmap',
        port: int = 6379
    ) -> Dict[str, Any]:
        """
        Enumeración Redis.
        
        Args:
            target: IP objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            tool: 'nmap' o 'redis-cli'
            port: Puerto Redis (default: 6379)
        
        Returns:
            Dict con información del escaneo
        """
        CommandSanitizer.validate_target(target)
        
        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool=tool,
            options={'port': port, 'service': 'redis'}
        )
        
        try:
            if tool == 'redis-cli':
                output_file = str(self.output_dir / f'redis-cli_{scan.id}.txt')
                command = ['redis-cli', '-h', target, 'INFO']
            else:  # nmap
                output_file = str(self.output_dir / f'nmap_redis_{scan.id}.xml')
                scripts = ['redis-info']
                command = SafeNmap.build_script_scan(
                    target=target,
                    port=port,
                    scripts=scripts,
                    output_file=output_file
                )
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting {tool} Redis enum {scan.id}")
            
            self._start_scan_thread(scan.id, sanitized_cmd, output_file, tool)
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': tool,
                'target': target,
                'port': port
            }
            
        except Exception as e:
            logger.error(f"Error starting Redis enum: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    def start_mongodb_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        port: int = 27017
    ) -> Dict[str, Any]:
        """
        Enumeración MongoDB con Nmap scripts.
        
        Args:
            target: IP objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            port: Puerto MongoDB (default: 27017)
        
        Returns:
            Dict con información del escaneo
        """
        CommandSanitizer.validate_target(target)
        
        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='nmap',
            options={'port': port, 'service': 'mongodb'}
        )
        
        try:
            output_file = str(self.output_dir / f'nmap_mongodb_{scan.id}.xml')
            scripts = ['mongodb-info', 'mongodb-databases']
            
            command = SafeNmap.build_script_scan(
                target=target,
                port=port,
                scripts=scripts,
                output_file=output_file
            )
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting nmap MongoDB enum {scan.id}")
            
            self._start_scan_thread(scan.id, sanitized_cmd, output_file, 'nmap')
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'nmap',
                'target': target,
                'port': port
            }
            
        except Exception as e:
            logger.error(f"Error starting MongoDB enum: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

    # ============================================
    # PREVIEW METHODS
    # ============================================

    def preview_mysql_enum(
        self,
        target: str,
        workspace_id: int,
        tool: str = 'nmap',
        port: int = 3306,
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando MySQL enum."""
        CommandSanitizer.validate_target(target)

        output_file = f'/workspaces/workspace_{workspace_id}/enumeration/{"mysql" if tool == "mysql" else "nmap_mysql"}_{{scan_id}}.{"txt" if tool == "mysql" else "xml"}'
        
        if tool == 'mysql':
            command = ['mysql', '-h', target, '-u', username or 'root', '-e', 'SHOW DATABASES;']
        else:  # nmap
            scripts = ['mysql-info', 'mysql-enum', 'mysql-empty-password']
            command = SafeNmap.build_script_scan(
                target=target,
                port=port,
                scripts=scripts,
                output_file=output_file
            )

        command_str = ' '.join([str(c) for c in command])

        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': tool,
                'target': target,
                'port': port,
                'service': 'mysql',
                'username': username or 'root' if tool == 'mysql' else None,
                'scripts': scripts if tool == 'nmap' else None
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }

    def preview_postgresql_enum(
        self,
        target: str,
        workspace_id: int,
        tool: str = 'nmap',
        port: int = 5432,
        username: str = 'postgres'
    ) -> Dict[str, Any]:
        """Preview del comando PostgreSQL enum."""
        CommandSanitizer.validate_target(target)

        output_file = f'/workspaces/workspace_{workspace_id}/enumeration/{"psql" if tool == "psql" else "nmap_postgresql"}_{{scan_id}}.{"txt" if tool == "psql" else "xml"}'
        
        if tool == 'psql':
            command = ['psql', '-h', target, '-U', username, '-c', '\\l']
        else:  # nmap
            scripts = ['pgsql-brute']
            command = SafeNmap.build_script_scan(
                target=target,
                port=port,
                scripts=scripts,
                output_file=output_file
            )

        command_str = ' '.join([str(c) for c in command])

        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': tool,
                'target': target,
                'port': port,
                'service': 'postgresql',
                'username': username if tool == 'psql' else None,
                'scripts': scripts if tool == 'nmap' else None
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }

    def preview_redis_enum(
        self,
        target: str,
        workspace_id: int,
        tool: str = 'nmap',
        port: int = 6379
    ) -> Dict[str, Any]:
        """Preview del comando Redis enum."""
        CommandSanitizer.validate_target(target)

        output_file = f'/workspaces/workspace_{workspace_id}/enumeration/{"redis-cli" if tool == "redis-cli" else "nmap_redis"}_{{scan_id}}.{"txt" if tool == "redis-cli" else "xml"}'
        
        if tool == 'redis-cli':
            command = ['redis-cli', '-h', target, 'INFO']
        else:  # nmap
            scripts = ['redis-info']
            command = SafeNmap.build_script_scan(
                target=target,
                port=port,
                scripts=scripts,
                output_file=output_file
            )

        command_str = ' '.join([str(c) for c in command])

        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': tool,
                'target': target,
                'port': port,
                'service': 'redis',
                'scripts': scripts if tool == 'nmap' else None
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }

    def preview_mongodb_enum(
        self,
        target: str,
        workspace_id: int,
        port: int = 27017
    ) -> Dict[str, Any]:
        """Preview del comando MongoDB enum."""
        CommandSanitizer.validate_target(target)

        output_file = f'/workspaces/workspace_{workspace_id}/enumeration/nmap_mongodb_{{scan_id}}.xml'
        scripts = ['mongodb-info', 'mongodb-databases']
        
        command = SafeNmap.build_script_scan(
            target=target,
            port=port,
            scripts=scripts,
            output_file=output_file
        )

        command_str = ' '.join([str(c) for c in command])

        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': 'nmap',
                'target': target,
                'port': port,
                'service': 'mongodb',
                'scripts': scripts
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }