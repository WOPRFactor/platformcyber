"""
WhatWeb Parser
==============

Parser para WhatWeb - Web technology fingerprinting.
Formato: JSON con plugins detectados (servidor, frameworks, CMS, etc).
"""

from pathlib import Path
from typing import List
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class WhatWebParser(BaseParser):
    """Parser para archivos JSON de WhatWeb."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return 'whatweb' in filename and file_path.suffix == '.json'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo JSON de WhatWeb.
        
        Formato:
        [
          {
            "target": "https://example.com",
            "http_status": 200,
            "plugins": {
              "HTTPServer": {"string": ["nginx/1.18.0"]},
              "X-Powered-By": {"string": ["PHP/7.4.3"]},
              "JQuery": {"version": ["3.5.1"]},
              "Bootstrap": {"version": ["4.5.0"]}
            }
          }
        ]
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con tecnologías detectadas
        """
        findings = []
        
        try:
            data = self._safe_parse_json(file_path)
            if not data or not isinstance(data, list):
                return findings
            
            for entry in data:
                target = entry.get('target', 'unknown')
                http_status = entry.get('http_status', 0)
                plugins = entry.get('plugins', {})
                
                technologies = []
                
                # Extraer tecnologías detectadas
                for plugin_name, plugin_data in plugins.items():
                    if isinstance(plugin_data, dict):
                        # Obtener versión o string
                        version_list = plugin_data.get('version', plugin_data.get('string', []))
                        if version_list:
                            tech_info = f"{plugin_name}: {version_list[0]}"
                            technologies.append(tech_info)
                
                if technologies:
                    # Determinar severidad basado en tecnologías conocidas con vulnerabilidades
                    severity = 'info'
                    vulnerable_techs = []
                    
                    # Check for outdated or vulnerable technologies
                    for tech in technologies:
                        tech_lower = tech.lower()
                        if any(old in tech_lower for old in ['php/5', 'php/7.0', 'php/7.1', 'jquery/1', 'jquery/2']):
                            severity = 'low'
                            vulnerable_techs.append(tech)
                    
                    description = f"Web technologies detected: {', '.join(technologies)}"
                    if vulnerable_techs:
                        description += f" (Potentially outdated: {', '.join(vulnerable_techs)})"
                    
                    finding = ParsedFinding(
                        title=f"Web fingerprinting: {target}",
                        severity=severity,
                        description=description,
                        category='web_reconnaissance',
                        affected_target=target,
                        evidence=f"Technologies: {', '.join(technologies)}",
                        remediation="Update outdated components to latest stable versions" if vulnerable_techs else None,
                        raw_data={
                            'tool': 'whatweb',
                            'target': target,
                            'http_status': http_status,
                            'technologies': technologies,
                            'vulnerable_technologies': vulnerable_techs,
                            'plugins': plugins
                        }
                    )
                    findings.append(finding)
            
            logger.info(f"WhatWeb: Parsed {len(findings)} technology fingerprints")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing WhatWeb file {file_path}: {e}")
            return findings


