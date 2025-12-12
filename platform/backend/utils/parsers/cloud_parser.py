"""
Cloud Pentesting Parsers
=========================

Parsers para herramientas de pentesting en entornos cloud.
"""

import json
import re
from typing import Dict, List, Any, Optional


class PacuParser:
    """Parser para resultados de Pacu (AWS)."""
    
    @staticmethod
    def parse_module_output(output: str, module_name: str) -> Dict[str, Any]:
        """
        Parsea la salida de un módulo de Pacu.
        
        Pacu usa formato de texto estructurado.
        """
        results = {
            'tool': 'pacu',
            'module': module_name,
            'findings': [],
            'summary': {}
        }
        
        # Extraer findings
        if '[+]' in output:
            findings = re.findall(r'\[\+\]\s*(.+)', output)
            results['findings'] = findings
        
        # Extraer warnings
        if '[!]' in output:
            warnings = re.findall(r'\[\!\]\s*(.+)', output)
            results['warnings'] = warnings
        
        # Extraer errores
        if '[-]' in output:
            errors = re.findall(r'\[-\]\s*(.+)', output)
            results['errors'] = errors
        
        # Extraer recursos encontrados
        if 'Found' in output or 'Discovered' in output:
            count_matches = re.findall(r'Found\s+(\d+)\s+(.+)', output)
            for count, resource_type in count_matches:
                results['summary'][resource_type] = int(count)
        
        return results


class ScoutSuiteParser:
    """Parser para resultados de ScoutSuite (Multi-cloud)."""
    
    @staticmethod
    def parse_json_report(json_path: str) -> Dict[str, Any]:
        """
        Parsea el reporte JSON de ScoutSuite.
        
        ScoutSuite genera reportes muy completos en JSON.
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            summary = {
                'tool': 'scoutsuite',
                'provider': data.get('provider', 'unknown'),
                'account_id': data.get('account_id'),
                'timestamp': data.get('last_run', {}).get('time'),
                'findings_summary': {},
                'services_analyzed': [],
                'total_findings': 0
            }
            
            # Extraer findings por servicio
            services = data.get('services', {})
            for service_name, service_data in services.items():
                summary['services_analyzed'].append(service_name)
                
                findings = service_data.get('findings', {})
                if findings:
                    summary['findings_summary'][service_name] = {}
                    
                    for finding_id, finding_data in findings.items():
                        severity = finding_data.get('level', 'info')
                        items = finding_data.get('items', [])
                        flagged_items = finding_data.get('flagged_items', 0)
                        
                        if severity not in summary['findings_summary'][service_name]:
                            summary['findings_summary'][service_name][severity] = 0
                        
                        summary['findings_summary'][service_name][severity] += flagged_items
                        summary['total_findings'] += flagged_items
            
            # Extraer top findings
            summary['top_findings'] = []
            for service_name, service_data in services.items():
                findings = service_data.get('findings', {})
                for finding_id, finding_data in findings.items():
                    if finding_data.get('level') in ['danger', 'warning']:
                        summary['top_findings'].append({
                            'service': service_name,
                            'finding_id': finding_id,
                            'description': finding_data.get('description'),
                            'level': finding_data.get('level'),
                            'flagged_items': finding_data.get('flagged_items', 0)
                        })
            
            # Ordenar por severidad y cantidad
            summary['top_findings'].sort(
                key=lambda x: (0 if x['level'] == 'danger' else 1, -x['flagged_items'])
            )
            summary['top_findings'] = summary['top_findings'][:20]  # Top 20
            
            return summary
            
        except Exception as e:
            return {
                'tool': 'scoutsuite',
                'error': f'Failed to parse ScoutSuite report: {str(e)}'
            }


class ProwlerParser:
    """Parser para resultados de Prowler (AWS, Azure, GCP)."""
    
    @staticmethod
    def parse_json_report(json_path: str) -> Dict[str, Any]:
        """
        Parsea el reporte JSON de Prowler.
        
        Prowler v3+ genera JSON estructurado.
        """
        try:
            with open(json_path, 'r') as f:
                # Prowler puede generar JSON Lines o array JSON
                content = f.read()
                
                # Intentar parsear como JSON array
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    # Si falla, intentar JSON Lines
                    data = [json.loads(line) for line in content.split('\n') if line.strip()]
            
            summary = {
                'tool': 'prowler',
                'total_checks': len(data),
                'findings_by_severity': {},
                'findings_by_service': {},
                'failed_checks': 0,
                'passed_checks': 0,
                'critical_findings': [],
                'high_findings': []
            }
            
            for check in data:
                status = check.get('Status', check.get('status', 'UNKNOWN'))
                severity = check.get('Severity', check.get('severity', 'unknown')).upper()
                service = check.get('ServiceName', check.get('service_name', 'unknown'))
                
                # Contar por status
                if status in ['FAIL', 'FAILED']:
                    summary['failed_checks'] += 1
                elif status in ['PASS', 'PASSED']:
                    summary['passed_checks'] += 1
                
                # Contar por severidad (solo fallos)
                if status in ['FAIL', 'FAILED']:
                    if severity not in summary['findings_by_severity']:
                        summary['findings_by_severity'][severity] = 0
                    summary['findings_by_severity'][severity] += 1
                    
                    # Contar por servicio
                    if service not in summary['findings_by_service']:
                        summary['findings_by_service'][service] = 0
                    summary['findings_by_service'][service] += 1
                    
                    # Extraer críticos y altos
                    finding = {
                        'check_id': check.get('CheckID', check.get('check_id')),
                        'check_title': check.get('CheckTitle', check.get('check_title')),
                        'service': service,
                        'severity': severity,
                        'resource': check.get('ResourceId', check.get('resource_id')),
                        'region': check.get('Region', check.get('region')),
                        'description': check.get('Description', check.get('description'))
                    }
                    
                    if severity == 'CRITICAL':
                        summary['critical_findings'].append(finding)
                    elif severity == 'HIGH':
                        summary['high_findings'].append(finding)
            
            # Limitar a top 50 de cada categoría
            summary['critical_findings'] = summary['critical_findings'][:50]
            summary['high_findings'] = summary['high_findings'][:50]
            
            return summary
            
        except Exception as e:
            return {
                'tool': 'prowler',
                'error': f'Failed to parse Prowler report: {str(e)}'
            }


class AzureHoundParser:
    """Parser para resultados de AzureHound."""
    
    @staticmethod
    def parse_json_output(json_path: str) -> Dict[str, Any]:
        """
        Parsea la salida JSON de AzureHound.
        
        AzureHound genera archivos JSON para importar a BloodHound.
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            summary = {
                'tool': 'azurehound',
                'metadata': data.get('meta', {}),
                'data_types': {},
                'total_objects': 0
            }
            
            # AzureHound genera diferentes tipos de datos
            data_section = data.get('data', [])
            
            # Contar por tipo
            for item in data_section:
                item_type = item.get('kind', item.get('type', 'unknown'))
                
                if item_type not in summary['data_types']:
                    summary['data_types'][item_type] = 0
                summary['data_types'][item_type] += 1
                summary['total_objects'] += 1
            
            # Extraer información de tenant
            summary['tenant_info'] = {
                'tenant_id': data.get('meta', {}).get('tenantId'),
                'collection_method': data.get('meta', {}).get('methods'),
                'collection_date': data.get('meta', {}).get('collectionDate')
            }
            
            return summary
            
        except Exception as e:
            return {
                'tool': 'azurehound',
                'error': f'Failed to parse AzureHound output: {str(e)}'
            }


class ROADtoolsParser:
    """Parser para resultados de ROADtools (Azure AD)."""
    
    @staticmethod
    def parse_database_summary(db_path: str) -> Dict[str, Any]:
        """
        Extrae resumen de la base de datos de ROADtools.
        
        ROADtools usa SQLite para almacenar datos.
        """
        try:
            import sqlite3
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            summary = {
                'tool': 'roadtools',
                'database': db_path,
                'stats': {}
            }
            
            # Contar usuarios
            cursor.execute("SELECT COUNT(*) FROM Users")
            summary['stats']['total_users'] = cursor.fetchone()[0]
            
            # Contar grupos
            cursor.execute("SELECT COUNT(*) FROM Groups")
            summary['stats']['total_groups'] = cursor.fetchone()[0]
            
            # Contar aplicaciones
            cursor.execute("SELECT COUNT(*) FROM Applications")
            summary['stats']['total_applications'] = cursor.fetchone()[0]
            
            # Contar service principals
            cursor.execute("SELECT COUNT(*) FROM ServicePrincipals")
            summary['stats']['total_service_principals'] = cursor.fetchone()[0]
            
            # Contar devices
            cursor.execute("SELECT COUNT(*) FROM Devices")
            summary['stats']['total_devices'] = cursor.fetchone()[0]
            
            # Usuarios con roles de administrador
            cursor.execute("""
                SELECT COUNT(DISTINCT ur.userId) 
                FROM UserRoles ur
                JOIN DirectoryRoles dr ON ur.roleId = dr.id
                WHERE dr.displayName LIKE '%Admin%'
            """)
            summary['stats']['admin_users'] = cursor.fetchone()[0]
            
            conn.close()
            
            return summary
            
        except Exception as e:
            return {
                'tool': 'roadtools',
                'error': f'Failed to parse ROADtools database: {str(e)}'
            }
    
    @staticmethod
    def parse_gui_export(json_path: str) -> Dict[str, Any]:
        """
        Parsea exportaciones JSON de roadrecon gui.
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # El formato depende de qué se exportó
            return {
                'tool': 'roadtools',
                'export_type': 'gui_export',
                'data': data,
                'total_items': len(data) if isinstance(data, list) else 1
            }
            
        except Exception as e:
            return {
                'tool': 'roadtools',
                'error': f'Failed to parse ROADtools GUI export: {str(e)}'
            }


class CloudEnumParser:
    """Parser genérico para enumeración de recursos cloud."""
    
    @staticmethod
    def parse_resource_list(output: str, resource_type: str) -> Dict[str, Any]:
        """
        Parsea listados de recursos cloud (AWS CLI, Azure CLI, gcloud).
        """
        resources = []
        
        # Intentar parsear como JSON
        try:
            data = json.loads(output)
            if isinstance(data, list):
                resources = data
            elif isinstance(data, dict):
                # AWS CLI suele retornar {ResourceType: [recursos]}
                for key, value in data.items():
                    if isinstance(value, list):
                        resources.extend(value)
        except json.JSONDecodeError:
            # Si no es JSON, extraer líneas
            resources = [line.strip() for line in output.split('\n') if line.strip()]
        
        return {
            'resource_type': resource_type,
            'total_resources': len(resources),
            'resources': resources[:100]  # Primeros 100
        }

