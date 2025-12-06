"""
SNMP Enumeration
================

Enumeración SNMP con snmpwalk, onesixtyone y Nmap.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import CommandSanitizer
from utils.commands import SafeNmap
from ..base import BaseEnumerationService

logger = logging.getLogger(__name__)


class SNMPEnumeration(BaseEnumerationService):
    """Enumeración SNMP."""

    def start_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        tool: str = 'nmap',
        port: int = 161,
        community: str = 'public',
        community_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enumeración SNMP."""
        CommandSanitizer.validate_target(target)

        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool=tool,
            options={'port': port, 'service': 'snmp'}
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            if tool == 'snmpwalk':
                output_file = workspace_output_dir / f'snmpwalk_{scan.id}.txt'
                command = ['snmpwalk', '-v2c', '-c', community, target]
            elif tool == 'onesixtyone':
                if not community_file:
                    raise ValueError('community_file is required for onesixtyone')
                output_file = workspace_output_dir / f'onesixtyone_{scan.id}.txt'
                command = ['onesixtyone', '-c', community_file, target]
            else:  # nmap
                output_file = workspace_output_dir / f'nmap_snmp_{scan.id}.xml'
                scripts = ['snmp-info', 'snmp-brute', 'snmp-processes']
                # SNMP usa UDP, necesitamos construir el comando manualmente con -sU
                command = ['nmap', '-sU', '-sV', '--script', ','.join(scripts), '-p', str(port), '-oA', str(output_file).replace('.xml', ''), target]

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting {tool} SNMP enum {scan.id}")

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
            logger.error(f"Error starting SNMP enum: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

    def preview_enum(
        self,
        target: str,
        workspace_id: int,
        tool: str = 'nmap',
        port: int = 161,
        community: str = 'public',
        community_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando SNMP enum."""
        CommandSanitizer.validate_target(target)

        if tool == 'snmpwalk':
            output_file = f'/workspaces/workspace_{workspace_id}/enumeration/snmpwalk_{{scan_id}}.txt'
            command = ['snmpwalk', '-v2c', '-c', community, target]
        elif tool == 'onesixtyone':
            if not community_file:
                raise ValueError('community_file is required for onesixtyone')
            output_file = f'/workspaces/workspace_{workspace_id}/enumeration/onesixtyone_{{scan_id}}.txt'
            command = ['onesixtyone', '-c', community_file, target]
        else:  # nmap
            output_file = f'/workspaces/workspace_{workspace_id}/enumeration/nmap_snmp_{{scan_id}}.xml'
            scripts = ['snmp-info', 'snmp-brute', 'snmp-processes']
            # SNMP usa UDP, necesitamos construir el comando manualmente con -sU
            command = ['nmap', '-sU', '-sV', '--script', ','.join(scripts), '-p', str(port), '-oA', output_file.replace('.xml', ''), target]

        command_str = ' '.join([str(c) for c in command])

        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tool': tool,
                'target': target,
                'port': port,
                'service': 'snmp',
                'community': community if tool == 'snmpwalk' else None,
                'community_file': community_file if tool == 'onesixtyone' else None,
                'scripts': scripts if tool == 'nmap' else None
            },
            'estimated_timeout': 600 if tool == 'onesixtyone' else 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }

