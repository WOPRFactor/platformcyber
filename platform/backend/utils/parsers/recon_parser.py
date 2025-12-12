"""
Reconnaissance Results Parser
==============================

Parsers para resultados de herramientas de reconnaissance.
"""

import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class ReconParser:
    """Parser para resultados de reconnaissance."""
    
    @staticmethod
    def parse_subfinder(output: str) -> Dict[str, Any]:
        """
        Parsea salida de subfinder.
        
        Formato esperado:
        subdomain1.example.com
        subdomain2.example.com
        """
        subdomains = [line.strip() for line in output.split('\n') if line.strip()]
        
        return {
            'tool': 'subfinder',
            'subdomains': list(set(subdomains)),  # Eliminar duplicados
            'count': len(set(subdomains))
        }
    
    @staticmethod
    def parse_amass(output: str) -> Dict[str, Any]:
        """
        Parsea salida de amass.
        
        Formato esperado:
        subdomain1.example.com
        subdomain2.example.com [192.168.1.1, 192.168.1.2]
        """
        subdomains = []
        subdomain_ips = {}
        
        for line in output.split('\n'):
            if not line.strip():
                continue
            
            # Extraer subdomain e IPs si existen
            match = re.match(r'(\S+)\s*\[(.*?)\]', line)
            if match:
                subdomain = match.group(1)
                ips = [ip.strip() for ip in match.group(2).split(',')]
                subdomains.append(subdomain)
                subdomain_ips[subdomain] = ips
            else:
                subdomain = line.strip()
                subdomains.append(subdomain)
        
        return {
            'tool': 'amass',
            'subdomains': list(set(subdomains)),
            'subdomain_ips': subdomain_ips,
            'count': len(set(subdomains))
        }
    
    @staticmethod
    def parse_theharvester(json_path: str) -> Dict[str, Any]:
        """
        Parsea salida JSON de theHarvester.
        
        Formato esperado: JSON
        {
            "emails": ["user@example.com"],
            "hosts": ["host1.example.com"],
            "ips": ["192.168.1.1"]
        }
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            return {
                'tool': 'theHarvester',
                'emails': data.get('emails', []),
                'hosts': data.get('hosts', []),
                'ips': data.get('ips', []),
                'email_count': len(data.get('emails', [])),
                'host_count': len(data.get('hosts', [])),
                'ip_count': len(data.get('ips', []))
            }
        except Exception as e:
            return {
                'tool': 'theHarvester',
                'error': str(e),
                'emails': [],
                'hosts': [],
                'ips': []
            }
    
    @staticmethod
    def parse_katana(output: str) -> Dict[str, Any]:
        """
        Parsea salida de Katana (crawler).
        
        Formato esperado:
        https://example.com/page1
        https://example.com/page2
        """
        urls = [line.strip() for line in output.split('\n') if line.strip()]
        
        # Analizar tipos de recursos
        endpoints = []
        js_files = []
        api_endpoints = []
        forms = []
        
        for url in urls:
            if '/api/' in url or url.endswith('.json'):
                api_endpoints.append(url)
            elif url.endswith('.js'):
                js_files.append(url)
            elif '?' in url or url.endswith('/login') or url.endswith('/register'):
                forms.append(url)
            else:
                endpoints.append(url)
        
        return {
            'tool': 'katana',
            'total_urls': len(urls),
            'endpoints': endpoints,
            'js_files': js_files,
            'api_endpoints': api_endpoints,
            'forms': forms,
            'all_urls': urls
        }
    
    @staticmethod
    def parse_dnsrecon(output: str) -> Dict[str, Any]:
        """
        Parsea salida de DNSRecon.
        """
        records = {
            'A': [],
            'AAAA': [],
            'MX': [],
            'NS': [],
            'TXT': [],
            'SOA': [],
            'CNAME': []
        }
        
        for line in output.split('\n'):
            if not line.strip():
                continue
            
            # Extraer tipo de registro y valor
            for record_type in records.keys():
                if f'[{record_type}]' in line or f'{record_type} ' in line:
                    records[record_type].append(line.strip())
        
        return {
            'tool': 'dnsrecon',
            'records': records,
            'total_records': sum(len(v) for v in records.values())
        }
    
    @staticmethod
    def parse_waybackurls(output: str) -> Dict[str, Any]:
        """
        Parsea salida de waybackurls (Wayback Machine).
        """
        urls = [line.strip() for line in output.split('\n') if line.strip()]
        
        # Agrupar por extensión
        by_extension = {}
        interesting_paths = []
        
        for url in urls:
            # Extraer extensión
            match = re.search(r'\.([a-z0-9]+)(\?|$)', url.lower())
            if match:
                ext = match.group(1)
                by_extension[ext] = by_extension.get(ext, 0) + 1
            
            # Identificar paths interesantes
            if any(keyword in url.lower() for keyword in 
                   ['admin', 'login', 'api', 'config', 'backup', 'upload', 'download']):
                interesting_paths.append(url)
        
        return {
            'tool': 'waybackurls',
            'total_urls': len(urls),
            'by_extension': by_extension,
            'interesting_paths': interesting_paths,
            'all_urls': urls[:1000]  # Limitar a 1000 para no sobrecargar
        }
    
    @staticmethod
    def parse_shodan(json_data: str) -> Dict[str, Any]:
        """
        Parsea respuesta de Shodan API.
        """
        try:
            data = json.loads(json_data) if isinstance(json_data, str) else json_data
            
            results = data.get('matches', [])
            
            services = {}
            countries = {}
            organizations = {}
            vulnerabilities = []
            
            for result in results:
                # Servicios
                port = result.get('port')
                if port:
                    services[port] = services.get(port, 0) + 1
                
                # Países
                country = result.get('location', {}).get('country_name')
                if country:
                    countries[country] = countries.get(country, 0) + 1
                
                # Organizaciones
                org = result.get('org')
                if org:
                    organizations[org] = organizations.get(org, 0) + 1
                
                # Vulnerabilidades
                vulns = result.get('vulns', [])
                vulnerabilities.extend(vulns)
            
            return {
                'tool': 'shodan',
                'total_results': len(results),
                'services': services,
                'countries': countries,
                'organizations': organizations,
                'vulnerabilities': list(set(vulnerabilities)),
                'raw_results': results[:50]  # Limitar para no sobrecargar
            }
        except Exception as e:
            return {
                'tool': 'shodan',
                'error': str(e)
            }
    
    @staticmethod
    def parse_gitleaks(output: str) -> Dict[str, Any]:
        """
        Parsea salida de GitLeaks (secrets detection).
        """
        findings = []
        
        # GitLeaks puede output en JSON o texto
        try:
            # Intentar parsear como JSON
            data = json.loads(output)
            if isinstance(data, list):
                findings = data
            elif isinstance(data, dict) and 'findings' in data:
                findings = data['findings']
        except:
            # Parsear como texto
            for line in output.split('\n'):
                if 'Finding:' in line or 'Secret:' in line or 'Leak:' in line:
                    findings.append({'raw': line.strip()})
        
        # Agrupar por tipo
        by_type = {}
        for finding in findings:
            rule_id = finding.get('RuleID', finding.get('rule', 'unknown'))
            by_type[rule_id] = by_type.get(rule_id, 0) + 1
        
        return {
            'tool': 'gitleaks',
            'total_findings': len(findings),
            'by_type': by_type,
            'findings': findings,
            'severity': 'CRITICAL' if len(findings) > 0 else 'INFO'
        }

