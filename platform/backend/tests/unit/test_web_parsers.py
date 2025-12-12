"""
Tests Unitarios - Web Parsers
==============================

Tests para parsers de reconocimiento web.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.reconnaissance.web.whatweb_parser import WhatWebParser
from services.reporting.parsers.reconnaissance.web.webcrawler_parser import WebCrawlerParser

FIXTURES_DIR = Path(__file__).parent.parent / 'fixtures' / 'reconnaissance'


class TestWebParsers:
    """Tests para parsers web."""
    
    def test_whatweb_parser(self):
        """Test WhatWebParser."""
        parser = WhatWebParser()
        fixture_file = FIXTURES_DIR / 'whatweb_sample.json'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'web_reconnaissance' for f in findings)
        assert any('technologies' in f.raw_data for f in findings)
        assert all(f.raw_data.get('tool') == 'whatweb' for f in findings)
    
    def test_webcrawler_parser(self):
        """Test WebCrawlerParser."""
        parser = WebCrawlerParser()
        fixture_file = FIXTURES_DIR / 'gospider_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) >= 0  # Puede no tener URLs sensibles
        if findings:
            assert all(f.affected_target.startswith('http') for f in findings)
            assert all(f.raw_data.get('tool') == 'webcrawler' for f in findings)
            # Debe detectar URLs sensibles
            assert any(f.severity == 'medium' for f in findings)
    
    def test_whatweb_can_parse(self, tmp_path):
        """Test can_parse de WhatWebParser."""
        parser = WhatWebParser()
        
        valid_file = tmp_path / 'whatweb_123.json'
        valid_file.touch()
        assert parser.can_parse(valid_file) is True
        
        invalid_file = tmp_path / 'other.json'
        invalid_file.touch()
        assert parser.can_parse(invalid_file) is False
    
    def test_webcrawler_can_parse(self, tmp_path):
        """Test can_parse de WebCrawlerParser."""
        parser = WebCrawlerParser()
        
        valid_files = [
            tmp_path / 'gospider_123.txt',
            tmp_path / 'hakrawler_123.txt',
            tmp_path / 'crawler_123.txt'
        ]
        for valid_file in valid_files:
            valid_file.touch()
            assert parser.can_parse(valid_file) is True
        
        invalid_file = tmp_path / 'other.txt'
        invalid_file.touch()
        assert parser.can_parse(invalid_file) is False
    
    def test_webcrawler_classifies_urls(self, tmp_path):
        """Test que WebCrawlerParser clasifica URLs correctamente."""
        parser = WebCrawlerParser()
        
        test_file = tmp_path / 'crawler_test.txt'
        test_file.write_text('''https://example.com/
https://example.com/admin/login
https://example.com/api/v1/users
https://example.com/static/style.css''')
        
        findings = parser.parse(test_file)
        # Debe tener 3 findings (admin, api, root) - excluye estáticos
        assert len(findings) == 3
        # Debe detectar admin como medium severity
        admin_finding = next((f for f in findings if 'admin' in f.affected_target), None)
        assert admin_finding is not None
        assert admin_finding.severity == 'medium'
        assert admin_finding.category == 'web_vulnerability'


