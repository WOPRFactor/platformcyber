"""
Amass Parser
============

Parser para archivos JSON de Amass.
Amass genera resultados en formato JSON con información de subdominios.
"""

import json
from pathlib import Path
from typing import List
from ..base_parser import BaseParser, ParsedFinding
from ...config import MAX_FILE_SIZE


class AmassParser(BaseParser):
    """Parser para archivos JSON de Amass."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si es un archivo JSON de Amass.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si es JSON y contiene 'amass' en el nombre
        """
        return (
            file_path.suffix.lower() == '.json' and 
            'amass' in file_path.stem.lower()
        )
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo JSON de Amass.
        
        Amass puede generar JSON con diferentes estructuras:
        - Array de objetos con campos: name, domain, addresses, etc.
        - Objeto con campo 'domains' o 'subdomains'
        
        Args:
            file_path: Ruta al archivo JSON
            
        Returns:
            Lista de ParsedFinding con subdominios encontrados
        """
        findings = []
        
        # Validar tamaño del archivo
        if not self._validate_file_size(file_path, MAX_FILE_SIZE):
            self.logger.warning(f"File {file_path} exceeds max size, skipping")
            return findings
        
        try:
            data = self._safe_parse_json(file_path)
            if not data:
                return findings
            
            # Amass puede tener diferentes estructuras
            subdomains = []
            
            if isinstance(data, list):
                # Array directo de subdominios
                for item in data:
                    if isinstance(item, dict):
                        name = item.get('name') or item.get('domain') or item.get('subdomain')
                        if name:
                            subdomains.append({
                                'name': name,
                                'domain': item.get('domain', ''),
                                'ip': item.get('ip') or (item.get('addresses', [{}])[0].get('ip') if item.get('addresses') else ''),
                                'sources': item.get('sources', [])
                            })
            elif isinstance(data, dict):
                # Objeto con campo 'domains' o 'subdomains'
                if 'domains' in data:
                    subdomains_list = data['domains']
                elif 'subdomains' in data:
                    subdomains_list = data['subdomains']
                else:
                    # Buscar cualquier campo que sea array de strings
                    for key, value in data.items():
                        if isinstance(value, list) and value and isinstance(value[0], str):
                            subdomains_list = value
                            break
                    else:
                        subdomains_list = []
                
                for item in subdomains_list:
                    if isinstance(item, str):
                        subdomains.append({'name': item, 'domain': '', 'ip': '', 'sources': []})
                    elif isinstance(item, dict):
                        name = item.get('name') or item.get('domain') or item.get('subdomain')
                        if name:
                            subdomains.append({
                                'name': name,
                                'domain': item.get('domain', ''),
                                'ip': item.get('ip') or (item.get('addresses', [{}])[0].get('ip') if item.get('addresses') else ''),
                                'sources': item.get('sources', [])
                            })
            
            # Crear findings
            for subdomain_data in subdomains:
                name = subdomain_data['name']
                domain = subdomain_data['domain']
                ip = subdomain_data['ip']
                sources = subdomain_data['sources']
                
                # Construir descripción
                description_parts = [f"Subdomain discovered: {name}"]
                if domain:
                    description_parts.append(f"Domain: {domain}")
                if ip:
                    description_parts.append(f"IP: {ip}")
                if sources:
                    description_parts.append(f"Sources: {', '.join(sources[:3])}")
                description = '. '.join(description_parts)
                
                finding = ParsedFinding(
                    title=f"Subdomain: {name}",
                    severity='info',
                    description=description,
                    category='reconnaissance',
                    affected_target=name,
                    raw_data={
                        'subdomain': name,
                        'domain': domain,
                        'ip': ip,
                        'sources': sources,
                        'tool': 'amass'
                    }
                )
                findings.append(finding)
            
            self.logger.info(f"Parsed {len(findings)} subdomains from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error parsing Amass JSON {file_path}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        return findings
