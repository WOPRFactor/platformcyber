"""
Tests Unitarios - OSINT Parsers
================================

Tests para parsers de Open Source Intelligence.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.reconnaissance.osint.shodan_parser import ShodanParser
from services.reporting.parsers.reconnaissance.osint.censys_parser import CensysParser
from services.reporting.parsers.reconnaissance.osint.theharvester_parser import TheHarvesterParser
from services.reporting.parsers.reconnaissance.osint.hunterio_parser import HunterioParser
from services.reporting.parsers.reconnaissance.osint.wayback_parser import WaybackParser

FIXTURES_DIR = Path(__file__).parent.parent / 'fixtures' / 'reconnaissance'


class TestOSINTParsers:
    """Tests para parsers de OSINT."""
    
    def test_shodan_parser(self):
        """Test ShodanParser."""
        parser = ShodanParser()
        fixture_file = FIXTURES_DIR / 'shodan_sample.json'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'osint' for f in findings)
        assert any(':' in f.affected_target for f in findings)  # IP:port format
        assert all(f.raw_data.get('tool') == 'shodan' for f in findings)
        # Debe tener al menos un finding con vulnerabilidades (high severity)
        assert any(f.severity == 'high' for f in findings)
    
    def test_censys_parser(self):
        """Test CensysParser."""
        parser = CensysParser()
        fixture_file = FIXTURES_DIR / 'censys_sample.json'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'osint' for f in findings)
        assert all(f.raw_data.get('tool') == 'censys' for f in findings)
    
    def test_theharvester_parser(self):
        """Test TheHarvesterParser."""
        parser = TheHarvesterParser()
        fixture_file = FIXTURES_DIR / 'theharvester_sample.json'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        # Debe tener hosts o emails
        assert any(f.raw_data.get('type') in ['host', 'email', 'ip', 'interesting_url'] for f in findings)
        assert all(f.raw_data.get('tool') == 'theharvester' for f in findings)
    
    def test_hunterio_parser(self):
        """Test HunterioParser."""
        parser = HunterioParser()
        fixture_file = FIXTURES_DIR / 'hunterio_sample.json'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'osint' for f in findings)
        assert all(f.raw_data.get('tool') == 'hunterio' for f in findings)
        # Debe tener pattern y/o emails
        assert any(f.raw_data.get('type') in ['pattern', 'email'] for f in findings)
    
    def test_wayback_parser(self):
        """Test WaybackParser."""
        parser = WaybackParser()
        fixture_file = FIXTURES_DIR / 'wayback_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'osint' for f in findings)
        assert all(f.raw_data.get('tool') == 'wayback' for f in findings)
        # Debe tener URLs sensibles (low severity)
        assert any(f.severity == 'low' for f in findings)
    
    def test_shodan_can_parse(self, tmp_path):
        """Test can_parse de ShodanParser."""
        parser = ShodanParser()
        
        valid_file = tmp_path / 'shodan_123.json'
        valid_file.touch()
        assert parser.can_parse(valid_file) is True
        
        invalid_file = tmp_path / 'other.json'
        invalid_file.touch()
        assert parser.can_parse(invalid_file) is False
    
    def test_shodan_vulnerabilities(self, tmp_path):
        """Test que ShodanParser detecta vulnerabilidades."""
        parser = ShodanParser()
        
        test_file = tmp_path / 'shodan_test.json'
        test_file.write_text('''{
          "matches": [
            {
              "ip_str": "192.0.2.1",
              "port": 443,
              "product": "nginx",
              "vulns": ["CVE-2021-44228"]
            }
          ]
        }''')
        
        findings = parser.parse(test_file)
        assert len(findings) == 1
        assert findings[0].severity == 'high'
        assert findings[0].cve_id == 'CVE-2021-44228'
    
    def test_hunterio_confidence(self, tmp_path):
        """Test que HunterioParser asigna severidad por confidence."""
        parser = HunterioParser()
        
        test_file = tmp_path / 'hunterio_test.json'
        test_file.write_text('''{
          "data": {
            "domain": "example.com",
            "emails": [
              {"value": "high@example.com", "confidence": 95},
              {"value": "low@example.com", "confidence": 50}
            ]
          }
        }''')
        
        findings = parser.parse(test_file)
        assert len(findings) == 2
        # Alta confidence = low severity (más riesgo)
        high_conf_finding = next(f for f in findings if 'high@' in f.affected_target)
        assert high_conf_finding.severity == 'low'


