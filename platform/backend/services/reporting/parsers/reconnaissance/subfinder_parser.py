"""
Subfinder Parser
===============

Parser para archivos TXT de Subfinder.
Cada línea contiene un subdominio descubierto.
"""

from pathlib import Path
from typing import List
from ..base_parser import BaseParser, ParsedFinding
from ...config import MAX_FILE_SIZE


class SubfinderParser(BaseParser):
    """Parser para archivos TXT de Subfinder."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si es un archivo TXT de Subfinder.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si es TXT y contiene 'subfinder' en el nombre
        """
        return (
            file_path.suffix.lower() == '.txt' and 
            'subfinder' in file_path.stem.lower()
        )
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo TXT de Subfinder (un dominio por línea).
        
        Args:
            file_path: Ruta al archivo TXT
            
        Returns:
            Lista de ParsedFinding con subdominios encontrados
        """
        findings = []
        
        # Validar tamaño del archivo
        if not self._validate_file_size(file_path, MAX_FILE_SIZE):
            self.logger.warning(f"File {file_path} exceeds max size, skipping")
            return findings
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            # Extraer dominios (un dominio por línea)
            subdomains = [
                line.strip() 
                for line in content.split('\n') 
                if line.strip() and not line.startswith('#')
            ]
            
            for subdomain in subdomains:
                # Validación básica de formato de dominio
                if '.' not in subdomain:
                    continue
                
                finding = ParsedFinding(
                    title=f"Subdomain: {subdomain}",
                    severity='info',
                    description="Discovered subdomain through reconnaissance",
                    category='reconnaissance',
                    affected_target=subdomain,
                    raw_data={'subdomain': subdomain, 'tool': 'subfinder'}
                )
                findings.append(finding)
            
            self.logger.info(f"Parsed {len(findings)} subdomains from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error parsing Subfinder TXT {file_path}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        return findings
