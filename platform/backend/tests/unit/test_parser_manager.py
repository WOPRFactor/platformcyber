"""
Tests Unitarios - ParserManager
================================

Tests para el gestor de parsers.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.parser_manager import ParserManager
from services.reporting.parsers.scanning.nmap_parser import NmapParser
from services.reporting.parsers.vulnerability.nuclei_parser import NucleiParser
from services.reporting.parsers.reconnaissance.subfinder_parser import SubfinderParser
from services.reporting.parsers.vulnerability.nikto_parser import NiktoParser


class TestParserManager:
    """Tests para ParserManager."""
    
    @pytest.fixture
    def manager(self):
        """Fixture que retorna instancia de ParserManager."""
        return ParserManager()
    
    def test_manager_initialization(self, manager):
        """Test que el manager se inicializa con parsers por defecto."""
        assert len(manager.parsers) > 0
        assert any(isinstance(p, NmapParser) for p in manager.parsers)
        assert any(isinstance(p, NucleiParser) for p in manager.parsers)
        assert any(isinstance(p, SubfinderParser) for p in manager.parsers)
        assert any(isinstance(p, NiktoParser) for p in manager.parsers)
    
    def test_get_parser_nmap(self, manager, tmp_path):
        """Test que get_parser encuentra NmapParser para archivos XML de Nmap."""
        nmap_file = tmp_path / "nmap_123.xml"
        nmap_file.touch()
        
        parser = manager.get_parser(nmap_file)
        assert parser is not None
        assert isinstance(parser, NmapParser)
    
    def test_get_parser_nuclei(self, manager, tmp_path):
        """Test que get_parser encuentra NucleiParser para archivos JSONL de Nuclei."""
        nuclei_file = tmp_path / "nuclei_123.jsonl"
        nuclei_file.touch()
        
        parser = manager.get_parser(nuclei_file)
        assert parser is not None
        assert isinstance(parser, NucleiParser)
    
    def test_get_parser_subfinder(self, manager, tmp_path):
        """Test que get_parser encuentra SubfinderParser para archivos TXT de Subfinder."""
        subfinder_file = tmp_path / "subfinder_123.txt"
        subfinder_file.touch()
        
        parser = manager.get_parser(subfinder_file)
        assert parser is not None
        assert isinstance(parser, SubfinderParser)
    
    def test_get_parser_nikto(self, manager, tmp_path):
        """Test que get_parser encuentra NiktoParser para archivos JSON de Nikto."""
        nikto_file = tmp_path / "nikto_123.json"
        nikto_file.touch()
        
        parser = manager.get_parser(nikto_file)
        assert parser is not None
        assert isinstance(parser, NiktoParser)
    
    def test_get_parser_unknown(self, manager, tmp_path):
        """Test que get_parser retorna None para archivos desconocidos."""
        unknown_file = tmp_path / "unknown.txt"
        unknown_file.touch()
        
        parser = manager.get_parser(unknown_file)
        assert parser is None
    
    def test_parse_file_with_valid_parser(self, manager, tmp_path):
        """Test que parse_file usa el parser correcto."""
        # Crear archivo de prueba simple
        test_file = tmp_path / "subfinder_test.txt"
        test_file.write_text("subdomain.example.com")
        
        findings = manager.parse_file(test_file)
        assert isinstance(findings, list)
        # Puede estar vacío si el parser no encuentra nada válido
    
    def test_parse_file_without_parser(self, manager, tmp_path):
        """Test que parse_file retorna lista vacía si no hay parser."""
        unknown_file = tmp_path / "unknown.txt"
        unknown_file.write_text("content")
        
        findings = manager.parse_file(unknown_file)
        assert findings == []
    
    def test_register_parser(self, manager):
        """Test que se puede registrar un nuevo parser."""
        from services.reporting.parsers.base_parser import BaseParser
        
        class TestParser(BaseParser):
            def can_parse(self, file_path: Path) -> bool:
                return file_path.suffix == '.test'
            
            def parse(self, file_path: Path):
                return []
        
        initial_count = len(manager.parsers)
        test_parser = TestParser()
        manager.register_parser(test_parser)
        
        assert len(manager.parsers) == initial_count + 1
        assert test_parser in manager.parsers

