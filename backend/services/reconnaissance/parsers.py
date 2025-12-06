"""
Result Parsers Module
====================

Módulo para parsear resultados de escaneos de reconocimiento.
"""

import json
import logging
from typing import Dict, Any
from pathlib import Path

from utils.parsers.recon_parser import ReconParser
from .base import BaseReconnaissanceService

logger = logging.getLogger(__name__)


class ResultParsersService(BaseReconnaissanceService):
    """Servicio para parsear resultados de escaneos."""
    
    def __init__(self, scan_repository=None):
        """Inicializa el servicio con parser."""
        super().__init__(scan_repository)
        self.parser = ReconParser()
    
    def get_scan_results(self, scan_id: int) -> Dict[str, Any]:
        """
        Obtiene y parsea resultados de un scan.
        
        Args:
            scan_id: ID del escaneo
        
        Returns:
            Dict con resultados parseados
        """
        scan = self.scan_repo.find_by_id(scan_id)
        
        if not scan:
            raise ValueError(f'Scan {scan_id} not found')
        
        if scan.status != 'completed':
            return {
                'scan_id': scan_id,
                'status': scan.status,
                'message': 'Scan not completed yet'
            }
        
        tool = scan.options.get('tool')
        recon_type = scan.options.get('recon_type')
        
        output_file = self._get_output_file(scan_id, tool)
        
        if not output_file.exists():
            return {
                'scan_id': scan_id,
                'error': 'Output file not found'
            }
        
        try:
            with open(output_file, 'r') as f:
                content = f.read()
            
            results = self._parse_by_tool(tool, content, output_file)
            
            return {
                'scan_id': scan_id,
                'status': 'completed',
                'tool': tool,
                'recon_type': recon_type,
                'results': results,
                'scan_info': {
                    'target': scan.target,
                    'started_at': scan.started_at.isoformat() if scan.started_at else None,
                    'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing results for scan {scan_id}: {e}")
            return {
                'scan_id': scan_id,
                'error': f'Failed to parse results: {str(e)}'
            }
    
    def _parse_by_tool(self, tool: str, content: str, output_file: Path) -> Dict[str, Any]:
        """Parsea resultados según la herramienta."""
        if tool == 'whois':
            return {
                'tool': 'whois',
                'output': content,
                'lines': len(content.split('\n'))
            }
        elif tool in ['subfinder', 'assetfinder', 'sublist3r']:
            return self.parser.parse_subfinder(content)
        elif tool == 'amass':
            return self.parser.parse_amass(content)
        elif tool == 'theHarvester':
            return self.parser.parse_theharvester(str(output_file))
        elif tool in ['katana', 'gospider', 'hakrawler']:
            return self.parser.parse_katana(content)
        elif tool == 'dnsrecon':
            return self.parser.parse_dnsrecon(content)
        elif tool == 'waybackurls':
            return self.parser.parse_waybackurls(content)
        elif tool == 'shodan':
            return self.parser.parse_shodan(content)
        elif tool in ['gitleaks', 'trufflehog']:
            return self.parser.parse_gitleaks(content)
        elif tool == 'crtsh':
            subdomains = [line.strip() for line in content.split('\n') if line.strip()]
            return {
                'subdomains': subdomains,
                'total': len(subdomains)
            }
        elif tool == 'findomain':
            subdomains = [line.strip() for line in content.split('\n') if line.strip()]
            return {
                'subdomains': subdomains,
                'total': len(subdomains)
            }
        elif tool == 'censys':
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {'raw_output': content}
        elif tool in ['host', 'nslookup']:
            return {
                'output': content,
                'lines': len(content.split('\n'))
            }
        elif tool == 'traceroute':
            return {
                'output': content,
                'lines': len(content.split('\n'))
            }
        elif tool in ['dnsenum', 'fierce']:
            return self.parser.parse_dnsrecon(content)
        else:
            return {'raw_output': content}
