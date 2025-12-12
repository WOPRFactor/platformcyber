"""
Tests Unitarios - NiktoParser
==============================

Tests para el parser de archivos JSON de Nikto.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.vulnerability.nikto_parser import NiktoParser


class TestNiktoParser:
    """Tests para NiktoParser."""
    
    @pytest.fixture
    def parser(self):
        """Fixture que retorna instancia de NiktoParser."""
        return NiktoParser()
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Fixture que crea archivo JSON de Nikto de ejemplo."""
        sample_path = Path(__file__).parent.parent / "fixtures" / "nikto_sample.json"
        if sample_path.exists():
            return sample_path
        
        # Si no existe el fixture, crear uno básico
        test_file = tmp_path / "nikto_test.json"
        test_file.write_text("""[{"host":"example.com","ip":"192.168.1.100","port":80,"vulnerabilities":[{"OSVDB":"12345","msg":"Test vulnerability","method":"GET","url":"/"}]}]""")
        return test_file
    
    def test_can_parse_nikto_json(self, parser, tmp_path):
        """Test que can_parse identifica archivos JSON de Nikto."""
        nikto_file = tmp_path / "nikto_123.json"
        nikto_file.touch()
        
        assert parser.can_parse(nikto_file) is True
    
    def test_can_parse_non_nikto_json(self, parser, tmp_path):
        """Test que can_parse rechaza JSON que no es de Nikto."""
        other_file = tmp_path / "other.json"
        other_file.touch()
        
        assert parser.can_parse(other_file) is False
    
    def test_can_parse_non_json(self, parser, tmp_path):
        """Test que can_parse rechaza archivos no JSON."""
        txt_file = tmp_path / "nikto_123.txt"
        txt_file.touch()
        
        assert parser.can_parse(txt_file) is False
    
    def test_parse_nikto_json(self, parser, sample_file):
        """Test parsing de archivo JSON de Nikto válido."""
        findings = parser.parse(sample_file)
        
        assert len(findings) > 0
        assert all(f.category == 'web_vulnerability' for f in findings)
        assert all(f.affected_target for f in findings)
    
    def test_parse_empty_file(self, parser, tmp_path):
        """Test parsing de archivo vacío."""
        empty_file = tmp_path / "nikto_empty.json"
        empty_file.write_text("")
        
        findings = parser.parse(empty_file)
        assert findings == []
    
    def test_parse_invalid_json(self, parser, tmp_path):
        """Test parsing de JSON malformado."""
        invalid_file = tmp_path / "nikto_invalid.json"
        invalid_file.write_text("{invalid json}")
        
        findings = parser.parse(invalid_file)
        assert findings == []
    
    def test_parse_single_scan(self, parser, tmp_path):
        """Test parsing de un solo scan (dict en lugar de array)."""
        test_file = tmp_path / "nikto_single.json"
        test_file.write_text("""{"host":"example.com","port":80,"vulnerabilities":[{"OSVDB":"12345","msg":"Test","method":"GET","url":"/"}]}""")
        
        findings = parser.parse(test_file)
        assert len(findings) == 1
    
    def test_parse_severity_assignment(self, parser, tmp_path):
        """Test que se asigna severidad según palabras clave."""
        test_file = tmp_path / "nikto_severity.json"
        test_file.write_text("""[{"host":"example.com","port":80,"vulnerabilities":[
            {"OSVDB":"1","msg":"SQL injection vulnerability","method":"GET","url":"/"},
            {"OSVDB":"2","msg":"XSS vulnerability detected","method":"GET","url":"/"},
            {"OSVDB":"3","msg":"Information disclosure","method":"GET","url":"/"},
            {"OSVDB":"4","msg":"Default page found","method":"GET","url":"/"}
        ]}]""")
        
        findings = parser.parse(test_file)
        severities = [f.severity for f in findings]
        
        assert 'critical' in severities  # SQL injection
        assert 'high' in severities  # XSS
        assert 'medium' in severities  # Information disclosure
        assert 'low' in severities  # Default page
    
    def test_parse_extracts_osvdb(self, parser, tmp_path):
        """Test que se extrae OSVDB correctamente."""
        test_file = tmp_path / "nikto_osvdb.json"
        test_file.write_text("""[{"host":"example.com","port":80,"vulnerabilities":[{"OSVDB":"12345","msg":"Test","method":"GET","url":"/"}]}]""")
        
        findings = parser.parse(test_file)
        assert len(findings) == 1
        assert "OSVDB-12345" in findings[0].references
    
    def test_parse_findings_structure(self, parser, sample_file):
        """Test que los findings tienen la estructura correcta."""
        findings = parser.parse(sample_file)
        
        if findings:
            finding = findings[0]
            assert hasattr(finding, 'title')
            assert hasattr(finding, 'severity')
            assert hasattr(finding, 'description')
            assert hasattr(finding, 'category')
            assert hasattr(finding, 'affected_target')
            assert 'host' in finding.raw_data
            assert 'port' in finding.raw_data





