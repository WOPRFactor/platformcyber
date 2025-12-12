"""
Kerbrute Scanner
================

Scanner para Kerbrute (user enumeration & password spraying).
"""

import logging
from typing import Dict, Any
from pathlib import Path

from repositories import ScanRepository
from utils.validators import CommandSanitizer, IPValidator
from utils.parsers.ad_parser import KerbruteParser
from services.active_directory.base import BaseADService
from services.active_directory.executors.scan_executor import ADScanExecutor

logger = logging.getLogger(__name__)


class KerbruteScanner(BaseADService):
    """Scanner para Kerbrute."""

    def __init__(self, scan_repository: ScanRepository = None):
        super().__init__(scan_repository)
        self.kerbrute_parser = KerbruteParser()
        self.executor = ADScanExecutor(self.scan_repo)

    def start_userenum(
        self,
        domain: str,
        dc_ip: str,
        userlist: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Enumera usuarios válidos con Kerbrute."""
        IPValidator.validate(dc_ip)

        scan = self.scan_repo.create(
            scan_type='active_directory',
            target=domain,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'kerbrute',
                'action': 'userenum',
                'dc_ip': dc_ip
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'kerbrute_userenum_{scan.id}.txt'

            command = [
                'kerbrute',
                'userenum',
                '-d', domain,
                '--dc', dc_ip,
                userlist,
                '-o', str(output_file)
            ]

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting Kerbrute userenum {scan.id}")

            self.executor.execute_scan_in_thread(scan.id, sanitized_cmd, output_file, 'kerbrute')
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'kerbrute',
                'action': 'userenum',
                'domain': domain
            }

        except Exception as e:
            logger.error(f"Error starting Kerbrute: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

    def start_passwordspray(
        self,
        domain: str,
        dc_ip: str,
        userlist: str,
        password: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Password spraying con Kerbrute."""
        IPValidator.validate(dc_ip)

        scan = self.scan_repo.create(
            scan_type='active_directory',
            target=domain,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'kerbrute',
                'action': 'passwordspray',
                'dc_ip': dc_ip
            }
        )

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'kerbrute_spray_{scan.id}.txt'

            command = [
                'kerbrute',
                'passwordspray',
                '-d', domain,
                '--dc', dc_ip,
                userlist,
                password,
                '-o', str(output_file)
            ]

            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])

            logger.info(f"Starting Kerbrute password spray {scan.id}")

            self.executor.execute_scan_in_thread(scan.id, sanitized_cmd, output_file, 'kerbrute')
            self.scan_repo.update_status(scan, 'running')

            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'kerbrute',
                'action': 'passwordspray',
                'domain': domain
            }

        except Exception as e:
            logger.error(f"Error starting Kerbrute spray: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise

    def get_results(self, scan_id: int, action: str) -> Dict[str, Any]:
        """Obtiene y parsea resultados de Kerbrute."""
        scan = self.scan_repo.find_by_id(scan_id)
        if not scan:
            raise ValueError(f'Scan {scan_id} not found')
        if scan.status != 'completed':
            return {'scan_id': scan_id, 'status': scan.status, 'message': 'Scan not completed yet'}

        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = workspace_output_dir / f'kerbrute_{action}_{scan_id}.txt'
            with open(output_file, 'r') as f:
                results = self.kerbrute_parser.parse_output(f.read())

            return {
                'scan_id': scan_id,
                'status': 'completed',
                'tool': 'kerbrute',
                'action': action,
                'results': results,
                'scan_info': {
                    'target': scan.target,
                    'started_at': scan.started_at.isoformat() if scan.started_at else None,
                    'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
                }
            }
        except Exception as e:
            logger.error(f"Error parsing Kerbrute results {scan_id}: {e}")
            return {'scan_id': scan_id, 'error': f'Failed to parse results: {str(e)}'}

