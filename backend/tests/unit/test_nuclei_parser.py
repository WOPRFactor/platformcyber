"""
Tests Unitarios - NucleiParser
===============================

Tests para el parser de archivos JSONL de Nuclei.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.vulnerability.nuclei_parser import NucleiParser


class TestNucleiParser:
    """Tests para NucleiParser."""
    
    @pytest.fixture
    def parser(self):
        """Fixture que retorna instancia de NucleiParser."""
        return NucleiParser()
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Fixture que crea archivo JSONL de Nuclei de ejemplo."""
        sample_path = Path(__file__).parent.parent / "fixtures" / "nuclei_sample.jsonl"
        if sample_path.exists():
            return sample_path
        
        # Si no existe el fixture, crear uno básico
        test_file = tmp_path / "nuclei_test.jsonl"
        test_file.write_text("""{"template-id":"test-template","info":{"name":"Test Vulnerability","severity":"high","description":"Test description"},"host":"https://example.com","matched-at":"https://example.com/test"}""")
        return test_file
    
    def test_can_parse_nuclei_jsonl(self, parser, tmp_path):
        """Test que can_parse identifica archivos JSONL de Nuclei."""
        nuclei_file = tmp_path / "nuclei_123.jsonl"
        nuclei_file.touch()
        
        assert parser.can_parse(nuclei_file) is True
    
    def test_can_parse_non_nuclei_jsonl(self, parser, tmp_path):
        """Test que can_parse rechaza JSONL que no es de Nuclei."""
        other_file = tmp_path / "other.jsonl"
        other_file.touch()
        
        assert parser.can_parse(other_file) is False
    
    def test_can_parse_non_jsonl(self, parser, tmp_path):
        """Test que can_parse rechaza archivos no JSONL."""
        txt_file = tmp_path / "nuclei_123.txt"
        txt_file.touch()
        
        assert parser.can_parse(txt_file) is False
    
    def test_parse_nuclei_jsonl(self, parser, sample_file):
        """Test parsing de archivo JSONL de Nuclei válido."""
        findings = parser.parse(sample_file)
        
        assert len(findings) > 0
        assert all(f.category == 'vulnerability' for f in findings)
        assert all(f.affected_target for f in findings)
    
    def test_parse_empty_file(self, parser, tmp_path):
        """Test parsing de archivo vacío."""
        empty_file = tmp_path / "nuclei_empty.jsonl"
        empty_file.write_text("")
        
        findings = parser.parse(empty_file)
        assert findings == []
    
    def test_parse_invalid_json_line(self, parser, tmp_path):
        """Test parsing con línea JSON inválida."""
        invalid_file = tmp_path / "nuclei_invalid.jsonl"
        invalid_file.write_text("""{"valid": "json"}
{invalid json}
{"another": "valid"}""")
        
        findings = parser.parse(invalid_file)
        # Debe parsear las líneas válidas e ignorar la inválida
        assert len(findings) == 2
    
    def test_parse_severity_mapping(self, parser, tmp_path):
        """Test que se mapean severidades correctamente."""
        test_file = tmp_path / "nuclei_severity.jsonl"
        test_file.write_text("""{"template-id":"test","info":{"severity":"critical"},"host":"test"}
{"template-id":"test","info":{"severity":"high"},"host":"test"}
{"template-id":"test","info":{"severity":"medium"},"host":"test"}
{"template-id":"test","info":{"severity":"low"},"host":"test"}
{"template-id":"test","info":{"severity":"info"},"host":"test"}""")
        
        findings = parser.parse(test_file)
        severities = [f.severity for f in findings]
        
        assert 'critical' in severities
        assert 'high' in severities
        assert 'medium' in severities
        assert 'low' in severities
        assert 'info' in severities
    
    def test_parse_extracts_cve(self, parser, tmp_path):
        """Test que se extrae CVE de referencias."""
        test_file = tmp_path / "nuclei_cve.jsonl"
        test_file.write_text("""{"template-id":"test","info":{"severity":"critical","reference":["https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-12345"]},"host":"test"}""")
        
        findings = parser.parse(test_file)
        assert len(findings) == 1
        assert findings[0].cve_id == "CVE-2021-12345"
    
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





