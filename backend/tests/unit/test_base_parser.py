"""
Tests Unitarios - BaseParser
============================

Tests para la clase base BaseParser y ParsedFinding.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.base_parser import BaseParser, ParsedFinding


class TestParsedFinding:
    """Tests para el dataclass ParsedFinding."""
    
    def test_parsed_finding_creation(self):
        """Test creación básica de ParsedFinding."""
        finding = ParsedFinding(
            title="Test Finding",
            severity="high",
            description="Test description",
            category="test",
            affected_target="example.com"
        )
        
        assert finding.title == "Test Finding"
        assert finding.severity == "high"
        assert finding.description == "Test description"
        assert finding.category == "test"
        assert finding.affected_target == "example.com"
        assert finding.evidence is None
        assert finding.remediation is None
        assert finding.cve_id is None
        assert finding.references == []
        assert finding.raw_data == {}
    
    def test_parsed_finding_with_optional_fields(self):
        """Test ParsedFinding con campos opcionales."""
        finding = ParsedFinding(
            title="Test Finding",
            severity="critical",
            description="Test description",
            category="vulnerability",
            affected_target="example.com",
            evidence="Evidence text",
            remediation="Fix this",
            cvss_score=9.8,
            cve_id="CVE-2021-12345",
            references=["https://example.com/ref"],
            raw_data={"key": "value"}
        )
        
        assert finding.evidence == "Evidence text"
        assert finding.remediation == "Fix this"
        assert finding.cvss_score == 9.8
        assert finding.cve_id == "CVE-2021-12345"
        assert finding.references == ["https://example.com/ref"]
        assert finding.raw_data == {"key": "value"}


class ConcreteParser(BaseParser):
    """Parser concreto para testing (no abstracto)."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Siempre retorna True para testing."""
        return True
    
    def parse(self, file_path: Path):
        """Retorna lista vacía para testing."""
        return []


class TestBaseParser:
    """Tests para la clase base BaseParser."""
    
    def test_base_parser_is_abstract(self):
        """Test que BaseParser no se puede instanciar directamente."""
        with pytest.raises(TypeError):
            BaseParser()
    
    def test_concrete_parser_can_be_instantiated(self):
        """Test que un parser concreto puede instanciarse."""
        parser = ConcreteParser()
        assert parser is not None
        assert parser.logger is not None
    
    def test_read_file_utf8(self, tmp_path):
        """Test lectura de archivo UTF-8."""
        parser = ConcreteParser()
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content", encoding='utf-8')
        
        content = parser._read_file(test_file)
        assert content == "Test content"
    
    def test_read_file_latin1_fallback(self, tmp_path):
        """Test fallback a latin-1 cuando UTF-8 falla."""
        parser = ConcreteParser()
        test_file = tmp_path / "test.txt"
        # Escribir contenido que requiere latin-1
        test_file.write_bytes(b"Test\xe9 content")
        
        content = parser._read_file(test_file, encoding='utf-8')
        # Debe leer con latin-1 fallback
        assert "Test" in content
    
    def test_read_file_nonexistent(self, tmp_path):
        """Test lectura de archivo inexistente."""
        parser = ConcreteParser()
        nonexistent = tmp_path / "nonexistent.txt"
        
        content = parser._read_file(nonexistent)
        assert content == ""
    
    def test_safe_parse_json_valid(self, tmp_path):
        """Test parsing de JSON válido."""
        parser = ConcreteParser()
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}', encoding='utf-8')
        
        data = parser._safe_parse_json(test_file)
        assert data == {"key": "value"}
    
    def test_safe_parse_json_invalid(self, tmp_path):
        """Test parsing de JSON inválido."""
        parser = ConcreteParser()
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": invalid}', encoding='utf-8')
        
        data = parser._safe_parse_json(test_file)
        assert data is None
    
    def test_safe_parse_json_nonexistent(self, tmp_path):
        """Test parsing de archivo inexistente."""
        parser = ConcreteParser()
        nonexistent = tmp_path / "nonexistent.json"
        
        data = parser._safe_parse_json(nonexistent)
        assert data is None
    
    def test_validate_file_size_valid(self, tmp_path):
        """Test validación de tamaño de archivo válido."""
        parser = ConcreteParser()
        test_file = tmp_path / "test.txt"
        test_file.write_text("small content")
        
        from services.reporting.config import MAX_FILE_SIZE
        assert parser._validate_file_size(test_file, MAX_FILE_SIZE) is True
    
    def test_validate_file_size_too_large(self, tmp_path):
        """Test validación de archivo muy grande."""
        parser = ConcreteParser()
        test_file = tmp_path / "test.txt"
        # Crear archivo que excede el límite (100MB)
        large_content = "x" * (101 * 1024 * 1024)  # 101MB
        test_file.write_text(large_content)
        
        max_size = 100 * 1024 * 1024  # 100MB
        assert parser._validate_file_size(test_file, max_size) is False





