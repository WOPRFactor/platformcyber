"""
WHOIS Parser
============

Parser para WHOIS - Domain registration information.
Formato: TXT con campos clave-valor.
"""

from pathlib import Path
from typing import List
import re
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class WhoisParser(BaseParser):
    """Parser para archivos de WHOIS."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return 'whois' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo WHOIS.
        
        Formato:
        Domain Name: EXAMPLE.TECH
        Creation Date: 2020-06-24T10:15:05.0Z
        Registry Expiry Date: 2026-06-24T23:59:59.0Z
        Registrar: Example Registrar
        Name Server: NS1.EXAMPLE.COM
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con información del dominio
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            
            whois_data = {}
            domain_name = None
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('%') or line.startswith('#'):
                    continue
                
                # Parsear campos clave: valor
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        whois_data[key] = value
                        
                        # Capturar domain name
                        if 'Domain Name' in key and not domain_name:
                            domain_name = value.lower()
            
            if not domain_name:
                domain_name = 'unknown'
            
            # Extraer información relevante
            creation_date = whois_data.get('Creation Date', whois_data.get('Created Date', 'N/A'))
            expiry_date = whois_data.get('Registry Expiry Date', whois_data.get('Expiry Date', 'N/A'))
            registrar = whois_data.get('Registrar', 'N/A')
            name_servers = [v for k, v in whois_data.items() if 'Name Server' in k]
            
            # Crear finding principal con info del dominio
            description = f"Domain: {domain_name}"
            if creation_date != 'N/A':
                description += f" | Created: {creation_date}"
            if expiry_date != 'N/A':
                description += f" | Expires: {expiry_date}"
            if registrar != 'N/A':
                description += f" | Registrar: {registrar}"
            
            evidence_parts = []
            if name_servers:
                evidence_parts.append(f"Name Servers: {', '.join(name_servers)}")
            
            finding = ParsedFinding(
                title=f"WHOIS information: {domain_name}",
                severity='info',
                description=description,
                category='reconnaissance',
                affected_target=domain_name,
                evidence=' | '.join(evidence_parts) if evidence_parts else None,
                raw_data={
                    'tool': 'whois',
                    'domain': domain_name,
                    'creation_date': creation_date,
                    'expiry_date': expiry_date,
                    'registrar': registrar,
                    'name_servers': name_servers,
                    'full_data': whois_data
                }
            )
            findings.append(finding)
            
            logger.info(f"WHOIS: Parsed information for {domain_name}")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing WHOIS file {file_path}: {e}")
            return findings


