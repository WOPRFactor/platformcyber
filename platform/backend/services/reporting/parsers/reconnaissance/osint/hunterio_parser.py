"""
Hunter.io Parser
================

Parser para Hunter.io - Email finder and verifier.
Formato: JSON con emails, pattern, confidence.
"""

from pathlib import Path
from typing import List
import logging
from ...base_parser import BaseParser, ParsedFinding

logger = logging.getLogger(__name__)


class HunterioParser(BaseParser):
    """Parser para archivos JSON de Hunter.io."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si el archivo puede ser parseado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si puede parsear el archivo
        """
        filename = file_path.name.lower()
        return ('hunter' in filename or 'hunterio' in filename) and file_path.suffix == '.json'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo JSON de Hunter.io.
        
        Formato:
        {
          "data": {
            "domain": "example.com",
            "pattern": "{first}.{last}",
            "emails": [
              {
                "value": "john.doe@example.com",
                "confidence": 95,
                "position": "Software Engineer"
              }
            ]
          }
        }
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings con emails y patterns encontrados
        """
        findings = []
        
        try:
            data = self._safe_parse_json(file_path)
            if not data:
                return findings
            
            data_section = data.get('data', {})
            domain = data_section.get('domain', 'unknown')
            pattern = data_section.get('pattern', 'unknown')
            emails = data_section.get('emails', [])
            
            # Finding por el pattern de emails
            if pattern and pattern != 'unknown':
                finding = ParsedFinding(
                    title=f"Email pattern discovered: {pattern}",
                    severity='info',
                    description=f"Email naming pattern for {domain}: {pattern}",
                    category='osint',
                    affected_target=domain,
                    evidence=f"Pattern: {pattern}",
                    remediation="Consider security awareness training for employees",
                    raw_data={'tool': 'hunterio', 'type': 'pattern', 'pattern': pattern, 'domain': domain}
                )
                findings.append(finding)
            
            # Finding por cada email
            for email_data in emails:
                email = email_data.get('value', '')
                confidence = email_data.get('confidence', 0)
                position = email_data.get('position', '')
                
                # Determinar severidad por confidence
                if confidence >= 90:
                    severity = 'low'  # Alta confianza = más riesgo
                else:
                    severity = 'info'
                
                description = f"Email found: {email}"
                if position:
                    description += f" (Position: {position})"
                description += f" - Confidence: {confidence}%"
                
                finding = ParsedFinding(
                    title=f"Email discovered: {email}",
                    severity=severity,
                    description=description,
                    category='osint',
                    affected_target=email,
                    evidence=f"Confidence: {confidence}%, Position: {position}",
                    remediation="Review email exposure and consider anti-phishing measures",
                    raw_data={
                        'tool': 'hunterio',
                        'type': 'email',
                        'email': email,
                        'confidence': confidence,
                        'position': position
                    }
                )
                findings.append(finding)
            
            logger.info(f"Hunter.io: Parsed {len(findings)} email findings")
            return findings
            
        except Exception as e:
            logger.error(f"Error parsing Hunter.io file {file_path}: {e}")
            return findings


