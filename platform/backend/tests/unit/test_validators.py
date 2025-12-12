"""
Test Validators
===============

Tests para validadores de seguridad.
"""

import pytest
from utils.validators import CommandSanitizer, IPValidator, DomainValidator


class TestCommandSanitizer:
    """Tests para CommandSanitizer."""
    
    def test_validate_ip_valid(self):
        """Test validación de IP válida."""
        assert CommandSanitizer.validate_target('192.168.1.1')
    
    def test_validate_ip_invalid(self):
        """Test validación de IP inválida."""
        with pytest.raises(ValueError):
            CommandSanitizer.validate_target('256.1.1.1')
    
    def test_validate_domain_valid(self):
        """Test validación de dominio válido."""
        assert CommandSanitizer.validate_target('example.com')
    
    def test_command_injection_detection(self):
        """Test detección de command injection."""
        malicious_commands = [
            ['nmap', '-sS', '127.0.0.1; rm -rf /'],
            ['nmap', '-sS', '127.0.0.1 | cat /etc/passwd'],
            ['nmap', '-sS', '127.0.0.1 && whoami'],
            ['nmap', '-sS', '`whoami`'],
        ]
        
        for cmd in malicious_commands:
            with pytest.raises(ValueError):
                CommandSanitizer.sanitize_command(cmd[0], cmd[1:])
    
    def test_command_whitelist(self):
        """Test whitelist de comandos."""
        # Comando permitido
        result = CommandSanitizer.sanitize_command('nmap', ['-sS', '192.168.1.1'])
        assert result == ['nmap', '-sS', '192.168.1.1']
        
        # Comando NO permitido
        with pytest.raises(ValueError):
            CommandSanitizer.sanitize_command('rm', ['-rf', '/'])
    
    def test_forbidden_sqlmap_options(self):
        """Test opciones prohibidas de SQLMap."""
        with pytest.raises(ValueError):
            CommandSanitizer.sanitize_command('sqlmap', ['-u', 'http://test.com', '--dump-all'])


class TestIPValidator:
    """Tests para IPValidator."""
    
    def test_valid_ipv4(self):
        """Test IPv4 válida."""
        assert IPValidator.is_valid_ip('192.168.1.1')
        assert IPValidator.is_valid_ip('10.0.0.1')
        assert IPValidator.is_valid_ip('8.8.8.8')
    
    def test_invalid_ipv4(self):
        """Test IPv4 inválida."""
        assert not IPValidator.is_valid_ip('256.1.1.1')
        assert not IPValidator.is_valid_ip('192.168.1')
        assert not IPValidator.is_valid_ip('invalid')
    
    def test_valid_cidr(self):
        """Test CIDR válido."""
        assert IPValidator.is_valid_cidr('192.168.1.0/24')
        assert IPValidator.is_valid_cidr('10.0.0.0/8')
    
    def test_invalid_cidr(self):
        """Test CIDR inválido."""
        assert not IPValidator.is_valid_cidr('192.168.1.1/33')
        assert not IPValidator.is_valid_cidr('invalid/24')
    
    def test_private_ip(self):
        """Test detección de IP privada."""
        assert IPValidator.is_private_ip('192.168.1.1')
        assert IPValidator.is_private_ip('10.0.0.1')
        assert IPValidator.is_private_ip('172.16.0.1')
        assert not IPValidator.is_private_ip('8.8.8.8')
    
    def test_port_validation(self):
        """Test validación de puertos."""
        assert IPValidator.validate_port(80)
        assert IPValidator.validate_port('443')
        assert not IPValidator.validate_port(0)
        assert not IPValidator.validate_port(65536)


class TestDomainValidator:
    """Tests para DomainValidator."""
    
    def test_valid_domain(self):
        """Test dominio válido."""
        assert DomainValidator.is_valid_domain('example.com')
        assert DomainValidator.is_valid_domain('sub.example.com')
        assert DomainValidator.is_valid_domain('api.v2.service.example.com')
    
    def test_invalid_domain(self):
        """Test dominio inválido."""
        assert not DomainValidator.is_valid_domain('invalid..com')
        assert not DomainValidator.is_valid_domain('-example.com')
        assert not DomainValidator.is_valid_domain('example')
    
    def test_wildcard_domain(self):
        """Test dominio wildcard."""
        assert DomainValidator.is_valid_wildcard_domain('*.example.com')
        assert not DomainValidator.is_valid_wildcard_domain('example.com')
    
    def test_extract_root_domain(self):
        """Test extracción de dominio raíz."""
        assert DomainValidator.extract_root_domain('sub.example.com') == 'example.com'
        assert DomainValidator.extract_root_domain('api.v2.service.example.com') == 'example.com'
        assert DomainValidator.extract_root_domain('example.com') == 'example.com'
    
    def test_url_validation(self):
        """Test validación de URLs."""
        assert DomainValidator.validate_url('https://example.com')
        assert DomainValidator.validate_url('http://sub.example.com:8080/path')
        assert not DomainValidator.validate_url('invalid-url')
        assert not DomainValidator.validate_url('ftp://example.com')



