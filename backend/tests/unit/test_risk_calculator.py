"""
Tests Unitarios - RiskCalculator
=================================

Tests para el calculador de métricas de riesgo.
"""

import pytest
from services.reporting.parsers.base_parser import ParsedFinding
from services.reporting.core.risk_calculator import RiskCalculator


class TestRiskCalculator:
    """Tests para RiskCalculator."""
    
    @pytest.fixture
    def calculator(self):
        """Fixture que retorna instancia de RiskCalculator."""
        return RiskCalculator()
    
    @pytest.fixture
    def sample_consolidated(self):
        """Fixture que retorna findings consolidados de ejemplo."""
        findings = {
            'vulnerability': [
                ParsedFinding("Critical Vuln", "critical", "Desc", "vulnerability", "target"),
                ParsedFinding("High Vuln", "high", "Desc", "vulnerability", "target"),
            ],
            'port_scan': [
                ParsedFinding("Open Port", "low", "Desc", "port_scan", "target"),
            ]
        }
        return findings
    
    def test_calculate_with_findings(self, calculator, sample_consolidated):
        """Test cálculo de riesgo con findings."""
        metrics = calculator.calculate(sample_consolidated)
        
        assert 'risk_score' in metrics
        assert 'risk_level' in metrics
        assert 'total_findings' in metrics
        assert 'severity_distribution' in metrics
        assert isinstance(metrics['risk_score'], float)
        assert 0 <= metrics['risk_score'] <= 10
    
    def test_calculate_empty(self, calculator):
        """Test cálculo de riesgo sin findings."""
        empty = {}
        metrics = calculator.calculate(empty)
        
        assert metrics['risk_score'] == 0.0
        assert metrics['risk_level'] == 'none'
        assert metrics['total_findings'] == 0
    
    def test_calculate_risk_level_critical(self, calculator):
        """Test que risk_level es critical para scores altos."""
        findings = {
            'vulnerability': [
                ParsedFinding("Critical", "critical", "Desc", "vulnerability", "target")
            ] * 5  # Múltiples critical
        }
        
        metrics = calculator.calculate(findings)
        assert metrics['risk_level'] == 'critical'
        assert metrics['risk_score'] >= 7.5
    
    def test_calculate_risk_level_high(self, calculator):
        """Test que risk_level es high para scores medios-altos."""
        findings = {
            'vulnerability': [
                ParsedFinding("High", "high", "Desc", "vulnerability", "target")
            ] * 10  # Múltiples high
        }
        
        metrics = calculator.calculate(findings)
        assert metrics['risk_level'] in ['high', 'critical']
    
    def test_calculate_severity_distribution(self, calculator, sample_consolidated):
        """Test que severity_distribution cuenta correctamente."""
        metrics = calculator.calculate(sample_consolidated)
        
        dist = metrics['severity_distribution']
        assert dist['critical'] == 1
        assert dist['high'] == 1
        assert dist['low'] == 1
    
    def test_calculate_vulnerabilities_only(self, calculator, sample_consolidated):
        """Test que vulnerabilities_only cuenta solo vulnerabilidades."""
        metrics = calculator.calculate(sample_consolidated)
        
        # Debe contar solo los de categoría 'vulnerability'
        assert metrics['vulnerabilities_only'] == 2
    
    def test_assess_risk_level(self, calculator):
        """Test que _assess_risk_level mapea scores correctamente."""
        assert calculator._assess_risk_level(9.0) == 'critical'
        assert calculator._assess_risk_level(7.0) == 'high'
        assert calculator._assess_risk_level(5.0) == 'medium'
        assert calculator._assess_risk_level(3.0) == 'low'
        assert calculator._assess_risk_level(1.0) == 'info'
        assert calculator._assess_risk_level(0.0) == 'none'





