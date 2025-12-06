"""
Mobile Pentesting Parsers
==========================

Parsers para herramientas de pentesting móvil (Android/iOS).
"""

import json
import re
from typing import Dict, List, Any, Optional
import xml.etree.ElementTree as ET


class MobSFParser:
    """Parser para resultados de MobSF (Mobile Security Framework)."""
    
    @staticmethod
    def parse_static_analysis(json_str: str) -> Dict[str, Any]:
        """
        Parsea el análisis estático de MobSF.
        
        MobSF genera JSON con análisis completo de APK/IPA.
        """
        try:
            data = json.loads(json_str)
            
            summary = {
                'tool': 'mobsf',
                'analysis_type': 'static',
                'app_name': data.get('app_name'),
                'package_name': data.get('package_name'),
                'version': data.get('version_name'),
                'target_sdk': data.get('target_sdk'),
                'min_sdk': data.get('min_sdk'),
                'file_name': data.get('file_name'),
                'size': data.get('size'),
                'md5': data.get('md5'),
                'sha1': data.get('sha1'),
                'sha256': data.get('sha256')
            }
            
            # Análisis de seguridad
            security_score = data.get('security_score', 0)
            summary['security_score'] = security_score
            summary['risk_level'] = MobSFParser._calculate_risk_level(security_score)
            
            # Permisos
            permissions = data.get('permissions', {})
            summary['total_permissions'] = len(permissions)
            summary['dangerous_permissions'] = [
                p for p, details in permissions.items()
                if details.get('severity') in ['high', 'dangerous']
            ]
            
            # Certificado
            cert_analysis = data.get('certificate_analysis', {})
            summary['certificate'] = {
                'issued_to': cert_analysis.get('issued_to'),
                'issued_by': cert_analysis.get('issued_by'),
                'validity': cert_analysis.get('validity'),
                'signature_algorithm': cert_analysis.get('signature_algorithm')
            }
            
            # Vulnerabilidades
            manifest_analysis = data.get('manifest_analysis', {})
            code_analysis = data.get('code_analysis', {})
            
            vulnerabilities = []
            
            # Manifest vulnerabilities
            for finding, details in manifest_analysis.items():
                if details.get('severity') in ['high', 'warning']:
                    vulnerabilities.append({
                        'source': 'manifest',
                        'title': finding,
                        'severity': details.get('severity'),
                        'description': details.get('description')
                    })
            
            # Code vulnerabilities
            for finding, details in code_analysis.items():
                if details.get('severity') in ['high', 'warning']:
                    vulnerabilities.append({
                        'source': 'code',
                        'title': finding,
                        'severity': details.get('severity'),
                        'description': details.get('description')
                    })
            
            summary['vulnerabilities'] = vulnerabilities
            summary['total_vulnerabilities'] = len(vulnerabilities)
            
            # Network security
            network_security = data.get('network_security', {})
            summary['network_security'] = {
                'clear_text_traffic': network_security.get('clear_text_traffic', False),
                'certificate_pinning': network_security.get('certificate_pinning', False)
            }
            
            # URLs encontradas
            urls = data.get('urls', [])
            summary['urls_found'] = len(urls)
            summary['urls'] = urls[:20]  # Primeros 20
            
            # API keys / secrets
            secrets = data.get('secrets', [])
            summary['secrets_found'] = len(secrets)
            summary['secrets'] = secrets
            
            return summary
            
        except json.JSONDecodeError as e:
            return {
                'tool': 'mobsf',
                'error': f'Failed to parse MobSF JSON: {str(e)}'
            }
    
    @staticmethod
    def _calculate_risk_level(score: int) -> str:
        """Calcula el nivel de riesgo basado en el score."""
        if score >= 80:
            return 'low'
        elif score >= 60:
            return 'medium'
        elif score >= 40:
            return 'high'
        else:
            return 'critical'


class APKToolParser:
    """Parser para resultados de APKTool."""
    
    @staticmethod
    def parse_manifest(manifest_path: str) -> Dict[str, Any]:
        """
        Parsea el AndroidManifest.xml decompilado.
        """
        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()
            
            manifest_data = {
                'tool': 'apktool',
                'package': root.get('package'),
                'version_code': root.get('{http://schemas.android.com/apk/res/android}versionCode'),
                'version_name': root.get('{http://schemas.android.com/apk/res/android}versionName')
            }
            
            # Permisos
            permissions = []
            for perm in root.findall('.//uses-permission'):
                perm_name = perm.get('{http://schemas.android.com/apk/res/android}name')
                if perm_name:
                    permissions.append(perm_name.split('.')[-1])
            
            manifest_data['permissions'] = permissions
            manifest_data['total_permissions'] = len(permissions)
            
            # Activities exportadas
            exported_activities = []
            for activity in root.findall('.//activity'):
                exported = activity.get('{http://schemas.android.com/apk/res/android}exported')
                name = activity.get('{http://schemas.android.com/apk/res/android}name')
                if exported == 'true' and name:
                    exported_activities.append(name)
            
            manifest_data['exported_activities'] = exported_activities
            
            # Services exportados
            exported_services = []
            for service in root.findall('.//service'):
                exported = service.get('{http://schemas.android.com/apk/res/android}exported')
                name = service.get('{http://schemas.android.com/apk/res/android}name')
                if exported == 'true' and name:
                    exported_services.append(name)
            
            manifest_data['exported_services'] = exported_services
            
            # Receivers exportados
            exported_receivers = []
            for receiver in root.findall('.//receiver'):
                exported = receiver.get('{http://schemas.android.com/apk/res/android}exported')
                name = receiver.get('{http://schemas.android.com/apk/res/android}name')
                if exported == 'true' and name:
                    exported_receivers.append(name)
            
            manifest_data['exported_receivers'] = exported_receivers
            
            # Backup allowed
            application = root.find('.//application')
            if application is not None:
                backup_allowed = application.get('{http://schemas.android.com/apk/res/android}allowBackup')
                manifest_data['backup_allowed'] = backup_allowed == 'true'
                
                debuggable = application.get('{http://schemas.android.com/apk/res/android}debuggable')
                manifest_data['debuggable'] = debuggable == 'true'
            
            return manifest_data
            
        except Exception as e:
            return {
                'tool': 'apktool',
                'error': f'Failed to parse manifest: {str(e)}'
            }
    
    @staticmethod
    def parse_strings(strings_xml_path: str) -> Dict[str, Any]:
        """Parsea strings.xml para encontrar secrets."""
        try:
            tree = ET.parse(strings_xml_path)
            root = tree.getroot()
            
            strings = []
            secrets = []
            
            # Keywords para detectar secrets
            secret_keywords = [
                'api_key', 'apikey', 'secret', 'password', 'token',
                'auth', 'credential', 'private', 'aws', 'azure'
            ]
            
            for string in root.findall('.//string'):
                name = string.get('name', '')
                value = string.text or ''
                
                strings.append({'name': name, 'value': value})
                
                # Detectar posibles secrets
                for keyword in secret_keywords:
                    if keyword in name.lower() or keyword in value.lower():
                        secrets.append({
                            'name': name,
                            'value': value,
                            'matched_keyword': keyword
                        })
                        break
            
            return {
                'tool': 'apktool',
                'total_strings': len(strings),
                'secrets_found': len(secrets),
                'secrets': secrets
            }
            
        except Exception as e:
            return {
                'tool': 'apktool',
                'error': f'Failed to parse strings.xml: {str(e)}'
            }


class FridaParser:
    """Parser para scripts de Frida."""
    
    @staticmethod
    def parse_hook_output(output: str) -> Dict[str, Any]:
        """
        Parsea la salida de un script de Frida.
        """
        hooks = []
        
        # Buscar líneas con llamadas interceptadas
        for line in output.split('\n'):
            # Formato típico: [*] Called: function_name(arg1, arg2) -> return_value
            match = re.match(r'\[\*\]\s+Called:\s+(\S+)\((.*?)\)\s*->\s*(.+)', line)
            if match:
                hooks.append({
                    'function': match.group(1),
                    'arguments': match.group(2),
                    'return_value': match.group(3).strip()
                })
            
            # Buscar también formato JSON
            if line.strip().startswith('{'):
                try:
                    hook_data = json.loads(line)
                    hooks.append(hook_data)
                except json.JSONDecodeError:
                    pass
        
        return {
            'tool': 'frida',
            'total_hooks': len(hooks),
            'hooks': hooks
        }


class ObjectionParser:
    """Parser para resultados de Objection."""
    
    @staticmethod
    def parse_output(output: str, command: str) -> Dict[str, Any]:
        """
        Parsea la salida de comandos de Objection.
        """
        results = {
            'tool': 'objection',
            'command': command,
            'output': output
        }
        
        # Parsear según el comando
        if 'env' in command:
            # Extraer información del entorno
            env_vars = {}
            for line in output.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    env_vars[key.strip()] = value.strip()
            results['environment'] = env_vars
        
        elif 'list' in command and 'activities' in command:
            # Extraer lista de activities
            activities = []
            for line in output.split('\n'):
                if line.strip() and not line.startswith('['):
                    activities.append(line.strip())
            results['activities'] = activities
            results['total'] = len(activities)
        
        elif 'list' in command and 'classes' in command:
            # Extraer lista de clases
            classes = []
            for line in output.split('\n'):
                if line.strip() and not line.startswith('['):
                    classes.append(line.strip())
            results['classes'] = classes[:100]  # Primeros 100
            results['total'] = len(classes)
        
        elif 'ssl' in command.lower() or 'pinning' in command.lower():
            # SSL pinning bypass
            results['ssl_pinning_bypassed'] = 'Unpinning' in output or 'success' in output.lower()
        
        return results

