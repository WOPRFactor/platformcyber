"""
Risk Calculator
===============

Calcula métricas de riesgo basadas en findings.
Genera risk score (0-10) y nivel de riesgo categórico.
"""

from typing import Dict, List
from ..parsers.base_parser import ParsedFinding
import logging
import math


class RiskCalculator:
    """
    Calcula métricas de riesgo basadas en findings.
    
    Utiliza una fórmula ponderada que considera:
    - Cantidad de findings por severidad
    - Escala logarítmica para evitar saturación
    - Ajustes específicos para casos críticos
    """
    
    # Pesos por severidad (para cálculo de risk score)
    SEVERITY_WEIGHTS = {
        'critical': 10.0,
        'high': 7.5,
        'medium': 5.0,
        'low': 2.5,
        'info': 0.5
    }
    
    def __init__(self):
        """Inicializa el calculador con logger."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def calculate(
        self, 
        consolidated: Dict[str, List[ParsedFinding]]
    ) -> Dict:
        """
        Calcula métricas de riesgo.
        
        Args:
            consolidated: Findings consolidados por categoría
            
        Returns:
            Dict con métricas: risk_score, risk_level, severity_distribution
        """
        # Obtener todos los findings
        all_findings = []
        for findings in consolidated.values():
            all_findings.extend(findings)
        
        if not all_findings:
            return {
                'risk_score': 0.0,
                'risk_level': 'none',
                'total_findings': 0,
                'severity_distribution': {
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0,
                    'info': 0
                }
            }
        
        # Contar por severidad
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        for finding in all_findings:
            severity = finding.severity.lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Calcular risk score (0-10)
        risk_score = self._calculate_risk_score(severity_counts)
        risk_level = self._assess_risk_level(risk_score)
        
        self.logger.info(f"Risk Score: {risk_score:.2f} ({risk_level})")
        
        return {
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'total_findings': len(all_findings),
            'severity_distribution': severity_counts,
            'vulnerabilities_only': sum(
                1 for f in all_findings 
                if f.category in ['vulnerability', 'web_vulnerability']
            )
        }
    
    def _calculate_risk_score(
        self, 
        severity_counts: Dict[str, int]
    ) -> float:
        """
        Calcula risk score ponderado (0-10).
        
        Fórmula:
        - Usa pesos por severidad
        - Escala logarítmica para evitar saturación
        - Ajustes específicos para casos críticos
        
        Args:
            severity_counts: Diccionario con conteos por severidad
            
        Returns:
            Risk score entre 0.0 y 10.0
        """
        # Score ponderado
        weighted_sum = 0.0
        for severity, count in severity_counts.items():
            weight = self.SEVERITY_WEIGHTS.get(severity, 0)
            # Usar logaritmo para reducir impacto de muchos findings
            weighted_sum += weight * math.log1p(count)
        
        # Normalizar a escala 0-10
        # Valor máximo teórico: 100 critical = ~46, normalizar a 10
        max_theoretical = 50.0
        risk_score = min(10.0, (weighted_sum / max_theoretical) * 10)
        
        # Ajustes específicos
        if severity_counts['critical'] > 0:
            # Al menos 7.5 si hay critical, pero si hay múltiples critical subir más
            min_score = 7.5 if severity_counts['critical'] == 1 else 8.5
            risk_score = max(min_score, risk_score)
        elif severity_counts['high'] > 5:
            # Al menos 6.0 si hay muchos high
            risk_score = max(6.0, risk_score)
        
        return risk_score
    
    def _assess_risk_level(self, risk_score: float) -> str:
        """
        Convierte risk score numérico a nivel categórico.
        
        Args:
            risk_score: Score numérico entre 0.0 y 10.0
            
        Returns:
            Nivel de riesgo: critical, high, medium, low, info, none
        """
        if risk_score >= 8.0:
            return 'critical'
        elif risk_score >= 6.0:
            return 'high'
        elif risk_score >= 4.0:
            return 'medium'
        elif risk_score >= 2.0:
            return 'low'
        elif risk_score > 0.0:
            return 'info'
        else:
            return 'none'
