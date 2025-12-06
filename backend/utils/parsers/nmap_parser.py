"""
Nmap Results Parser
===================

Parser completo para resultados de Nmap en formato XML y texto.
"""

import xml.etree.ElementTree as ET
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class NmapParser:
    """Parser para resultados de Nmap."""
    
    @staticmethod
    def parse_xml(xml_file: str) -> Dict[str, Any]:
        """
        Parsea archivo XML de Nmap.
        
        Args:
            xml_file: Path al archivo XML
        
        Returns:
            Dict con resultados estructurados
        """
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            results = {
                'scan_info': NmapParser._parse_scan_info(root),
                'hosts': []
            }
            
            # Parsear cada host
            for host in root.findall('host'):
                host_data = NmapParser._parse_host(host)
                if host_data:
                    results['hosts'].append(host_data)
            
            # Estadísticas
            results['summary'] = {
                'total_hosts': len(results['hosts']),
                'up_hosts': len([h for h in results['hosts'] if h['status'] == 'up']),
                'total_ports': sum(len(h.get('ports', [])) for h in results['hosts']),
                'open_ports': sum(
                    len([p for p in h.get('ports', []) if p['state'] == 'open'])
                    for h in results['hosts']
                )
            }
            
            return results
            
        except Exception as e:
            return {
                'error': f'Failed to parse Nmap XML: {str(e)}',
                'hosts': []
            }
    
    @staticmethod
    def _parse_scan_info(root: ET.Element) -> Dict[str, Any]:
        """Parsea información del scan."""
        scaninfo = root.find('scaninfo')
        if scaninfo is None:
            return {}
        
        return {
            'type': scaninfo.get('type'),
            'protocol': scaninfo.get('protocol'),
            'numservices': scaninfo.get('numservices'),
            'services': scaninfo.get('services')
        }
    
    @staticmethod
    def _parse_host(host: ET.Element) -> Optional[Dict[str, Any]]:
        """Parsea información de un host."""
        # Estado del host
        status = host.find('status')
        if status is None:
            return None
        
        host_data = {
            'status': status.get('state'),
            'reason': status.get('reason')
        }
        
        # Direcciones (IP, MAC)
        addresses = {}
        for addr in host.findall('address'):
            addr_type = addr.get('addrtype')
            addresses[addr_type] = {
                'addr': addr.get('addr'),
                'vendor': addr.get('vendor')
            }
        host_data['addresses'] = addresses
        
        # Hostnames
        hostnames = []
        for hostname in host.findall('.//hostname'):
            hostnames.append({
                'name': hostname.get('name'),
                'type': hostname.get('type')
            })
        host_data['hostnames'] = hostnames
        
        # Puertos
        ports = []
        for port in host.findall('.//port'):
            port_data = NmapParser._parse_port(port)
            if port_data:
                ports.append(port_data)
        host_data['ports'] = ports
        
        # OS Detection
        os_matches = []
        for osmatch in host.findall('.//osmatch'):
            os_matches.append({
                'name': osmatch.get('name'),
                'accuracy': osmatch.get('accuracy'),
                'line': osmatch.get('line')
            })
        if os_matches:
            host_data['os'] = os_matches
        
        # Scripts NSE
        host_scripts = []
        for script in host.findall('.//hostscript/script'):
            host_scripts.append({
                'id': script.get('id'),
                'output': script.get('output')
            })
        if host_scripts:
            host_data['host_scripts'] = host_scripts
        
        return host_data
    
    @staticmethod
    def _parse_port(port: ET.Element) -> Optional[Dict[str, Any]]:
        """Parsea información de un puerto."""
        state = port.find('state')
        if state is None:
            return None
        
        port_data = {
            'port': port.get('portid'),
            'protocol': port.get('protocol'),
            'state': state.get('state'),
            'reason': state.get('reason')
        }
        
        # Servicio
        service = port.find('service')
        if service is not None:
            port_data['service'] = {
                'name': service.get('name'),
                'product': service.get('product'),
                'version': service.get('version'),
                'extrainfo': service.get('extrainfo'),
                'ostype': service.get('ostype'),
                'method': service.get('method'),
                'conf': service.get('conf')
            }
        
        # Scripts NSE
        scripts = []
        for script in port.findall('script'):
            script_data = {
                'id': script.get('id'),
                'output': script.get('output')
            }
            
            # Parsear tablas/elementos del script
            elements = {}
            for elem in script.findall('.//elem'):
                key = elem.get('key')
                if key:
                    elements[key] = elem.text
            if elements:
                script_data['elements'] = elements
            
            scripts.append(script_data)
        
        if scripts:
            port_data['scripts'] = scripts
        
        return port_data
    
    @staticmethod
    def parse_text_output(output: str) -> Dict[str, Any]:
        """
        Parsea salida de texto de Nmap.
        
        Args:
            output: Output de texto de Nmap
        
        Returns:
            Dict con resultados básicos
        """
        results = {
            'hosts': [],
            'summary': {}
        }
        
        # Extraer hosts y puertos con regex
        host_blocks = re.split(r'Nmap scan report for ', output)[1:]
        
        for block in host_blocks:
            lines = block.split('\n')
            if not lines:
                continue
            
            # Primera línea tiene el host
            host_line = lines[0].strip()
            host_match = re.search(r'([\w\.-]+)\s*\(?([\d\.]+)?\)?', host_line)
            
            if not host_match:
                continue
            
            hostname = host_match.group(1)
            ip = host_match.group(2) or hostname
            
            host_data = {
                'hostname': hostname,
                'ip': ip,
                'ports': []
            }
            
            # Buscar puertos
            in_port_section = False
            for line in lines[1:]:
                if 'PORT' in line and 'STATE' in line and 'SERVICE' in line:
                    in_port_section = True
                    continue
                
                if in_port_section:
                    port_match = re.match(
                        r'(\d+)/(tcp|udp)\s+(\w+)\s+(\S+)',
                        line.strip()
                    )
                    if port_match:
                        host_data['ports'].append({
                            'port': port_match.group(1),
                            'protocol': port_match.group(2),
                            'state': port_match.group(3),
                            'service': port_match.group(4)
                        })
                    elif line.strip() and not line.startswith('|'):
                        in_port_section = False
            
            if host_data['ports']:
                results['hosts'].append(host_data)
        
        # Resumen
        results['summary'] = {
            'total_hosts': len(results['hosts']),
            'total_ports': sum(len(h['ports']) for h in results['hosts'])
        }
        
        return results
    
    @staticmethod
    def extract_vulnerabilities(parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrae vulnerabilidades de scripts NSE.
        
        Args:
            parsed_data: Datos parseados de Nmap
        
        Returns:
            Lista de vulnerabilidades encontradas
        """
        vulnerabilities = []
        
        for host in parsed_data.get('hosts', []):
            host_ip = host.get('addresses', {}).get('ipv4', {}).get('addr', 'unknown')
            
            # Vulnerabilidades en puertos
            for port in host.get('ports', []):
                port_num = port.get('port')
                service = port.get('service', {}).get('name', 'unknown')
                
                for script in port.get('scripts', []):
                    script_id = script.get('id', '')
                    output = script.get('output', '')
                    
                    # Detectar scripts de vulnerabilidades
                    if any(keyword in script_id for keyword in 
                           ['vuln', 'cve', 'exploit', 'dos', 'backdoor']):
                        
                        severity = NmapParser._determine_severity(script_id, output)
                        
                        vulnerabilities.append({
                            'host': host_ip,
                            'port': port_num,
                            'service': service,
                            'script': script_id,
                            'description': output,
                            'severity': severity
                        })
            
            # Vulnerabilidades a nivel de host
            for script in host.get('host_scripts', []):
                script_id = script.get('id', '')
                output = script.get('output', '')
                
                if any(keyword in script_id for keyword in 
                       ['vuln', 'cve', 'exploit', 'smb', 'ms']):
                    
                    severity = NmapParser._determine_severity(script_id, output)
                    
                    vulnerabilities.append({
                        'host': host_ip,
                        'port': None,
                        'service': 'host',
                        'script': script_id,
                        'description': output,
                        'severity': severity
                    })
        
        return vulnerabilities
    
    @staticmethod
    def _determine_severity(script_id: str, output: str) -> str:
        """Determina severidad de vulnerabilidad."""
        output_lower = output.lower()
        script_lower = script_id.lower()
        
        # Critical
        if any(keyword in output_lower for keyword in 
               ['critical', 'remote code execution', 'rce', 'unauthenticated']):
            return 'CRITICAL'
        
        # High
        if any(keyword in script_lower for keyword in 
               ['ms17-010', 'eternalblue', 'shellshock', 'heartbleed']):
            return 'HIGH'
        
        if any(keyword in output_lower for keyword in 
               ['vulnerable', 'exploit', 'high']):
            return 'HIGH'
        
        # Medium
        if any(keyword in output_lower for keyword in 
               ['medium', 'information disclosure', 'weak']):
            return 'MEDIUM'
        
        # Low
        return 'LOW'


class RustScanParser:
    """Parser para resultados de RustScan."""
    
    @staticmethod
    def parse_output(output: str) -> Dict[str, Any]:
        """
        Parsea salida de RustScan.
        
        Formato esperado:
        Open 192.168.1.1:22
        Open 192.168.1.1:80
        """
        hosts = {}
        
        for line in output.split('\n'):
            match = re.match(r'Open\s+([\d\.]+):(\d+)', line)
            if match:
                ip = match.group(1)
                port = match.group(2)
                
                if ip not in hosts:
                    hosts[ip] = {'ip': ip, 'ports': []}
                
                hosts[ip]['ports'].append({
                    'port': port,
                    'state': 'open'
                })
        
        return {
            'tool': 'rustscan',
            'hosts': list(hosts.values()),
            'summary': {
                'total_hosts': len(hosts),
                'total_open_ports': sum(len(h['ports']) for h in hosts.values())
            }
        }


class MasscanParser:
    """Parser para resultados de Masscan."""
    
    @staticmethod
    def parse_output(output: str) -> Dict[str, Any]:
        """
        Parsea salida de Masscan.
        
        Formato esperado:
        Discovered open port 80/tcp on 192.168.1.1
        """
        hosts = {}
        
        for line in output.split('\n'):
            match = re.match(
                r'Discovered open port (\d+)/(tcp|udp) on ([\d\.]+)',
                line
            )
            if match:
                port = match.group(1)
                protocol = match.group(2)
                ip = match.group(3)
                
                if ip not in hosts:
                    hosts[ip] = {'ip': ip, 'ports': []}
                
                hosts[ip]['ports'].append({
                    'port': port,
                    'protocol': protocol,
                    'state': 'open'
                })
        
        return {
            'tool': 'masscan',
            'hosts': list(hosts.values()),
            'summary': {
                'total_hosts': len(hosts),
                'total_open_ports': sum(len(h['ports']) for h in hosts.values())
            }
        }

