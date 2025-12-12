"""
SMTP Enumeration
================

Enumeración SMTP con smtp-user-enum y Nmap.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from utils.commands import SafeNmap
from ..base import BaseEnumerationService

logger = logging.getLogger(__name__)


class SMTPEnumeration(BaseEnumerationService):
    """Enumeración SMTP."""

    def start_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'nmap',
        port: int = 25,
        userlist: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enumeración SMTP."""
        CommandSanitizer.validate_target(target)

        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool=tool,
            options={'port': port, 'service': 'smtp'}
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            if tool == 'smtp-user-enum':
                if not userlist:
                    raise ValueError('userlist is required for smtp-user-enum')
                output_file = workspace_output_dir / f'smtp-user-enum_{scan.id}.txt'
                command = ['smtp-user-enum', '-M', 'VRFY', '-U', userlist, '-t', target]
            else:  # nmap
                output_file = workspace_output_dir / f'nmap_smtp_{scan.id}.xml'
                scripts = ['smtp-commands', 'smtp-enum-users', 'smtp-vuln-cve2010-4344']
                command = SafeNmap.build_script_scan(
                    target=target,
                    port=port,
                    scripts=scripts,
                    output_file=str(output_file)
                )

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting {tool} SMTP enum {scan.id}")

            self._start_scan_thread(scan.id, sanitized_cmd, str(output_file), tool)
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': tool,
                'target': target,
                'port': port
            }

        except Exception as e:
            logger.error(f"Error starting SMTP enum: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

    def preview_enum(
        self,
        target: str,
        workspace_id: int,
        tool: str = 'nmap',
        port: int = 25,
        userlist: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando SMTP enum."""
        CommandSanitizer.validate_target(target)

        output_file = f'/workspaces/workspace_{workspace_id}/enumeration/{"smtp-user-enum" if tool == "smtp-user-enum" else "nmap_smtp"}_{{scan_id}}.{"txt" if tool == "smtp-user-enum" else "xml"}'
        
        if tool == 'smtp-user-enum':
            if not userlist:
                raise ValueError('userlist is required for smtp-user-enum')
            command = ['smtp-user-enum', '-M', 'VRFY', '-U', userlist, '-t', target]
        else:  # nmap
            scripts = ['smtp-commands', 'smtp-enum-users', 'smtp-vuln-cve2010-4344']
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
                'service': 'smtp',
                'userlist': userlist if tool == 'smtp-user-enum' else None,
                'scripts': scripts if tool == 'nmap' else None
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }

