"""
RDP Enumeration
===============

Enumeración RDP con Nmap.
"""

import logging
from typing import Dict, Any
from pathlib import Path

from utils.validators import CommandSanitizer
from utils.commands import SafeNmap
from ..base import BaseEnumerationService

logger = logging.getLogger(__name__)


class RDPEnumeration(BaseEnumerationService):
    """Enumeración RDP."""

    def start_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        port: int = 3389
    ) -> Dict[str, Any]:
        """Enumeración RDP con Nmap scripts."""
        CommandSanitizer.validate_target(target)

        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool='nmap',
            options={'port': port, 'service': 'rdp'}
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'nmap_rdp_{scan.id}.xml'
            scripts = ['rdp-enum-encryption', 'rdp-ntlm-info']

            command = SafeNmap.build_script_scan(
                target=target,
                port=port,
                scripts=scripts,
                output_file=str(output_file)
            )

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting Nmap RDP enum {scan.id}")

            self._start_scan_thread(scan.id, sanitized_cmd, str(output_file), 'nmap')
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'nmap',
                'target': target,
                'port': port
            }

        except Exception as e:
            logger.error(f"Error starting RDP enum: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

    def preview_enum(
        self,
        target: str,
        workspace_id: int,
        port: int = 3389
    ) -> Dict[str, Any]:
        """Preview del comando RDP enum."""
        CommandSanitizer.validate_target(target)

        output_file = f'/workspaces/workspace_{workspace_id}/enumeration/nmap_rdp_{{scan_id}}.xml'
        scripts = ['rdp-enum-encryption', 'rdp-ntlm-info']

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
                'service': 'rdp',
                'scripts': scripts
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }

