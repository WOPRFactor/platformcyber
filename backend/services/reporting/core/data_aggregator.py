"""
Data Aggregator
===============

Consolida y deduplica findings de múltiples parsers.
Agrupa por categoría y ordena por severidad.
"""

from typing import List, Dict
from ..parsers.base_parser import ParsedFinding
import logging


class DataAggregator:
    """
    Consolida y deduplica findings de múltiples parsers.
    
    Procesa una lista de findings y:
    1. Deduplica findings similares
    2. Agrupa por categoría
    3. Ordena por severidad
    """
    
    def __init__(self):
        """Inicializa el agregador con logger."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def consolidate(
        self, 
        findings: List[ParsedFinding]
    ) -> Dict[str, List[ParsedFinding]]:
        """
        Consolida findings por categoría y deduplica.
        
        Args:
            findings: Lista de todos los findings parseados
            
        Returns:
            Diccionario organizado por categoría con findings ordenados
        """
        self.logger.info(f"Consolidating {len(findings)} findings")
        
        # Deduplicar primero
        deduplicated = self._deduplicate(findings)
        self.logger.info(
            f"After deduplication: {len(deduplicated)} findings"
        )
        
        # Agrupar por categoría
        by_category = {}
        for finding in deduplicated:
            category = finding.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(finding)
        
        # Ordenar cada categoría por severidad (critical primero)
        severity_order = {
            'critical': 0, 
            'high': 1, 
            'medium': 2, 
            'low': 3, 
            'info': 4
        }
        
        for category in by_category:
            by_category[category].sort(
                key=lambda f: (
                    severity_order.get(f.severity.lower(), 999),
                    f.title
                )
            )
        
        self.logger.info(
            f"Consolidated into {len(by_category)} categories"
        )
        
        return by_category
    
    def _deduplicate(
        self, 
        findings: List[ParsedFinding]
    ) -> List[ParsedFinding]:
        """
        Deduplica findings similares.
        
        Criterio de deduplicación:
        - Mismo título (case-insensitive)
        - Misma severidad
        - Mismo target (case-insensitive)
        
        Args:
            findings: Lista de findings a deduplicar
            
        Returns:
            Lista de findings sin duplicados
        """
        seen = set()
        deduplicated = []
        
        for finding in findings:
            # Crear clave única para deduplicación
            key = (
                finding.title.lower().strip(),
                finding.severity.lower(),
                finding.affected_target.lower().strip()
            )
            
            if key not in seen:
                seen.add(key)
                deduplicated.append(finding)
        
        duplicates_removed = len(findings) - len(deduplicated)
        if duplicates_removed > 0:
            self.logger.info(
                f"Removed {duplicates_removed} duplicate findings"
            )
        
        return deduplicated
    
    def get_statistics(
        self, 
        consolidated: Dict[str, List[ParsedFinding]]
    ) -> Dict:
        """
        Calcula estadísticas de los findings consolidados.
        
        Args:
            consolidated: Findings organizados por categoría
            
        Returns:
            Dict con estadísticas: totales, por severidad, por categoría
        """
        all_findings = []
        for findings in consolidated.values():
            all_findings.extend(findings)
        
        # Por severidad
        by_severity = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        for finding in all_findings:
            severity = finding.severity.lower()
            if severity in by_severity:
                by_severity[severity] += 1
        
        # Por categoría
        by_category = {
            category: len(findings)
            for category, findings in consolidated.items()
        }
        
        # Targets únicos
        unique_targets = set(f.affected_target for f in all_findings)
        
        return {
            'total_findings': len(all_findings),
            'by_severity': by_severity,
            'by_category': by_category,
            'unique_targets': len(unique_targets),
            'targets': list(unique_targets)
        }
