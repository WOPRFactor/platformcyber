"""
Tests Unitarios - DNS Parsers
==============================

Tests para parsers de enumeración DNS.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.reconnaissance.dns.dnsrecon_parser import DNSReconParser
from services.reporting.parsers.reconnaissance.dns.fierce_parser import FierceParser
from services.reporting.parsers.reconnaissance.dns.dnsenum_parser import DNSEnumParser
from services.reporting.parsers.reconnaissance.dns.traceroute_parser import TracerouteParser

FIXTURES_DIR = Path(__file__).parent.parent / 'fixtures' / 'reconnaissance'


class TestDNSParsers:
    """Tests para parsers de DNS."""
    
    def test_dnsrecon_parser(self):
        """Test DNSReconParser."""
        parser = DNSReconParser()
        fixture_file = FIXTURES_DIR / 'dnsrecon_sample.json'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'dns_enumeration' for f in findings)
        assert any(f.raw_data.get('record_type') == 'A' for f in findings)
        assert all(f.raw_data.get('tool') == 'dnsrecon' for f in findings)
    
    def test_fierce_parser(self):
        """Test FierceParser."""
        parser = FierceParser()
        fixture_file = FIXTURES_DIR / 'fierce_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        # Debe encontrar NS, SOA o subdominios
        assert any('NS' in f.raw_data.get('type', '') or 
                   'SOA' in f.raw_data.get('type', '') or 
                   'subdomain' in f.raw_data.get('type', '') 
                   for f in findings)
        assert all(f.raw_data.get('tool') == 'fierce' for f in findings)
    
    def test_dnsenum_parser(self):
        """Test DNSEnumParser."""
        parser = DNSEnumParser()
        fixture_file = FIXTURES_DIR / 'dnsenum_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'dns_enumeration' for f in findings)
        assert all(f.raw_data.get('tool') == 'dnsenum' for f in findings)
    
    def test_traceroute_parser(self):
        """Test TracerouteParser."""
        parser = TracerouteParser()
        fixture_file = FIXTURES_DIR / 'traceroute_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'reconnaissance' for f in findings)
        assert all(f.raw_data.get('tool') == 'traceroute' for f in findings)
        # Debe tener hops o timeouts
        assert any('hop' in f.raw_data for f in findings)
    
    def test_dnsrecon_can_parse(self, tmp_path):
        """Test can_parse de DNSReconParser."""
        parser = DNSReconParser()
        
        valid_file = tmp_path / 'dnsrecon_123.json'
        valid_file.touch()
        assert parser.can_parse(valid_file) is True
        
        invalid_file = tmp_path / 'other.json'
        invalid_file.touch()
        assert parser.can_parse(invalid_file) is False
    
    def test_fierce_can_parse(self, tmp_path):
        """Test can_parse de FierceParser."""
        parser = FierceParser()
        
        valid_file = tmp_path / 'fierce_123.txt'
        valid_file.touch()
        assert parser.can_parse(valid_file) is True
        
        invalid_file = tmp_path / 'other.txt'
        invalid_file.touch()
        assert parser.can_parse(invalid_file) is False
    
    def test_dnsenum_can_parse(self, tmp_path):
        """Test can_parse de DNSEnumParser."""
        parser = DNSEnumParser()
        
        valid_file = tmp_path / 'dnsenum_123.txt'
        valid_file.touch()
        assert parser.can_parse(valid_file) is True
        
        invalid_file = tmp_path / 'other.txt'
        invalid_file.touch()
        assert parser.can_parse(invalid_file) is False
    
    def test_traceroute_can_parse(self, tmp_path):
        """Test can_parse de TracerouteParser."""
        parser = TracerouteParser()
        
        valid_file = tmp_path / 'traceroute_123.txt'
        valid_file.touch()
        assert parser.can_parse(valid_file) is True
        
        invalid_file = tmp_path / 'other.txt'
        invalid_file.touch()
        assert parser.can_parse(invalid_file) is False
    
    def test_dnsrecon_ignores_scaninfo(self, tmp_path):
        """Test que DNSReconParser ignora registros ScanInfo."""
        parser = DNSReconParser()
        
        test_file = tmp_path / 'dnsrecon_test.json'
        test_file.write_text('''[
            {"type": "ScanInfo", "arguments": "test"},
            {"type": "A", "name": "example.com", "address": "192.0.2.1"}
        ]''')
        
        findings = parser.parse(test_file)
        # Solo debe tener 1 finding (el A, no el ScanInfo)
        assert len(findings) == 1
        assert findings[0].raw_data.get('record_type') == 'A'
    
    def test_fierce_parses_nearby(self, tmp_path):
        """Test que FierceParser parsea IPs cercanas."""
        parser = FierceParser()
        
        test_file = tmp_path / 'fierce_test.txt'
        test_file.write_text('''NS: ns1.example.com.
Nearby:
{'192.0.2.9': 'server1.example.com.'}''')
        
        findings = parser.parse(test_file)
        # Debe encontrar NS y nearby
        assert len(findings) >= 2
        assert any(f.raw_data.get('type') == 'nearby' for f in findings)


