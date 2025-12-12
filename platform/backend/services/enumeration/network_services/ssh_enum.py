"""
SSH Enumeration
===============

Enumeración SSH con ssh-audit y Nmap.
"""

import logging
from typing import Dict, Any
from pathlib import Path

from utils.validators import CommandSanitizer
from utils.commands import SafeNmap
from ..base import BaseEnumerationService

logger = logging.getLogger(__name__)


class SSHEnumeration(BaseEnumerationService):
    """Enumeración SSH."""

    def start_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'nmap',
        port: int = 22
    ) -> Dict[str, Any]:
        """Enumeración SSH."""
        CommandSanitizer.validate_target(target)

        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool=tool,
            options={'port': port, 'service': 'ssh'}
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            if tool == 'ssh-audit':
                output_file = workspace_output_dir / f'ssh-audit_{scan.id}.txt'
                command = ['ssh-audit', f'{target}:{port}']
            else:  # nmap
                output_file = workspace_output_dir / f'nmap_ssh_{scan.id}.xml'
                scripts = ['ssh-hostkey', 'ssh2-enum-algos', 'ssh-auth-methods']
                command = SafeNmap.build_script_scan(
                    target=target,
                    port=port,
                    scripts=scripts,
                    output_file=str(output_file)
                )

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting {tool} SSH enum {scan.id}")

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
            logger.error(f"Error starting SSH enum: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

    def preview_enum(
        self,
        target: str,
        workspace_id: int,
        tool: str = 'nmap',
        port: int = 22
    ) -> Dict[str, Any]:
        """Preview del comando SSH enum."""
        CommandSanitizer.validate_target(target)

        output_file = f'/workspaces/workspace_{workspace_id}/enumeration/{"ssh-audit" if tool == "ssh-audit" else "nmap_ssh"}_{{scan_id}}.{"txt" if tool == "ssh-audit" else "xml"}'
        
        if tool == 'ssh-audit':
            command = ['ssh-audit', f'{target}:{port}']
        else:  # nmap
            scripts = ['ssh-hostkey', 'ssh2-enum-algos', 'ssh-auth-methods']
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
                'service': 'ssh',
                'scripts': scripts if tool == 'nmap' else None
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }

