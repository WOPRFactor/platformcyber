"""
GetNPUsers Scanner
==================

Scanner para GetNPUsers (AS-REP Roasting).
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from repositories import ScanRepository
from utils.validators import CommandSanitizer
from utils.parsers.ad_parser import GetNPUsersParser
from services.active_directory.base import BaseADService
from services.active_directory.executors.scan_executor import ADScanExecutor

logger = logging.getLogger(__name__)


class GetNPUsersScanner(BaseADService):
    """Scanner para GetNPUsers."""

    def __init__(self, scan_repository: ScanRepository = None):
        super().__init__(scan_repository)
        self.getnpusers_parser = GetNPUsersParser()
        self.executor = ADScanExecutor(self.scan_repo)

    def start_scan(
        self,
        domain: str,
        workspace_id: int,
        user_id: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        dc_ip: Optional[str] = None,
        usersfile: Optional[str] = None,
        no_pass: bool = True
    ) -> Dict[str, Any]:
        """AS-REP Roasting con GetNPUsers.py."""
        scan = self.scan_repo.create(
            scan_type='active_directory',
            target=domain,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'getnpusers',
                'no_pass': no_pass
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'getnpusers_{scan.id}.txt'

            command = [
                'GetNPUsers.py',
                domain + '/',
                '-outputfile', str(output_file),
                '-format', 'hashcat'
            ]

            if no_pass:
                command.append('-no-pass')
            else:
                if username and password:
                    command[1] = f'{domain}/{username}:{password}'

            if dc_ip:
                command.extend(['-dc-ip', dc_ip])

            if usersfile:
                command.extend(['-usersfile', usersfile])
            else:
                command.append('-request')

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting GetNPUsers {scan.id}")

            self.executor.execute_scan_in_thread(scan.id, sanitized_cmd, output_file, 'getnpusers')
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'getnpusers',
                'domain': domain
            }

        except Exception as e:
            logger.error(f"Error starting GetNPUsers: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

    def get_results(self, scan_id: int) -> Dict[str, Any]:
        """Obtiene y parsea resultados de GetNPUsers."""
        scan = self.scan_repo.find_by_id(scan_id)
        if not scan:
            raise ValueError(f'Scan {scan_id} not found')
        if scan.status != 'completed':
            return {'scan_id': scan_id, 'status': scan.status, 'message': 'Scan not completed yet'}

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'getnpusers_{scan_id}.txt'
            with open(output_file, 'r') as f:
                results = self.getnpusers_parser.parse_output(f.read())

            return {
                'scan_id': scan_id,
                'status': 'completed',
                'tool': 'getnpusers',
                'results': results,
                'scan_info': {
                    'target': scan.target,
                    'started_at': scan.started_at.isoformat() if scan.started_at else None,
                    'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
                }
            }
        except Exception as e:
            logger.error(f"Error parsing GetNPUsers results {scan_id}: {e}")
            return {'scan_id': scan_id, 'error': f'Failed to parse results: {str(e)}'}

