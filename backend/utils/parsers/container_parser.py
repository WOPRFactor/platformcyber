"""
Container & Kubernetes Security Parsers
========================================

Parsers para herramientas de seguridad de contenedores y Kubernetes.
"""

import json
import re
from typing import Dict, List, Any, Optional


class TrivyParser:
    """Parser para resultados de Trivy."""
    
    @staticmethod
    def parse_json(json_str: str) -> Dict[str, Any]:
        """
        Parsea la salida JSON de Trivy.
        """
        try:
            data = json.loads(json_str)
            
            results = data.get('Results', [])
            
            all_vulnerabilities = []
            by_severity = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'UNKNOWN': 0}
            
            for result in results:
                target = result.get('Target', 'unknown')
                vulns = result.get('Vulnerabilities', [])
                
                for vuln in vulns:
                    severity = vuln.get('Severity', 'UNKNOWN')
                    by_severity[severity] = by_severity.get(severity, 0) + 1
                    
                    all_vulnerabilities.append({
                        'target': target,
                        'vuln_id': vuln.get('VulnerabilityID'),
                        'package_name': vuln.get('PkgName'),
                        'installed_version': vuln.get('InstalledVersion'),
                        'fixed_version': vuln.get('FixedVersion'),
                        'severity': severity,
                        'title': vuln.get('Title'),
                        'description': vuln.get('Description', '')[:200]  # Primeros 200 chars
                    })
            
            # Ordenar por severidad
            severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'UNKNOWN': 4}
            all_vulnerabilities.sort(key=lambda x: severity_order.get(x['severity'], 5))
            
            return {
                'tool': 'trivy',
                'total_vulnerabilities': len(all_vulnerabilities),
                'by_severity': by_severity,
                'vulnerabilities': all_vulnerabilities[:100],  # Primeros 100
                'metadata': data.get('Metadata', {})
            }
            
        except json.JSONDecodeError as e:
            return {
                'tool': 'trivy',
                'error': f'Failed to parse Trivy JSON: {str(e)}'
            }


class GrypeParser:
    """Parser para resultados de Grype."""
    
    @staticmethod
    def parse_json(json_str: str) -> Dict[str, Any]:
        """
        Parsea la salida JSON de Grype.
        """
        try:
            data = json.loads(json_str)
            
            matches = data.get('matches', [])
            
            vulnerabilities = []
            by_severity = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'Negligible': 0}
            
            for match in matches:
                vulnerability = match.get('vulnerability', {})
                artifact = match.get('artifact', {})
                
                severity = vulnerability.get('severity', 'Unknown')
                by_severity[severity] = by_severity.get(severity, 0) + 1
                
                vulnerabilities.append({
                    'vuln_id': vulnerability.get('id'),
                    'package_name': artifact.get('name'),
                    'package_version': artifact.get('version'),
                    'package_type': artifact.get('type'),
                    'severity': severity,
                    'fix_versions': vulnerability.get('fix', {}).get('versions', []),
                    'urls': vulnerability.get('urls', [])
                })
            
            return {
                'tool': 'grype',
                'total_vulnerabilities': len(vulnerabilities),
                'by_severity': by_severity,
                'vulnerabilities': vulnerabilities[:100],
                'source': data.get('source', {})
            }
            
        except json.JSONDecodeError as e:
            return {
                'tool': 'grype',
                'error': f'Failed to parse Grype JSON: {str(e)}'
            }


class SyftParser:
    """Parser para resultados de Syft (SBOM generation)."""
    
    @staticmethod
    def parse_json(json_str: str) -> Dict[str, Any]:
        """
        Parsea el SBOM JSON de Syft.
        """
        try:
            data = json.loads(json_str)
            
            artifacts = data.get('artifacts', [])
            
            # Agrupar por tipo
            by_type = {}
            by_language = {}
            
            for artifact in artifacts:
                artifact_type = artifact.get('type', 'unknown')
                language = artifact.get('language', 'unknown')
                
                by_type[artifact_type] = by_type.get(artifact_type, 0) + 1
                if language != 'unknown':
                    by_language[language] = by_language.get(language, 0) + 1
            
            return {
                'tool': 'syft',
                'total_artifacts': len(artifacts),
                'by_type': by_type,
                'by_language': by_language,
                'artifacts': artifacts[:100],  # Primeros 100
                'source': data.get('source', {}),
                'descriptor': data.get('descriptor', {})
            }
            
        except json.JSONDecodeError as e:
            return {
                'tool': 'syft',
                'error': f'Failed to parse Syft JSON: {str(e)}'
            }


class KubeHunterParser:
    """Parser para resultados de Kube-hunter."""
    
    @staticmethod
    def parse_json(json_str: str) -> Dict[str, Any]:
        """
        Parsea la salida JSON de Kube-hunter.
        """
        try:
            data = json.loads(json_str)
            
            vulnerabilities = data.get('vulnerabilities', [])
            services = data.get('services', [])
            hunter_statistics = data.get('hunter_statistics', [])
            
            # Agrupar vulnerabilidades por severidad
            by_severity = {'high': 0, 'medium': 0, 'low': 0}
            
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'low').lower()
                by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Extraer vulnerabilidades críticas
            critical_vulns = [
                v for v in vulnerabilities
                if v.get('severity', '').lower() in ['high', 'critical']
            ]
            
            return {
                'tool': 'kube-hunter',
                'total_vulnerabilities': len(vulnerabilities),
                'by_severity': by_severity,
                'critical_vulnerabilities': critical_vulns,
                'total_services': len(services),
                'services': services,
                'hunter_statistics': hunter_statistics,
                'nodes': data.get('nodes', [])
            }
            
        except json.JSONDecodeError as e:
            return {
                'tool': 'kube-hunter',
                'error': f'Failed to parse Kube-hunter JSON: {str(e)}'
            }


class KubeBenchParser:
    """Parser para resultados de Kube-bench (CIS Kubernetes Benchmark)."""
    
    @staticmethod
    def parse_json(json_str: str) -> Dict[str, Any]:
        """
        Parsea la salida JSON de Kube-bench.
        """
        try:
            data = json.loads(json_str)
            
            controls = data.get('Controls', [])
            
            totals = {
                'total_pass': data.get('Totals', {}).get('total_pass', 0),
                'total_fail': data.get('Totals', {}).get('total_fail', 0),
                'total_warn': data.get('Totals', {}).get('total_warn', 0),
                'total_info': data.get('Totals', {}).get('total_info', 0)
            }
            
            # Extraer controles fallidos
            failed_controls = []
            warned_controls = []
            
            for control in controls:
                tests = control.get('tests', [])
                for test in tests:
                    results = test.get('results', [])
                    for result in results:
                        if result.get('status') == 'FAIL':
                            failed_controls.append({
                                'test_number': result.get('test_number'),
                                'test_desc': result.get('test_desc'),
                                'remediation': result.get('remediation'),
                                'scored': result.get('scored')
                            })
                        elif result.get('status') == 'WARN':
                            warned_controls.append({
                                'test_number': result.get('test_number'),
                                'test_desc': result.get('test_desc')
                            })
            
            # Calcular compliance score
            total_tests = sum(totals.values())
            compliance_score = (totals['total_pass'] / total_tests * 100) if total_tests > 0 else 0
            
            return {
                'tool': 'kube-bench',
                'totals': totals,
                'compliance_score': round(compliance_score, 2),
                'failed_controls': failed_controls,
                'warned_controls': warned_controls,
                'summary': data.get('Totals', {})
            }
            
        except json.JSONDecodeError as e:
            return {
                'tool': 'kube-bench',
                'error': f'Failed to parse Kube-bench JSON: {str(e)}'
            }


class KubescapeParser:
    """Parser para resultados de Kubescape."""
    
    @staticmethod
    def parse_json(json_str: str) -> Dict[str, Any]:
        """
        Parsea la salida JSON de Kubescape.
        """
        try:
            data = json.loads(json_str)
            
            summary_details = data.get('summaryDetails', {})
            
            controls_info = summary_details.get('controls', {})
            
            # Risk score
            risk_score = summary_details.get('score', 0)
            
            # Compliance
            compliance_score = summary_details.get('complianceScore', 0)
            
            # Controles por severidad
            controls_by_severity = {}
            frameworks = data.get('frameworks', [])
            
            for framework in frameworks:
                controls = framework.get('controls', [])
                for control in controls:
                    severity = control.get('severity', 'unknown')
                    status = control.get('status', 'unknown')
                    
                    if severity not in controls_by_severity:
                        controls_by_severity[severity] = {'passed': 0, 'failed': 0}
                    
                    if status == 'passed':
                        controls_by_severity[severity]['passed'] += 1
                    else:
                        controls_by_severity[severity]['failed'] += 1
            
            # Recursos escaneados
            resources_summary = summary_details.get('resources', {})
            
            return {
                'tool': 'kubescape',
                'risk_score': risk_score,
                'compliance_score': compliance_score,
                'controls_summary': controls_info,
                'controls_by_severity': controls_by_severity,
                'resources_scanned': resources_summary.get('totalResources', 0),
                'frameworks': [f.get('name') for f in frameworks]
            }
            
        except json.JSONDecodeError as e:
            return {
                'tool': 'kubescape',
                'error': f'Failed to parse Kubescape JSON: {str(e)}'
            }


class DockerBenchParser:
    """Parser para resultados de Docker Bench for Security."""
    
    @staticmethod
    def parse_output(output: str) -> Dict[str, Any]:
        """
        Parsea la salida de Docker Bench for Security.
        """
        results = {
            'tool': 'docker-bench',
            'pass': [],
            'warn': [],
            'info': [],
            'note': []
        }
        
        for line in output.split('\n'):
            if '[PASS]' in line:
                results['pass'].append(line.replace('[PASS]', '').strip())
            elif '[WARN]' in line:
                results['warn'].append(line.replace('[WARN]', '').strip())
            elif '[INFO]' in line:
                results['info'].append(line.replace('[INFO]', '').strip())
            elif '[NOTE]' in line:
                results['note'].append(line.replace('[NOTE]', '').strip())
        
        results['totals'] = {
            'pass': len(results['pass']),
            'warn': len(results['warn']),
            'info': len(results['info']),
            'note': len(results['note'])
        }
        
        return results

