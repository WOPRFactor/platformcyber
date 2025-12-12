"""
Tests Unitarios - SubfinderParser
==================================

Tests para el parser de archivos TXT de Subfinder.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.reconnaissance.subfinder_parser import SubfinderParser


class TestSubfinderParser:
    """Tests para SubfinderParser."""
    
    @pytest.fixture
    def parser(self):
        """Fixture que retorna instancia de SubfinderParser."""
        return SubfinderParser()
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Fixture que crea archivo TXT de Subfinder de ejemplo."""
        sample_path = Path(__file__).parent.parent / "fixtures" / "subfinder_sample.txt"
        if sample_path.exists():
            return sample_path
        
        # Si no existe el fixture, crear uno básico
        test_file = tmp_path / "subfinder_test.txt"
        test_file.write_text("""subdomain1.example.com
subdomain2.example.com
www.example.com""")
        return test_file
    
    def test_can_parse_subfinder_txt(self, parser, tmp_path):
        """Test que can_parse identifica archivos TXT de Subfinder."""
        subfinder_file = tmp_path / "subfinder_123.txt"
        subfinder_file.touch()
        
        assert parser.can_parse(subfinder_file) is True
    
    def test_can_parse_non_subfinder_txt(self, parser, tmp_path):
        """Test que can_parse rechaza TXT que no es de Subfinder."""
        other_file = tmp_path / "other.txt"
        other_file.touch()
        
        assert parser.can_parse(other_file) is False
    
    def test_can_parse_non_txt(self, parser, tmp_path):
        """Test que can_parse rechaza archivos no TXT."""
        xml_file = tmp_path / "subfinder_123.xml"
        xml_file.touch()
        
        assert parser.can_parse(xml_file) is False
    
    def test_parse_subfinder_txt(self, parser, sample_file):
        """Test parsing de archivo TXT de Subfinder válido."""
        findings = parser.parse(sample_file)
        
        assert len(findings) > 0
        assert all(f.category == 'reconnaissance' for f in findings)
        assert all(f.severity == 'info' for f in findings)
        assert all(f.affected_target for f in findings)
    
    def test_parse_empty_file(self, parser, tmp_path):
        """Test parsing de archivo vacío."""
        empty_file = tmp_path / "subfinder_empty.txt"
        empty_file.write_text("")
        
        findings = parser.parse(empty_file)
        assert findings == []
    
    def test_parse_ignores_comments(self, parser, tmp_path):
        """Test que se ignoran líneas de comentario."""
        test_file = tmp_path / "subfinder_comments.txt"
        test_file.write_text("""subdomain1.example.com
# Este es un comentario
subdomain2.example.com
# Otro comentario""")
        
        findings = parser.parse(test_file)
        assert len(findings) == 2
    
    def test_parse_ignores_empty_lines(self, parser, tmp_path):
        """Test que se ignoran líneas vacías."""
        test_file = tmp_path / "subfinder_empty_lines.txt"
        test_file.write_text("""subdomain1.example.com

subdomain2.example.com

subdomain3.example.com""")
        
        findings = parser.parse(test_file)
        assert len(findings) == 3
    
    def test_parse_validates_domain_format(self, parser, tmp_path):
        """Test que se valida formato de dominio básico."""
        test_file = tmp_path / "subfinder_invalid.txt"
        test_file.write_text("""valid.example.com
invalid_domain
another.valid.com
not_a_domain""")
        
        findings = parser.parse(test_file)
        # Solo debe parsear dominios válidos (con punto)
        assert len(findings) == 2
    
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
            assert 'subdomain' in finding.raw_data





