"""
Vulnerability Assessment Parsers
==================================

Parsers para herramientas de análisis de vulnerabilidades.
"""

import json
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from pathlib import Path


class NucleiParser:
    """Parser para resultados de Nuclei."""
    
    @staticmethod
    def parse_jsonl(output: str) -> Dict[str, Any]:
        """
        Parsea salida JSONL de Nuclei.
        
        Formato esperado: Una línea JSON por finding
        """
        findings = []
        
        for line in output.strip().split('\n'):
            if not line.strip():
                continue
            
            try:
                finding = json.loads(line)
                findings.append({
                    'template_id': finding.get('template-id'),
                    'template': finding.get('template'),
                    'name': finding.get('info', {}).get('name'),
                    'severity': finding.get('info', {}).get('severity'),
                    'description': finding.get('info', {}).get('description'),
                    'tags': finding.get('info', {}).get('tags', []),
                    'matched_at': finding.get('matched-at'),
                    'matcher_name': finding.get('matcher-name'),
                    'type': finding.get('type'),
                    'host': finding.get('host'),
                    'timestamp': finding.get('timestamp')
                })
            except json.JSONDecodeError:
                continue
        
        # Agrupar por severidad
        by_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }
        
        for finding in findings:
            severity = finding.get('severity', 'info').lower()
            if severity in by_severity:
                by_severity[severity].append(finding)
        
        return {
            'tool': 'nuclei',
            'total_findings': len(findings),
            'by_severity': {
                'critical': len(by_severity['critical']),
                'high': len(by_severity['high']),
                'medium': len(by_severity['medium']),
                'low': len(by_severity['low']),
                'info': len(by_severity['info'])
            },
            'findings': findings,
            'findings_by_severity': by_severity
        }


class NiktoParser:
    """Parser para resultados de Nikto."""
    
    @staticmethod
    def parse_json(json_data: str) -> Dict[str, Any]:
        """Parsea salida JSON de Nikto."""
        try:
            data = json.loads(json_data) if isinstance(json_data, str) else json_data
            
            vulnerabilities = []
            
            # Nikto puede tener múltiples hosts
            for host_data in data.get('vulnerabilities', []):
                for vuln in host_data:
                    vulnerabilities.append({
                        'id': vuln.get('id'),
                        'method': vuln.get('method'),
                        'uri': vuln.get('uri'),
                        'message': vuln.get('msg'),
                        'osvdb': vuln.get('OSVDB'),
                        'references': vuln.get('references', [])
                    })
            
            return {
                'tool': 'nikto',
                'total_findings': len(vulnerabilities),
                'findings': vulnerabilities,
                'scan_info': {
                    'target': data.get('host'),
                    'port': data.get('port'),
                    'ssl': data.get('ssl')
                }
            }
        except Exception as e:
            return {
                'tool': 'nikto',
                'error': str(e),
                'findings': []
            }
    
    @staticmethod
    def parse_xml(xml_file: str) -> Dict[str, Any]:
        """Parsea salida XML de Nikto."""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            vulnerabilities = []
            
            for item in root.findall('.//item'):
                vulnerabilities.append({
                    'id': item.get('id'),
                    'osvdb': item.findtext('osvdb'),
                    'method': item.findtext('method'),
                    'uri': item.findtext('uri'),
                    'description': item.findtext('description'),
                    'namelink': item.findtext('namelink')
                })
            
            return {
                'tool': 'nikto',
                'total_findings': len(vulnerabilities),
                'findings': vulnerabilities
            }
        except Exception as e:
            return {
                'tool': 'nikto',
                'error': str(e),
                'findings': []
            }


class SQLMapParser:
    """Parser para resultados de SQLMap."""
    
    @staticmethod
    def parse_output(output: str) -> Dict[str, Any]:
        """
        Parsea salida de texto de SQLMap.
        """
        results = {
            'tool': 'sqlmap',
            'vulnerable': False,
            'injections': [],
            'databases': [],
            'tables': [],
            'columns': [],
            'data': []
        }
        
        # Detectar si es vulnerable
        if 'vulnerable' in output.lower() or 'sqlmap identified' in output.lower():
            results['vulnerable'] = True
        
        # Extraer tipo de inyección
        injection_matches = re.findall(
            r'Parameter: (.*?) \(.*?\)\s+Type: (.*?)\s+Title: (.*?)\s+Payload:',
            output,
            re.DOTALL
        )
        
        for match in injection_matches:
            results['injections'].append({
                'parameter': match[0].strip(),
                'type': match[1].strip(),
                'title': match[2].strip()
            })
        
        # Extraer bases de datos
        db_match = re.search(r'available databases.*?:\s*\[(.*?)\]', output, re.IGNORECASE | re.DOTALL)
        if db_match:
            dbs = [db.strip().strip("'") for db in db_match.group(1).split(',')]
            results['databases'] = dbs
        
        # Extraer tablas
        table_matches = re.findall(r'Database: (.*?)\s+\[(.*?) tables?\]', output)
        for db, count in table_matches:
            results['tables'].append({
                'database': db.strip(),
                'count': count.strip()
            })
        
        return results
    
    @staticmethod
    def parse_json(json_path: str) -> Dict[str, Any]:
        """Parsea salida JSON de SQLMap."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            return {
                'tool': 'sqlmap',
                'vulnerable': len(data.get('data', [])) > 0,
                'data': data.get('data', []),
                'error': data.get('error')
            }
        except Exception as e:
            return {
                'tool': 'sqlmap',
                'error': str(e)
            }


class TestSSLParser:
    """Parser para resultados de testssl.sh."""
    
    @staticmethod
    def parse_json(json_path: str) -> Dict[str, Any]:
        """Parsea salida JSON de testssl.sh."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            findings = []
            critical_issues = []
            
            for item in data:
                severity = item.get('severity', 'INFO').upper()
                
                finding = {
                    'id': item.get('id'),
                    'severity': severity,
                    'finding': item.get('finding'),
                    'cve': item.get('cve'),
                    'cwe': item.get('cwe')
                }
                
                findings.append(finding)
                
                if severity in ['CRITICAL', 'HIGH']:
                    critical_issues.append(finding)
            
            return {
                'tool': 'testssl',
                'total_findings': len(findings),
                'critical_issues': len(critical_issues),
                'findings': findings,
                'critical_findings': critical_issues
            }
        except Exception as e:
            return {
                'tool': 'testssl',
                'error': str(e),
                'findings': []
            }


class WhatWebParser:
    """Parser para resultados de WhatWeb."""
    
    @staticmethod
    def parse_json(json_data: str) -> Dict[str, Any]:
        """Parsea salida JSON de WhatWeb."""
        try:
            data = json.loads(json_data) if isinstance(json_data, str) else json_data
            
            if not isinstance(data, list):
                data = [data]
            
            results = {
                'tool': 'whatweb',
                'targets': []
            }
            
            for target in data:
                plugins = {}
                
                for plugin_name, plugin_data in target.get('plugins', {}).items():
                    if isinstance(plugin_data, dict):
                        plugins[plugin_name] = {
                            'version': plugin_data.get('version', []),
                            'string': plugin_data.get('string', [])
                        }
                    else:
                        plugins[plugin_name] = plugin_data
                
                results['targets'].append({
                    'target': target.get('target'),
                    'http_status': target.get('http_status'),
                    'request_config': target.get('request_config'),
                    'plugins': plugins
                })
            
            return results
        except Exception as e:
            return {
                'tool': 'whatweb',
                'error': str(e),
                'targets': []
            }


class WappalyzerParser:
    """Parser para resultados de Wappalyzer."""
    
    @staticmethod
    def parse_json(json_data: str) -> Dict[str, Any]:
        """Parsea salida JSON de Wappalyzer."""
        try:
            data = json.loads(json_data) if isinstance(json_data, str) else json_data
            
            technologies = []
            categories = {}
            
            for tech in data.get('technologies', []):
                tech_data = {
                    'name': tech.get('name'),
                    'version': tech.get('version'),
                    'categories': tech.get('categories', []),
                    'confidence': tech.get('confidence'),
                    'website': tech.get('website')
                }
                
                technologies.append(tech_data)
                
                # Agrupar por categoría
                for category in tech.get('categories', []):
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(tech.get('name'))
            
            return {
                'tool': 'wappalyzer',
                'total_technologies': len(technologies),
                'technologies': technologies,
                'by_category': categories
            }
        except Exception as e:
            return {
                'tool': 'wappalyzer',
                'error': str(e),
                'technologies': []
            }


class ZAPParser:
    """Parser para resultados de OWASP ZAP."""
    
    @staticmethod
    def parse_xml(xml_file: str) -> Dict[str, Any]:
        """Parsea reporte XML de ZAP."""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            alerts = []
            
            for site in root.findall('.//site'):
                site_url = site.get('name')
                
                for alert in site.findall('.//alertitem'):
                    alerts.append({
                        'site': site_url,
                        'alert': alert.findtext('alert'),
                        'risk': alert.findtext('riskdesc'),
                        'confidence': alert.findtext('confidence'),
                        'description': alert.findtext('desc'),
                        'solution': alert.findtext('solution'),
                        'reference': alert.findtext('reference'),
                        'cweid': alert.findtext('cweid'),
                        'wascid': alert.findtext('wascid'),
                        'uri': alert.findtext('uri'),
                        'param': alert.findtext('param')
                    })
            
            # Agrupar por severidad
            by_risk = {
                'High': [],
                'Medium': [],
                'Low': [],
                'Informational': []
            }
            
            for alert in alerts:
                risk = alert.get('risk', 'Informational')
                if risk in by_risk:
                    by_risk[risk].append(alert)
            
            return {
                'tool': 'zap',
                'total_alerts': len(alerts),
                'by_risk': {
                    'high': len(by_risk['High']),
                    'medium': len(by_risk['Medium']),
                    'low': len(by_risk['Low']),
                    'info': len(by_risk['Informational'])
                },
                'alerts': alerts,
                'alerts_by_risk': by_risk
            }
        except Exception as e:
            return {
                'tool': 'zap',
                'error': str(e),
                'alerts': []
            }
    
    @staticmethod
    def parse_json(json_path: str) -> Dict[str, Any]:
        """Parsea reporte JSON de ZAP."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            alerts = data.get('site', [{}])[0].get('alerts', [])
            
            # Agrupar por riesgo
            by_risk = {
                'High': [],
                'Medium': [],
                'Low': [],
                'Informational': []
            }
            
            for alert in alerts:
                risk = alert.get('risk', 'Informational')
                if risk in by_risk:
                    by_risk[risk].append(alert)
            
            return {
                'tool': 'zap',
                'total_alerts': len(alerts),
                'by_risk': {
                    'high': len(by_risk['High']),
                    'medium': len(by_risk['Medium']),
                    'low': len(by_risk['Low']),
                    'info': len(by_risk['Informational'])
                },
                'alerts': alerts,
                'alerts_by_risk': by_risk
            }
        except Exception as e:
            return {
                'tool': 'zap',
                'error': str(e),
                'alerts': []
            }

