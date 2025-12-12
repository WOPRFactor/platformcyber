"""
Unit Tests - Parsers
====================

Tests para los parsers más críticos del sistema.
"""

import unittest
import json
from utils.parsers.nmap_parser import NmapParser
from utils.parsers.api_parser import ArjunParser, JWTToolParser, GraphQLParser
from utils.parsers.mobile_parser import MobSFParser
from utils.parsers.container_parser import TrivyParser


class TestNmapParser(unittest.TestCase):
    """Tests para NmapParser."""
    
    def test_parse_basic_scan(self):
        """Test de parseo básico de Nmap."""
        xml_output = '''<?xml version="1.0" encoding="UTF-8"?>
<nmaprun scanner="nmap" version="7.94">
  <host>
    <address addr="192.168.1.1" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="80">
        <state state="open"/>
        <service name="http" product="nginx" version="1.18.0"/>
      </port>
      <port protocol="tcp" portid="443">
        <state state="open"/>
        <service name="https" product="nginx" version="1.18.0"/>
      </port>
    </ports>
  </host>
</nmaprun>'''
        
        parser = NmapParser()
        result = parser.parse_xml(xml_output)
        
        self.assertIn('hosts', result)
        self.assertEqual(len(result['hosts']), 1)
        
        host = result['hosts'][0]
        self.assertEqual(host['ip'], '192.168.1.1')
        self.assertIn('ports', host)
        self.assertEqual(len(host['ports']), 2)
    
    def test_parse_empty_scan(self):
        """Test de parseo con scan vacío."""
        xml_output = '''<?xml version="1.0" encoding="UTF-8"?>
<nmaprun scanner="nmap" version="7.94">
</nmaprun>'''
        
        parser = NmapParser()
        result = parser.parse_xml(xml_output)
        
        self.assertIn('hosts', result)
        self.assertEqual(len(result['hosts']), 0)


class TestArjunParser(unittest.TestCase):
    """Tests para ArjunParser."""
    
    def test_parse_parameters(self):
        """Test de parseo de parámetros descubiertos."""
        output = """
[+] Discovered parameters for GET: id, page, limit
[+] Discovered parameters for POST: username, password, email
        """
        
        parser = ArjunParser()
        result = parser.parse_output(output)
        
        self.assertEqual(result['tool'], 'arjun')
        self.assertIn('parameters', result)
        
        params = result['parameters']
        self.assertGreater(len(params['get_params']), 0)
        self.assertGreater(len(params['post_params']), 0)
        self.assertGreater(params['total'], 0)
    
    def test_parse_no_parameters(self):
        """Test cuando no se encuentran parámetros."""
        output = "No parameters found"
        
        parser = ArjunParser()
        result = parser.parse_output(output)
        
        self.assertEqual(result['parameters']['total'], 0)


class TestJWTToolParser(unittest.TestCase):
    """Tests para JWTToolParser."""
    
    def test_parse_jwt_basic(self):
        """Test de parseo básico de JWT."""
        output = '''
{"alg": "HS256", "typ": "JWT"}
{"sub": "1234567890", "name": "John Doe", "iat": 1516239022}
        '''
        
        parser = JWTToolParser()
        result = parser.parse_jwt_info(output)
        
        self.assertEqual(result['tool'], 'jwt_tool')
        self.assertIn('jwt_info', result)
        
        jwt_info = result['jwt_info']
        self.assertEqual(jwt_info['algorithm'], 'HS256')
        self.assertIn('sub', jwt_info['payload'])


class TestGraphQLParser(unittest.TestCase):
    """Tests para GraphQLParser."""
    
    def test_parse_introspection(self):
        """Test de parseo de introspection GraphQL."""
        introspection = {
            "data": {
                "__schema": {
                    "types": [
                        {
                            "name": "Query",
                            "kind": "OBJECT",
                            "fields": [
                                {"name": "user"},
                                {"name": "posts"}
                            ]
                        },
                        {
                            "name": "Mutation",
                            "kind": "OBJECT",
                            "fields": [
                                {"name": "createUser"}
                            ]
                        },
                        {
                            "name": "User",
                            "kind": "OBJECT",
                            "fields": [
                                {"name": "id"},
                                {"name": "password"}
                            ]
                        }
                    ]
                }
            }
        }
        
        parser = GraphQLParser()
        result = parser.parse_introspection(json.dumps(introspection))
        
        self.assertEqual(result['tool'], 'graphql')
        self.assertTrue(result['introspection_enabled'])
        self.assertGreater(result['total_queries'], 0)
        self.assertGreater(result['total_mutations'], 0)
        self.assertGreater(len(result['sensitive_fields']), 0)


class TestMobSFParser(unittest.TestCase):
    """Tests para MobSFParser."""
    
    def test_parse_static_analysis(self):
        """Test de parseo de análisis estático de MobSF."""
        mobsf_result = {
            "app_name": "TestApp",
            "package_name": "com.example.testapp",
            "version_name": "1.0.0",
            "target_sdk": "31",
            "min_sdk": "21",
            "security_score": 75,
            "permissions": {
                "android.permission.INTERNET": {
                    "status": "dangerous",
                    "info": "Network access",
                    "description": "Allows network communication"
                }
            }
        }
        
        parser = MobSFParser()
        result = parser.parse_static_analysis(json.dumps(mobsf_result))
        
        self.assertEqual(result['tool'], 'mobsf')
        self.assertEqual(result['analysis_type'], 'static')
        self.assertEqual(result['app_name'], 'TestApp')
        self.assertEqual(result['security_score'], 75)


class TestTrivyParser(unittest.TestCase):
    """Tests para TrivyParser."""
    
    def test_parse_image_scan(self):
        """Test de parseo de escaneo de imagen Trivy."""
        trivy_result = {
            "ArtifactName": "nginx:latest",
            "ArtifactType": "container_image",
            "Results": [
                {
                    "Target": "nginx:latest (alpine 3.18.4)",
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-2023-1234",
                            "Severity": "CRITICAL",
                            "PkgName": "openssl",
                            "InstalledVersion": "1.1.1",
                            "FixedVersion": "1.1.1k",
                            "Title": "OpenSSL vulnerability"
                        },
                        {
                            "VulnerabilityID": "CVE-2023-5678",
                            "Severity": "HIGH",
                            "PkgName": "curl",
                            "InstalledVersion": "7.80.0",
                            "FixedVersion": "7.81.0"
                        }
                    ]
                }
            ]
        }
        
        parser = TrivyParser()
        result = parser.parse_image_scan(json.dumps(trivy_result))
        
        self.assertEqual(result['tool'], 'trivy')
        self.assertEqual(result['artifact_name'], 'nginx:latest')
        self.assertGreater(result['total_vulnerabilities'], 0)
        self.assertIn('CRITICAL', result['by_severity'])


class TestCommandSanitizer(unittest.TestCase):
    """Tests para CommandSanitizer."""
    
    def test_sanitize_basic_command(self):
        """Test de sanitización básica."""
        from utils.validators import CommandSanitizer
        
        cmd = CommandSanitizer.sanitize_command('nmap', ['-sV', '192.168.1.1'])
        
        self.assertIsInstance(cmd, list)
        self.assertEqual(cmd[0], 'nmap')
        self.assertIn('-sV', cmd)
        self.assertIn('192.168.1.1', cmd)
    
    def test_sanitize_rejects_dangerous_chars(self):
        """Test que rechaza caracteres peligrosos."""
        from utils.validators import CommandSanitizer
        
        with self.assertRaises(ValueError):
            CommandSanitizer.sanitize_command('nmap', ['-sV', '192.168.1.1; rm -rf /'])
        
        with self.assertRaises(ValueError):
            CommandSanitizer.sanitize_command('nmap', ['-sV', '192.168.1.1 && cat /etc/passwd'])


class TestDomainValidator(unittest.TestCase):
    """Tests para DomainValidator."""
    
    def test_valid_domains(self):
        """Test de dominios válidos."""
        from utils.validators import DomainValidator
        
        valid_domains = [
            'example.com',
            'subdomain.example.com',
            'api.v1.example.co.uk',
            'test-site.org'
        ]
        
        for domain in valid_domains:
            self.assertTrue(DomainValidator.is_valid_domain(domain))
    
    def test_valid_ips(self):
        """Test de IPs válidas."""
        from utils.validators import DomainValidator
        
        valid_ips = [
            '192.168.1.1',
            '10.0.0.1',
            '172.16.0.1',
            '8.8.8.8'
        ]
        
        for ip in valid_ips:
            self.assertTrue(DomainValidator.is_valid_domain(ip))
    
    def test_invalid_domains(self):
        """Test de dominios inválidos."""
        from utils.validators import DomainValidator
        
        invalid_domains = [
            'localhost',
            '127.0.0.1',
            '0.0.0.0',
            'invalid..domain.com',
            'domain_with_underscore.com'
        ]
        
        for domain in invalid_domains:
            with self.assertRaises(ValueError):
                DomainValidator.is_valid_domain(domain)


if __name__ == '__main__':
    unittest.main()



