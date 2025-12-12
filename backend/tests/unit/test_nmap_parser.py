"""
Tests Unitarios - NmapParser
============================

Tests para el parser de archivos XML de Nmap.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.scanning.nmap_parser import NmapParser


class TestNmapParser:
    """Tests para NmapParser."""
    
    @pytest.fixture
    def parser(self):
        """Fixture que retorna instancia de NmapParser."""
        return NmapParser()
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Fixture que crea archivo XML de Nmap de ejemplo."""
        sample_path = Path(__file__).parent.parent / "fixtures" / "nmap_sample.xml"
        if sample_path.exists():
            return sample_path
        
        # Si no existe el fixture, crear uno básico
        test_file = tmp_path / "nmap_test.xml"
        test_file.write_text("""<?xml version="1.0"?>
<nmaprun>
  <host>
    <status state="up"/>
    <address addr="192.168.1.100" addrtype="ipv4"/>
    <hostnames>
      <hostname name="test.example.com" type="PTR"/>
    </hostnames>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open"/>
        <service name="ssh" product="OpenSSH" version="8.2"/>
      </port>
      <port protocol="tcp" portid="80">
        <state state="open"/>
        <service name="http" product="Apache" version="2.4"/>
      </port>
    </ports>
  </host>
</nmaprun>""")
        return test_file
    
    def test_can_parse_nmap_xml(self, parser, tmp_path):
        """Test que can_parse identifica archivos XML de Nmap."""
        nmap_file = tmp_path / "nmap_123.xml"
        nmap_file.touch()
        
        assert parser.can_parse(nmap_file) is True
    
    def test_can_parse_non_nmap_xml(self, parser, tmp_path):
        """Test que can_parse rechaza XML que no es de Nmap."""
        other_file = tmp_path / "other.xml"
        other_file.touch()
        
        assert parser.can_parse(other_file) is False
    
    def test_can_parse_non_xml(self, parser, tmp_path):
        """Test que can_parse rechaza archivos no XML."""
        txt_file = tmp_path / "nmap_123.txt"
        txt_file.touch()
        
        assert parser.can_parse(txt_file) is False
    
    def test_parse_nmap_xml(self, parser, sample_file):
        """Test parsing de archivo XML de Nmap válido."""
        findings = parser.parse(sample_file)
        
        assert len(findings) > 0
        assert all(f.category == 'port_scan' for f in findings)
        assert all(f.affected_target for f in findings)
        assert all('port' in f.raw_data for f in findings)
    
    def test_parse_empty_file(self, parser, tmp_path):
        """Test parsing de archivo vacío."""
        empty_file = tmp_path / "nmap_empty.xml"
        empty_file.write_text("")
        
        findings = parser.parse(empty_file)
        assert findings == []
    
    def test_parse_invalid_xml(self, parser, tmp_path):
        """Test parsing de XML malformado."""
        invalid_file = tmp_path / "nmap_invalid.xml"
        invalid_file.write_text("<invalid>xml</invalid>")
        
        findings = parser.parse(invalid_file)
        # Debe retornar lista vacía sin crashear
        assert isinstance(findings, list)
    
    def test_parse_findings_structure(self, parser, sample_file):
        """Test que los findings tienen la estructura correcta."""
        findings = parser.parse(sample_file)
        
        if findings:
            finding = findings[0]
            assert hasattr(finding, 'title')
            assert hasattr(finding, 'severity')
            assert hasattr(finding, 'description')
            assert hasattr(finding, 'category')
            assert hasattr(finding, 'affected_target')
            assert hasattr(finding, 'raw_data')
    
    def test_parse_severity_assignment(self, parser, sample_file):
        """Test que se asigna severidad correcta según puerto."""
        findings = parser.parse(sample_file)
        
        # Verificar que todos tienen severidad válida
        valid_severities = ['critical', 'high', 'medium', 'low', 'info']
        assert all(f.severity in valid_severities for f in findings)
    
    def test_parse_extracts_port_info(self, parser, sample_file):
        """Test que se extrae información de puertos correctamente."""
        findings = parser.parse(sample_file)
        
        if findings:
            finding = findings[0]
            assert 'port' in finding.raw_data
            assert 'protocol' in finding.raw_data
            assert 'service' in finding.raw_data





