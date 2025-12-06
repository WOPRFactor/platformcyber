"""
DNS Enumeration
===============

Enumeración DNS con dig y Nmap.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from utils.validators import CommandSanitizer, DomainValidator
from utils.commands import SafeNmap
from ..base import BaseEnumerationService

logger = logging.getLogger(__name__)


class DNSEnumeration(BaseEnumerationService):
    """Enumeración DNS."""

    def start_enum(
        self,
        target: str,
        workspace_id: int,
        user_id: int,
        domain: Optional[str] = None,
        tool: str = 'nmap',
        port: int = 53
    ) -> Dict[str, Any]:
        """Enumeración DNS."""
        CommandSanitizer.validate_target(target)

        # Si no se proporciona domain, intentar usar target como domain
        if not domain:
            if DomainValidator.is_valid_domain(target):
                domain = target
            else:
                raise ValueError('domain is required when target is an IP address')

        DomainValidator.is_valid_domain(domain)

        scan = self._create_scan(
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            tool=tool,
            options={'port': port, 'service': 'dns', 'domain': domain}
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            if tool == 'dig':
                output_file = workspace_output_dir / f'dig_zone_{scan.id}.txt'
                command = ['dig', '@' + target, 'axfr', domain]
            else:  # nmap
                output_file = workspace_output_dir / f'nmap_dns_{scan.id}.xml'
                scripts = ['dns-zone-transfer', 'dns-recursion']
                command = SafeNmap.build_script_scan(
                    target=target,
                    port=port,
                    scripts=scripts,
                    output_file=str(output_file)
                )

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting {tool} DNS enum {scan.id}")

            self._start_scan_thread(scan.id, sanitized_cmd, str(output_file), tool)
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': tool,
                'target': target,
                'domain': domain
            }

        except Exception as e:
            logger.error(f"Error starting DNS enum: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

    def preview_enum(
        self,
        target: str,
        workspace_id: int,
        domain: Optional[str] = None,
        tool: str = 'nmap',
        port: int = 53
    ) -> Dict[str, Any]:
        """Preview del comando DNS enum."""
        CommandSanitizer.validate_target(target)

        if not domain:
            if DomainValidator.is_valid_domain(target):
                domain = target
            else:
                raise ValueError('domain is required when target is an IP address')

        DomainValidator.is_valid_domain(domain)

        if tool == 'dig':
            output_file = f'/workspaces/workspace_{workspace_id}/enumeration/dig_zone_{{scan_id}}.txt'
            command = ['dig', '@' + target, 'axfr', domain]
        else:  # nmap
            output_file = f'/workspaces/workspace_{workspace_id}/enumeration/nmap_dns_{{scan_id}}.xml'
            scripts = ['dns-zone-transfer', 'dns-recursion']
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
                'domain': domain,
                'port': port,
                'service': 'dns'
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }

