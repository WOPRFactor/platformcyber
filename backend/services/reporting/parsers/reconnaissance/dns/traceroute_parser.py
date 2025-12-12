"""
Traceroute Parser
==================

Parser para Traceroute - Network path tracing.
Formato: TXT con saltos (hops), línea por salto.
"""

from pathlib import Path
from typing import List
import re
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class TracerouteParser(BaseParser):
    """Parser para archivos de Traceroute."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return 'traceroute' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de Traceroute.
        
        Formato:
        traceroute to example.com (192.0.2.1), 30 hops max
         1  192.168.0.1 (192.168.0.1)  5.203 ms
         2  10.42.64.1 (10.42.64.1)  9.512 ms
         5  * * *
        16  vps-123.example.com (192.0.2.1)  151.231 ms
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con saltos de red encontrados
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            target_domain = None
            target_ip = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Primera línea: traceroute to example.com (192.0.2.1)
                if line.startswith('traceroute to'):
                    match = re.search(r'traceroute to ([\w\.\-]+) \(([\d\.]+)\)', line)
                    if match:
                        target_domain = match.group(1)
                        target_ip = match.group(2)
                    continue
                
                # Saltos: formato " 1  192.168.0.1 (192.168.0.1)  5.203 ms"
                match = re.search(r'^\s*(\d+)\s+([\w\.\-]+)\s+\(([\d\.]+)\)\s+([\d\.]+)\s*ms', line)
                if match:
                    hop_number = int(match.group(1))
                    hostname = match.group(2)
                    ip = match.group(3)
                    latency = float(match.group(4))
                    
                    finding = ParsedFinding(
                        title=f"Traceroute hop {hop_number}: {hostname}",
                        severity='info',
                        description=f"Network hop: {hostname} ({ip}) - {latency}ms",
                        category='reconnaissance',
                        affected_target=hostname,
                        evidence=f"Hop: {hop_number}, IP: {ip}, Latency: {latency}ms",
                        raw_data={
                            'tool': 'traceroute',
                            'hop': hop_number,
                            'hostname': hostname,
                            'ip': ip,
                            'latency_ms': latency,
                            'target_domain': target_domain,
                            'target_ip': target_ip
                        }
                    )
                    findings.append(finding)
                
                # Timeouts: " 5  * * *"
                elif re.search(r'^\s*(\d+)\s+\*\s+\*\s+\*', line):
                    hop_number = int(re.search(r'^\s*(\d+)', line).group(1))
                    finding = ParsedFinding(
                        title=f"Traceroute hop {hop_number}: Timeout",
                        severity='info',
                        description=f"Hop {hop_number} timed out (filtered or unreachable)",
                        category='reconnaissance',
                        affected_target=target_domain or 'unknown',
                        evidence="No response received",
                        raw_data={
                            'tool': 'traceroute',
                            'hop': hop_number,
                            'status': 'timeout'
                        }
                    )
                    findings.append(finding)
            
            logger.info(f"Traceroute: Parsed {len(findings)} hops")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing Traceroute file {file_path}: {e}")
            return findings


