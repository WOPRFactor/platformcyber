"""
CrackMapExec AD Scanner
========================

Scanner para CrackMapExec AD enumeration.
"""

import logging
from typing import Dict, Any
from pathlib import Path

from repositories import ScanRepository
from utils.validators import CommandSanitizer, IPValidator
from utils.parsers.ad_parser import CrackMapExecADParser
from services.active_directory.base import BaseADService
from services.active_directory.executors.scan_executor import ADScanExecutor

logger = logging.getLogger(__name__)


class CrackMapExecADScanner(BaseADService):
    """Scanner para CrackMapExec AD."""

    def __init__(self, scan_repository: ScanRepository = None):
        super().__init__(scan_repository)
        self.cme_ad_parser = CrackMapExecADParser()
        self.executor = ADScanExecutor(self.scan_repo)

    def start_enum_users(
        self,
        dc_ip: str,
        username: str,
        password: str,
        domain: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Enumera usuarios AD con CrackMapExec."""
        IPValidator.validate(dc_ip)

        scan = self.scan_repo.create(
            scan_type='active_directory',
            target=dc_ip,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'crackmapexec',
                'action': 'enum_users',
                'domain': domain
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'cme_users_{scan.id}.txt'

            command = [
                'crackmapexec', 'smb', dc_ip,
                '-u', username,
                '-p', password,
                '-d', domain,
                '--users',
                '--log', str(output_file)
            ]

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting CME enum users {scan.id}")

            self.executor.execute_scan_in_thread(scan.id, sanitized_cmd, output_file, 'crackmapexec')
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'crackmapexec',
                'action': 'enum_users',
                'target': dc_ip
            }

        except Exception as e:
            logger.error(f"Error starting CME enum users: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

    def start_enum_groups(
        self,
        dc_ip: str,
        username: str,
        password: str,
        domain: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Enumera grupos AD con CrackMapExec."""
        IPValidator.validate(dc_ip)

        scan = self.scan_repo.create(
            scan_type='active_directory',
            target=dc_ip,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'crackmapexec',
                'action': 'enum_groups',
                'domain': domain
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'cme_groups_{scan.id}.txt'

            command = [
                'crackmapexec', 'smb', dc_ip,
                '-u', username,
                '-p', password,
                '-d', domain,
                '--groups',
                '--log', str(output_file)
            ]

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting CME enum groups {scan.id}")

            self.executor.execute_scan_in_thread(scan.id, sanitized_cmd, output_file, 'crackmapexec')
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'crackmapexec',
                'action': 'enum_groups',
                'target': dc_ip
            }

        except Exception as e:
            logger.error(f"Error starting CME enum groups: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

    def get_results(self, scan_id: int, action: str) -> Dict[str, Any]:
        """Obtiene y parsea resultados de CrackMapExec."""
        scan = self.scan_repo.find_by_id(scan_id)
        if not scan:
            raise ValueError(f'Scan {scan_id} not found')
        if scan.status != 'completed':
            return {'scan_id': scan_id, 'status': scan.status, 'message': 'Scan not completed yet'}

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            if action == 'enum_users':
                output_file = workspace_output_dir / f'cme_users_{scan_id}.txt'
                with open(output_file, 'r') as f:
                    results = self.cme_ad_parser.parse_enum_users(f.read())
            elif action == 'enum_groups':
                output_file = workspace_output_dir / f'cme_groups_{scan_id}.txt'
                with open(output_file, 'r') as f:
                    results = self.cme_ad_parser.parse_enum_groups(f.read())
            else:
                results = {'error': f'Unknown CME action: {action}'}

            return {
                'scan_id': scan_id,
                'status': 'completed',
                'tool': 'crackmapexec',
                'action': action,
                'results': results,
                'scan_info': {
                    'target': scan.target,
                    'started_at': scan.started_at.isoformat() if scan.started_at else None,
                    'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
                }
            }
        except Exception as e:
            logger.error(f"Error parsing CME results {scan_id}: {e}")
            return {'scan_id': scan_id, 'error': f'Failed to parse results: {str(e)}'}

