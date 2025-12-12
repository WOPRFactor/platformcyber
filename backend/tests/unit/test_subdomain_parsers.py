"""
Tests Unitarios - Subdomain Parsers
====================================

Tests para parsers de enumeración de subdominios.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.reconnaissance.subdomain.assetfinder_parser import AssetfinderParser
from services.reporting.parsers.reconnaissance.subdomain.sublist3r_parser import Sublist3rParser
from services.reporting.parsers.reconnaissance.subdomain.findomain_parser import FindomainParser
from services.reporting.parsers.reconnaissance.subdomain.crtsh_parser import CrtshParser

FIXTURES_DIR = Path(__file__).parent.parent / 'fixtures' / 'reconnaissance'


class TestSubdomainParsers:
    """Tests para parsers de enumeración de subdominios."""
    
    def test_assetfinder_parser(self):
        """Test AssetfinderParser."""
        parser = AssetfinderParser()
        fixture_file = FIXTURES_DIR / 'assetfinder_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'reconnaissance' for f in findings)
        assert all(f.severity == 'info' for f in findings)
        assert all('subdomain' in f.raw_data for f in findings)
        assert all(f.raw_data.get('tool') == 'assetfinder' for f in findings)
    
    def test_sublist3r_parser(self):
        """Test Sublist3rParser."""
        parser = Sublist3rParser()
        fixture_file = FIXTURES_DIR / 'sublist3r_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all('.' in f.affected_target for f in findings)
        assert all(f.raw_data.get('tool') == 'sublist3r' for f in findings)
    
    def test_findomain_parser(self):
        """Test FindomainParser."""
        parser = FindomainParser()
        fixture_file = FIXTURES_DIR / 'findomain_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'reconnaissance' for f in findings)
        assert all(f.raw_data.get('tool') == 'findomain' for f in findings)
    
    def test_crtsh_parser(self):
        """Test CrtshParser."""
        parser = CrtshParser()
        fixture_file = FIXTURES_DIR / 'crtsh_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'reconnaissance' for f in findings)
        assert all(f.raw_data.get('tool') == 'crtsh' for f in findings)
    
    def test_assetfinder_can_parse(self, tmp_path):
        """Test can_parse de AssetfinderParser."""
        parser = AssetfinderParser()
        
        valid_file = tmp_path / 'assetfinder_123.txt'
        valid_file.touch()
        assert parser.can_parse(valid_file) is True
        
        invalid_file = tmp_path / 'other.txt'
        invalid_file.touch()
        assert parser.can_parse(invalid_file) is False
    
    def test_sublist3r_can_parse(self, tmp_path):
        """Test can_parse de Sublist3rParser."""
        parser = Sublist3rParser()
        
        valid_file = tmp_path / 'sublist3r_123.txt'
        valid_file.touch()
        assert parser.can_parse(valid_file) is True
        
        invalid_file = tmp_path / 'other.txt'
        invalid_file.touch()
        assert parser.can_parse(invalid_file) is False
    
    def test_findomain_can_parse(self, tmp_path):
        """Test can_parse de FindomainParser."""
        parser = FindomainParser()
        
        valid_file = tmp_path / 'findomain_123.txt'
        valid_file.touch()
        assert parser.can_parse(valid_file) is True
        
        invalid_file = tmp_path / 'other.txt'
        invalid_file.touch()
        assert parser.can_parse(invalid_file) is False
    
    def test_crtsh_can_parse(self, tmp_path):
        """Test can_parse de CrtshParser."""
        parser = CrtshParser()
        
        valid_file1 = tmp_path / 'crtsh_123.txt'
        valid_file1.touch()
        assert parser.can_parse(valid_file1) is True
        
        valid_file2 = tmp_path / 'crt.sh_123.txt'
        valid_file2.touch()
        assert parser.can_parse(valid_file2) is True
        
        invalid_file = tmp_path / 'other.txt'
        invalid_file.touch()
        assert parser.can_parse(invalid_file) is False
    
    def test_parsers_ignore_empty_lines(self, tmp_path):
        """Test que todos los parsers ignoran líneas vacías."""
        test_content = """subdomain1.example.com

subdomain2.example.com

subdomain3.example.com"""
        
        parsers = [
            AssetfinderParser(),
            Sublist3rParser(),
            FindomainParser(),
            CrtshParser()
        ]
        
        for parser in parsers:
            test_file = tmp_path / f"{parser.__class__.__name__.lower()}_test.txt"
            test_file.write_text(test_content)
            
            findings = parser.parse(test_file)
            assert len(findings) == 3
    
    def test_parsers_ignore_comments(self, tmp_path):
        """Test que todos los parsers ignoran comentarios."""
        test_content = """subdomain1.example.com
# Este es un comentario
subdomain2.example.com
# Otro comentario"""
        
        parsers = [
            AssetfinderParser(),
            Sublist3rParser(),
            FindomainParser(),
            CrtshParser()
        ]
        
        for parser in parsers:
            test_file = tmp_path / f"{parser.__class__.__name__.lower()}_test.txt"
            test_file.write_text(test_content)
            
            findings = parser.parse(test_file)
            assert len(findings) == 2


