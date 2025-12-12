"""
Tests Unitarios - Other Parsers
================================

Tests para otros parsers de reconocimiento.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.reconnaissance.other.whois_parser import WhoisParser
from services.reporting.parsers.reconnaissance.other.googledorks_parser import GoogleDorksParser
from services.reporting.parsers.reconnaissance.other.secrets_parser import SecretsParser

FIXTURES_DIR = Path(__file__).parent.parent / 'fixtures' / 'reconnaissance'


class TestOtherParsers:
    """Tests para otros parsers."""
    
    def test_whois_parser(self):
        """Test WhoisParser."""
        parser = WhoisParser()
        fixture_file = FIXTURES_DIR / 'whois_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert findings[0].category == 'reconnaissance'
        assert 'domain' in findings[0].raw_data
        assert findings[0].raw_data.get('tool') == 'whois'
    
    def test_googledorks_parser(self):
        """Test GoogleDorksParser."""
        parser = GoogleDorksParser()
        fixture_file = FIXTURES_DIR / 'googledorks_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'information_disclosure' for f in findings)
        assert all(f.raw_data.get('tool') == 'googledorks' for f in findings)
        # Debe tener diferentes severidades
        assert any(f.severity == 'critical' for f in findings)
        assert any(f.severity == 'high' for f in findings)
    
    def test_secrets_parser(self):
        """Test SecretsParser."""
        parser = SecretsParser()
        fixture_file = FIXTURES_DIR / 'gitleaks_sample.json'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'secrets_exposure' for f in findings)
        assert all(f.severity in ['critical', 'high', 'medium'] for f in findings)
        assert all(f.raw_data.get('tool') == 'secrets_detection' for f in findings)
    
    def test_whois_can_parse(self, tmp_path):
        """Test can_parse de WhoisParser."""
        parser = WhoisParser()
        
        valid_file = tmp_path / 'whois_123.txt'
        valid_file.touch()
        assert parser.can_parse(valid_file) is True
        
        invalid_file = tmp_path / 'other.txt'
        invalid_file.touch()
        assert parser.can_parse(invalid_file) is False
    
    def test_googledorks_can_parse(self, tmp_path):
        """Test can_parse de GoogleDorksParser."""
        parser = GoogleDorksParser()
        
        valid_files = [
            tmp_path / 'googledork_123.txt',
            tmp_path / 'dork_123.txt',
            tmp_path / 'google_123.txt'
        ]
        for valid_file in valid_files:
            valid_file.touch()
            assert parser.can_parse(valid_file) is True
        
        invalid_file = tmp_path / 'other.txt'
        invalid_file.touch()
        assert parser.can_parse(invalid_file) is False
    
    def test_secrets_can_parse(self, tmp_path):
        """Test can_parse de SecretsParser."""
        parser = SecretsParser()
        
        valid_files = [
            tmp_path / 'gitleaks_123.json',
            tmp_path / 'trufflehog_123.json',
            tmp_path / 'secret_123.json'
        ]
        for valid_file in valid_files:
            valid_file.touch()
            assert parser.can_parse(valid_file) is True
        
        invalid_file = tmp_path / 'other.json'
        invalid_file.touch()
        assert parser.can_parse(invalid_file) is False
    
    def test_googledorks_severity_classification(self, tmp_path):
        """Test que GoogleDorksParser clasifica severidades correctamente."""
        parser = GoogleDorksParser()
        
        test_file = tmp_path / 'dork_test.txt'
        test_file.write_text('''https://example.com/backup.sql
https://example.com/admin/config.php
https://example.com/error.log
https://example.com/page.html''')
        
        findings = parser.parse(test_file)
        assert len(findings) == 4
        
        # Verificar severidades
        sql_finding = next((f for f in findings if '.sql' in f.affected_target), None)
        assert sql_finding is not None
        assert sql_finding.severity == 'critical'
        
        config_finding = next((f for f in findings if 'config' in f.affected_target), None)
        assert config_finding is not None
        assert config_finding.severity == 'high'
        
        log_finding = next((f for f in findings if '.log' in f.affected_target), None)
        assert log_finding is not None
        assert log_finding.severity == 'medium'
    
    def test_secrets_severity_classification(self, tmp_path):
        """Test que SecretsParser clasifica severidades correctamente."""
        parser = SecretsParser()
        
        test_file = tmp_path / 'secrets_test.json'
        test_file.write_text('''[
          {"Description": "AWS Access Key", "Match": "AKIA...", "File": "config.js", "StartLine": 10, "RuleID": "aws-key"},
          {"Description": "API Token", "Match": "token123", "File": ".env", "StartLine": 5, "RuleID": "token"}
        ]''')
        
        findings = parser.parse(test_file)
        assert len(findings) == 2
        
        # AWS Key debe ser critical
        aws_finding = next((f for f in findings if 'AWS' in f.title), None)
        assert aws_finding is not None
        assert aws_finding.severity == 'critical'
        
        # Token debe ser high
        token_finding = next((f for f in findings if 'Token' in f.title), None)
        assert token_finding is not None
        assert token_finding.severity == 'high'


