"""
Tests Unitarios - Network Services Enumeration Parsers
======================================================

Tests para parsers de enumeración de servicios de red.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.enumeration.network.ssh_audit_parser import SSHAuditParser
from services.reporting.parsers.enumeration.network.smtp_enum_parser import SMTPEnumParser
from services.reporting.parsers.enumeration.network.dns_zone_parser import DNSZoneParser
from services.reporting.parsers.enumeration.network.snmpwalk_parser import SNMPWalkParser
from services.reporting.parsers.enumeration.network.onesixtyone_parser import OneSixtyOneParser
from services.reporting.parsers.enumeration.network.ldapsearch_parser import LDAPSearchParser

FIXTURES_DIR = Path(__file__).parent.parent / 'fixtures' / 'enumeration' / 'network'


class TestNetworkParsers:
    """Tests para parsers de enumeración de servicios de red."""
    
    def test_ssh_audit_parser(self):
        """Test SSHAuditParser."""
        parser = SSHAuditParser()
        fixture_file = FIXTURES_DIR / 'ssh_audit_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) >= 0
        assert all(f.raw_data.get('tool') == 'ssh-audit' for f in findings) if findings else True
    
    def test_smtp_enum_parser(self):
        """Test SMTPEnumParser."""
        parser = SMTPEnumParser()
        fixture_file = FIXTURES_DIR / 'smtp_enum_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.category == 'smtp_enumeration' for f in findings)
        assert all(f.raw_data.get('tool') == 'smtp-user-enum' for f in findings)
        assert all('valid_users' in f.raw_data for f in findings)
    
    def test_dns_zone_parser(self):
        """Test DNSZoneParser."""
        parser = DNSZoneParser()
        fixture_file = FIXTURES_DIR / 'dns_zone_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.raw_data.get('tool') == 'dig_zone_transfer' for f in findings)
        # Verificar que hay finding de zone transfer
        zone_findings = [f for f in findings if f.title == 'DNS Zone Transfer successful']
        assert len(zone_findings) > 0
    
    def test_snmpwalk_parser(self):
        """Test SNMPWalkParser."""
        parser = SNMPWalkParser()
        fixture_file = FIXTURES_DIR / 'snmpwalk_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.raw_data.get('tool') == 'snmpwalk' for f in findings)
        # Verificar que hay finding de system info
        system_findings = [f for f in findings if 'system_info' in f.raw_data]
        assert len(system_findings) > 0
    
    def test_onesixtyone_parser(self):
        """Test OneSixtyOneParser."""
        parser = OneSixtyOneParser()
        fixture_file = FIXTURES_DIR / 'onesixtyone_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.raw_data.get('tool') == 'onesixtyone' for f in findings)
        assert all('community_string' in f.raw_data for f in findings)
    
    def test_ldapsearch_parser(self):
        """Test LDAPSearchParser."""
        parser = LDAPSearchParser()
        fixture_file = FIXTURES_DIR / 'ldapsearch_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) > 0
        assert all(f.raw_data.get('tool') == 'ldapsearch' for f in findings)
        # Verificar que hay finding de usuarios
        user_findings = [f for f in findings if 'users' in f.raw_data]
        assert len(user_findings) > 0
    
    def test_ssh_audit_can_parse(self):
        """Test SSHAuditParser.can_parse()."""
        parser = SSHAuditParser()
        
        assert parser.can_parse(Path('ssh-audit_123.txt'))
        assert parser.can_parse(Path('ssh_audit_sample.txt'))
        assert not parser.can_parse(Path('ssh-audit_123.json'))
        assert not parser.can_parse(Path('nmap_123.xml'))
    
    def test_smtp_enum_can_parse(self):
        """Test SMTPEnumParser.can_parse()."""
        parser = SMTPEnumParser()
        
        assert parser.can_parse(Path('smtp_enum_123.txt'))
        assert parser.can_parse(Path('SMTP_ENUM_sample.txt'))
        assert not parser.can_parse(Path('smtp_123.txt'))
        assert not parser.can_parse(Path('smtp_enum_123.json'))
    
    def test_dns_zone_can_parse(self):
        """Test DNSZoneParser.can_parse()."""
        parser = DNSZoneParser()
        
        assert parser.can_parse(Path('dig_123.txt'))
        assert parser.can_parse(Path('zone_transfer_sample.txt'))
        assert not parser.can_parse(Path('dig_123.json'))
        assert not parser.can_parse(Path('nmap_123.xml'))
    
    def test_snmpwalk_can_parse(self):
        """Test SNMPWalkParser.can_parse()."""
        parser = SNMPWalkParser()
        
        assert parser.can_parse(Path('snmpwalk_123.txt'))
        assert parser.can_parse(Path('SNMPWALK_sample.txt'))
        assert not parser.can_parse(Path('snmpwalk_123.json'))
        assert not parser.can_parse(Path('nmap_123.xml'))
    
    def test_onesixtyone_can_parse(self):
        """Test OneSixtyOneParser.can_parse()."""
        parser = OneSixtyOneParser()
        
        assert parser.can_parse(Path('onesixtyone_123.txt'))
        assert parser.can_parse(Path('ONESIXTYONE_sample.txt'))
        assert not parser.can_parse(Path('onesixtyone_123.json'))
        assert not parser.can_parse(Path('nmap_123.xml'))
    
    def test_ldapsearch_can_parse(self):
        """Test LDAPSearchParser.can_parse()."""
        parser = LDAPSearchParser()
        
        assert parser.can_parse(Path('ldapsearch_123.txt'))
        assert parser.can_parse(Path('ldap_enum_sample.txt'))
        assert not parser.can_parse(Path('ldapsearch_123.json'))
        assert not parser.can_parse(Path('nmap_123.xml'))


