"""
LDAP Domain Dump Scanner
========================

Scanner para ldapdomaindump.
"""

import logging
from typing import Dict, Any
from pathlib import Path

from repositories import ScanRepository
from utils.validators import CommandSanitizer, IPValidator
from utils.parsers.ad_parser import LDAPDomainDumpParser
from services.active_directory.base import BaseADService
from services.active_directory.executors.scan_executor import ADScanExecutor

logger = logging.getLogger(__name__)


class LDAPDomainDumpScanner(BaseADService):
    """Scanner para ldapdomaindump."""

    def __init__(self, scan_repository: ScanRepository = None):
        super().__init__(scan_repository)
        self.ldapdump_parser = LDAPDomainDumpParser()
        self.executor = ADScanExecutor(self.scan_repo)

    def start_scan(
        self,
        dc_ip: str,
        username: str,
        password: str,
        domain: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Dump de información LDAP."""
        IPValidator.validate(dc_ip)

        scan = self.scan_repo.create(
            scan_type='active_directory',
            target=dc_ip,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'ldapdomaindump',
                'domain': domain
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_dir = workspace_output_dir / f'ldapdump_{scan.id}'
            output_dir.mkdir(exist_ok=True)

            command = [
                'ldapdomaindump',
                '-u', f'{domain}\\{username}',
                '-p', password,
                dc_ip,
                '-o', str(output_dir)
            ]

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting ldapdomaindump {scan.id}")

            self.executor.execute_scan_in_thread(scan.id, sanitized_cmd, output_dir, 'ldapdomaindump')
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'ldapdomaindump',
                'target': dc_ip
            }

        except Exception as e:
            logger.error(f"Error starting ldapdomaindump: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

    def get_results(self, scan_id: int) -> Dict[str, Any]:
        """Obtiene y parsea resultados de ldapdomaindump."""
        scan = self.scan_repo.find_by_id(scan_id)
        if not scan:
            raise ValueError(f'Scan {scan_id} not found')
        if scan.status != 'completed':
            return {'scan_id': scan_id, 'status': scan.status, 'message': 'Scan not completed yet'}

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_dir = workspace_output_dir / f'ldapdump_{scan_id}'
            json_files = list(output_dir.glob('*.json'))
            if json_files:
                results = self.ldapdump_parser.parse_json(str(json_files[0]))
            else:
                results = {'message': 'Check HTML reports in output directory'}

            return {
                'scan_id': scan_id,
                'status': 'completed',
                'tool': 'ldapdomaindump',
                'results': results,
                'scan_info': {
                    'target': scan.target,
                    'started_at': scan.started_at.isoformat() if scan.started_at else None,
                    'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
                }
            }
        except Exception as e:
            logger.error(f"Error parsing ldapdomaindump results {scan_id}: {e}")
            return {'scan_id': scan_id, 'error': f'Failed to parse results: {str(e)}'}

