"""
Tests Unitarios - Port Scanning Parsers
========================================

Tests para parsers de port scanning.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.scanning.rustscan_parser import RustScanParser
from services.reporting.parsers.scanning.masscan_parser import MasscanParser
from services.reporting.parsers.scanning.naabu_parser import NaabuParser

FIXTURES_DIR = Path(__file__).parent.parent / 'fixtures' / 'scanning'


class TestPortScanningParsers:
    """Tests para parsers de port scanning."""
    
    def test_rustscan_parser(self):
        """Test RustScanParser."""
        parser = RustScanParser()
        fixture_file = FIXTURES_DIR / 'rustscan_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'port_scanning' for f in findings)
        assert all('port' in f.raw_data for f in findings)
        assert all(f.raw_data.get('tool') == 'rustscan' for f in findings)
    
    def test_masscan_parser(self):
        """Test MasscanParser."""
        parser = MasscanParser()
        fixture_file = FIXTURES_DIR / 'masscan_sample.json'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.severity == 'info' for f in findings)
        assert all(f.raw_data.get('tool') == 'masscan' for f in findings)
    
    def test_naabu_parser(self):
        """Test NaabuParser."""
        parser = NaabuParser()
        fixture_file = FIXTURES_DIR / 'naabu_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(':' in f.affected_target for f in findings)
        assert all(f.raw_data.get('tool') == 'naabu' for f in findings)
    
    def test_rustscan_can_parse(self):
        """Test RustScanParser.can_parse()."""
        parser = RustScanParser()
        
        assert parser.can_parse(Path('rustscan_123.txt'))
        assert parser.can_parse(Path('RUSTSCAN_sample.txt'))
        assert not parser.can_parse(Path('nmap_123.xml'))
        assert not parser.can_parse(Path('rustscan_123.json'))
    
    def test_masscan_can_parse(self):
        """Test MasscanParser.can_parse()."""
        parser = MasscanParser()
        
        assert parser.can_parse(Path('masscan_123.json'))
        assert parser.can_parse(Path('MASSCAN_sample.json'))
        assert not parser.can_parse(Path('masscan_123.txt'))
        assert not parser.can_parse(Path('nmap_123.xml'))
    
    def test_naabu_can_parse(self):
        """Test NaabuParser.can_parse()."""
        parser = NaabuParser()
        
        assert parser.can_parse(Path('naabu_123.txt'))
        assert parser.can_parse(Path('NAABU_sample.txt'))
        assert not parser.can_parse(Path('naabu_123.json'))
        assert not parser.can_parse(Path('nmap_123.xml'))



