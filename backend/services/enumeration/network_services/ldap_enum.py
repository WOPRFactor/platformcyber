"""
LDAP Enumeration
================

Enumeración LDAP con ldapsearch y Nmap.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from utils.commands import SafeNmap
from ..base import BaseEnumerationService

logger = logging.getLogger(__name__)


class LDAPEnumeration(BaseEnumerationService):
    """Enumeración LDAP."""

    def start_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'nmap',
        port: int = 389,
        base_dn: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enumeración LDAP."""
        CommandSanitizer.validate_target(target)

        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool=tool,
            options={'port': port, 'service': 'ldap'}
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            if tool == 'ldapsearch':
                output_file = workspace_output_dir / f'ldapsearch_{scan.id}.txt'
                command = ['ldapsearch', '-x', '-H', f'ldap://{target}', '-b', base_dn or '']
            else:  # nmap
                output_file = workspace_output_dir / f'nmap_ldap_{scan.id}.xml'
                scripts = ['ldap-rootdse', 'ldap-search']
                command = SafeNmap.build_script_scan(
                    target=target,
                    port=port,
                    scripts=scripts,
                    output_file=str(output_file)
                )

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting {tool} LDAP enum {scan.id}")

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
            logger.error(f"Error starting LDAP enum: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

    def preview_enum(
        self,
        target: str,
        workspace_id: int,
        tool: str = 'nmap',
        port: int = 389,
        base_dn: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando LDAP enum."""
        CommandSanitizer.validate_target(target)

        if tool == 'ldapsearch':
            output_file = f'/workspaces/workspace_{workspace_id}/enumeration/ldapsearch_{{scan_id}}.txt'
            command = ['ldapsearch', '-x', '-H', f'ldap://{target}', '-b', base_dn or '']
        else:  # nmap
            output_file = f'/workspaces/workspace_{workspace_id}/enumeration/nmap_ldap_{{scan_id}}.xml'
            scripts = ['ldap-rootdse', 'ldap-search']
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
                'service': 'ldap',
                'base_dn': base_dn if tool == 'ldapsearch' else None,
                'scripts': scripts if tool == 'nmap' else None
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }

