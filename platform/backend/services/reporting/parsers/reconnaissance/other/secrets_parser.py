"""
Secrets Detection Parser
========================

Parser para Secrets Detection (Gitleaks, Trufflehog) - Exposed secrets.
Formato: JSON con secrets encontrados (API keys, passwords, tokens).
"""

from pathlib import Path
from typing import List
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class SecretsParser(BaseParser):
    """Parser para archivos de herramientas de detección de secretos."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return (('gitleaks' in filename or 'trufflehog' in filename or 'secret' in filename) 
                and file_path.suffix == '.json')
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo JSON de Gitleaks/Trufflehog.
        
        Formato:
        [
          {
            "Description": "AWS Access Key",
            "Match": "AKIAIOSFODNN7EXAMPLE",
            "File": "config/aws.js",
            "StartLine": 15,
            "RuleID": "aws-access-token",
            "Entropy": 4.5
          }
        ]
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con secretos expuestos encontrados
        """
        findings = []
        
        try:
            data = self._safe_parse_json(file_path)
            if not data or not isinstance(data, list):
                return findings
            
            for secret in data:
                description = secret.get('Description', 'Secret detected')
                match_value = secret.get('Match', '')
                file_path_str = secret.get('File', 'unknown')
                start_line = secret.get('StartLine', 0)
                rule_id = secret.get('RuleID', 'unknown')
                entropy = secret.get('Entropy', 0)
                
                # Determinar severidad basado en tipo de secreto
                description_lower = description.lower()
                if any(kw in description_lower for kw in ['password', 'api key', 'access key', 
                                                          'secret key', 'private key']):
                    severity = 'critical'
                elif any(kw in description_lower for kw in ['token', 'credential']):
                    severity = 'high'
                else:
                    severity = 'medium'
                
                # Ocultar parte del secret (security)
                if match_value and len(match_value) > 10:
                    masked_value = match_value[:4] + '...' + match_value[-4:]
                else:
                    masked_value = '***'
                
                finding = ParsedFinding(
                    title=f"Exposed secret: {description}",
                    severity=severity,
                    description=f"Secret detected in {file_path_str} (line {start_line}): {description}",
                    category='secrets_exposure',
                    affected_target=file_path_str,
                    evidence=f"Rule: {rule_id}, Entropy: {entropy}, Value: {masked_value}",
                    remediation="IMMEDIATE: Rotate exposed credentials and remove from code/repository",
                    raw_data={
                        'tool': 'secrets_detection',
                        'description': description,
                        'file': file_path_str,
                        'line': start_line,
                        'rule_id': rule_id,
                        'entropy': entropy,
                        'match_length': len(match_value)
                    }
                )
                findings.append(finding)
            
            logger.info(f"SecretsDetection: Parsed {len(findings)} exposed secrets")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing Secrets file {file_path}: {e}")
            return findings


