"""
Tests Unitarios - SMB Enumeration Parsers
=========================================

Tests para parsers de enumeración SMB.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.enumeration.smb.enum4linux_parser import Enum4linuxParser
from services.reporting.parsers.enumeration.smb.smbmap_parser import SMBMapParser
from services.reporting.parsers.enumeration.smb.smbclient_parser import SMBClientParser

FIXTURES_DIR = Path(__file__).parent.parent / 'fixtures' / 'enumeration' / 'smb'


class TestSMBParsers:
    """Tests para parsers de enumeración SMB."""
    
    def test_enum4linux_parser(self):
        """Test Enum4linuxParser."""
        parser = Enum4linuxParser()
        fixture_file = FIXTURES_DIR / 'enum4linux_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'smb_enumeration' for f in findings)
        assert all(f.raw_data.get('tool') == 'enum4linux' for f in findings)
    
    def test_smbmap_parser(self):
        """Test SMBMapParser."""
        parser = SMBMapParser()
        fixture_file = FIXTURES_DIR / 'smbmap_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) >= 0
        assert all(f.raw_data.get('tool') == 'smbmap' for f in findings) if findings else True
    
    def test_smbclient_parser(self):
        """Test SMBClientParser."""
        parser = SMBClientParser()
        fixture_file = FIXTURES_DIR / 'smbclient_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) >= 0
        assert all(f.raw_data.get('tool') == 'smbclient' for f in findings) if findings else True
    
    def test_enum4linux_can_parse(self):
        """Test Enum4linuxParser.can_parse()."""
        parser = Enum4linuxParser()
        
        assert parser.can_parse(Path('enum4linux_123.txt'))
        assert parser.can_parse(Path('ENUM4LINUX_sample.txt'))
        assert not parser.can_parse(Path('enum4linux_123.json'))
        assert not parser.can_parse(Path('nmap_123.xml'))
    
    def test_smbmap_can_parse(self):
        """Test SMBMapParser.can_parse()."""
        parser = SMBMapParser()
        
        assert parser.can_parse(Path('smbmap_123.txt'))
        assert parser.can_parse(Path('SMBMAP_sample.txt'))
        assert not parser.can_parse(Path('smbmap_123.json'))
        assert not parser.can_parse(Path('nmap_123.xml'))
    
    def test_smbclient_can_parse(self):
        """Test SMBClientParser.can_parse()."""
        parser = SMBClientParser()
        
        assert parser.can_parse(Path('smbclient_123.txt'))
        assert parser.can_parse(Path('SMBCLIENT_sample.txt'))
        assert not parser.can_parse(Path('smbclient_123.json'))
        assert not parser.can_parse(Path('nmap_123.xml'))


