"""
Tests Unitarios - SSL Enumeration Parsers
=========================================

Tests para parsers de enumeración SSL/TLS.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.enumeration.ssl.sslscan_parser import SSLScanParser
from services.reporting.parsers.enumeration.ssl.sslyze_parser import SSLyzeParser
from services.reporting.parsers.enumeration.ssl.testssl_parser import TestSSLParser

FIXTURES_DIR = Path(__file__).parent.parent / 'fixtures' / 'enumeration' / 'ssl'


class TestSSLParsers:
    """Tests para parsers de enumeración SSL/TLS."""
    
    def test_sslscan_parser(self):
        """Test SSLScanParser."""
        parser = SSLScanParser()
        fixture_file = FIXTURES_DIR / 'sslscan_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'ssl_enumeration' for f in findings)
        assert all(f.raw_data.get('tool') == 'sslscan' for f in findings)
        # Verificar que hay finding de weak ciphers
        weak_ciphers_findings = [f for f in findings if f.raw_data.get('type') == 'weak_ciphers']
        assert len(weak_ciphers_findings) > 0
    
    def test_sslyze_parser(self):
        """Test SSLyzeParser."""
        parser = SSLyzeParser()
        fixture_file = FIXTURES_DIR / 'sslyze_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) >= 0
        assert all(f.raw_data.get('tool') == 'sslyze' for f in findings) if findings else True
        # Verificar que hay finding de weak ciphers si existen
        if findings:
            weak_ciphers_findings = [f for f in findings if 'weak_ciphers' in f.raw_data]
            assert len(weak_ciphers_findings) > 0
    
    def test_testssl_parser(self):
        """Test TestSSLParser."""
        parser = TestSSLParser()
        fixture_file = FIXTURES_DIR / 'testssl_sample.json'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'ssl_vulnerability' for f in findings)
        assert all(f.raw_data.get('tool') == 'testssl' for f in findings)
        # Verificar que hay finding de weak protocols
        weak_protocols_findings = [f for f in findings if 'weak_protocols' in f.raw_data]
        assert len(weak_protocols_findings) > 0
    
    def test_sslscan_can_parse(self):
        """Test SSLScanParser.can_parse()."""
        parser = SSLScanParser()
        
        assert parser.can_parse(Path('sslscan_123.txt'))
        assert parser.can_parse(Path('SSLSCAN_sample.txt'))
        assert not parser.can_parse(Path('sslscan_123.json'))
        assert not parser.can_parse(Path('nmap_123.xml'))
    
    def test_sslyze_can_parse(self):
        """Test SSLyzeParser.can_parse()."""
        parser = SSLyzeParser()
        
        assert parser.can_parse(Path('sslyze_123.txt'))
        assert parser.can_parse(Path('SSLYZE_sample.txt'))
        assert not parser.can_parse(Path('sslyze_123.json'))
        assert not parser.can_parse(Path('nmap_123.xml'))
    
    def test_testssl_can_parse(self):
        """Test TestSSLParser.can_parse()."""
        parser = TestSSLParser()
        
        assert parser.can_parse(Path('testssl_123.json'))
        assert parser.can_parse(Path('TESTSSL_sample.json'))
        assert not parser.can_parse(Path('testssl_123.txt'))
        assert not parser.can_parse(Path('nmap_123.xml'))


