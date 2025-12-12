"""
Tests Unitarios - DataAggregator
=================================

Tests para el agregador y deduplicador de findings.
"""

import pytest
from services.reporting.parsers.base_parser import ParsedFinding
from services.reporting.core.data_aggregator import DataAggregator


class TestDataAggregator:
    """Tests para DataAggregator."""
    
    @pytest.fixture
    def aggregator(self):
        """Fixture que retorna instancia de DataAggregator."""
        return DataAggregator()
    
    @pytest.fixture
    def sample_findings(self):
        """Fixture que retorna findings de ejemplo."""
        return [
            ParsedFinding(
                title="Test Finding 1",
                severity="high",
                description="Description 1",
                category="vulnerability",
                affected_target="example.com"
            ),
            ParsedFinding(
                title="Test Finding 2",
                severity="medium",
                description="Description 2",
                category="port_scan",
                affected_target="example.com"
            ),
            ParsedFinding(
                title="Test Finding 1",  # Duplicado
                severity="high",
                description="Description 1",
                category="vulnerability",
                affected_target="example.com"
            ),
        ]
    
    def test_consolidate_groups_by_category(self, aggregator, sample_findings):
        """Test que consolidate agrupa findings por categoría."""
        consolidated = aggregator.consolidate(sample_findings)
        
        assert 'vulnerability' in consolidated
        assert 'port_scan' in consolidated
        assert len(consolidated['vulnerability']) == 1  # Después de deduplicación
        assert len(consolidated['port_scan']) == 1
    
    def test_consolidate_deduplicates(self, aggregator, sample_findings):
        """Test que consolidate deduplica findings similares."""
        consolidated = aggregator.consolidate(sample_findings)
        
        # Debe haber 2 findings únicos (el duplicado se elimina)
        total = sum(len(f) for f in consolidated.values())
        assert total == 2
    
    def test_consolidate_sorts_by_severity(self, aggregator):
        """Test que consolidate ordena por severidad."""
        findings = [
            ParsedFinding("Low", "low", "Desc", "test", "target"),
            ParsedFinding("Critical", "critical", "Desc", "test", "target"),
            ParsedFinding("High", "high", "Desc", "test", "target"),
            ParsedFinding("Medium", "medium", "Desc", "test", "target"),
        ]
        
        consolidated = aggregator.consolidate(findings)
        sorted_findings = consolidated['test']
        
        assert sorted_findings[0].severity == 'critical'
        assert sorted_findings[1].severity == 'high'
        assert sorted_findings[2].severity == 'medium'
        assert sorted_findings[3].severity == 'low'
    
    def test_get_statistics(self, aggregator, sample_findings):
        """Test que get_statistics calcula estadísticas correctas."""
        consolidated = aggregator.consolidate(sample_findings)
        stats = aggregator.get_statistics(consolidated)
        
        assert stats['total_findings'] == 2  # Después de deduplicación
        assert 'by_severity' in stats
        assert 'by_category' in stats
        assert 'unique_targets' in stats
        assert stats['by_severity']['high'] == 1
        assert stats['by_severity']['medium'] == 1
    
    def test_get_statistics_empty(self, aggregator):
        """Test que get_statistics maneja findings vacíos."""
        consolidated = {}
        stats = aggregator.get_statistics(consolidated)
        
        assert stats['total_findings'] == 0
        assert stats['unique_targets'] == 0
    
    def test_deduplicate_case_insensitive(self, aggregator):
        """Test que deduplicación es case-insensitive."""
        findings = [
            ParsedFinding("Test", "high", "Desc", "test", "Example.com"),
            ParsedFinding("test", "high", "Desc", "test", "example.com"),  # Mismo pero diferente case
        ]
        
        consolidated = aggregator.consolidate(findings)
        total = sum(len(f) for f in consolidated.values())
        
        # Debe deduplicar (case-insensitive)
        assert total == 1





