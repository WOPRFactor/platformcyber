"""
Nmap Parser
===========

Parser para archivos XML de Nmap.
Extrae información de hosts, puertos abiertos y servicios.
"""

import xmltodict
from pathlib import Path
from typing import List
from ..base_parser import BaseParser, ParsedFinding
from ...config import MAX_FILE_SIZE


class NmapParser(BaseParser):
    """Parser para archivos XML de Nmap."""
    
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si es un archivo XML de Nmap.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si es XML y contiene 'nmap' en el nombre
        """
        return (
            file_path.suffix.lower() == '.xml' and 
            'nmap' in file_path.stem.lower()
        )
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo XML de Nmap y extrae puertos abiertos.
        
        Args:
            file_path: Ruta al archivo XML
            
        Returns:
            Lista de ParsedFinding con puertos abiertos encontrados
        """
        findings = []
        
        # Validar tamaño del archivo
        if not self._validate_file_size(file_path, MAX_FILE_SIZE):
            self.logger.warning(f"File {file_path} exceeds max size, skipping")
            return findings
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            data = xmltodict.parse(content)
            nmaprun = data.get('nmaprun', {})
            
            # Manejar host único o múltiples
            hosts = nmaprun.get('host', [])
            if not isinstance(hosts, list):
                hosts = [hosts] if hosts else []
            
            for host in hosts:
                if not host:
                    continue
                
                # Extraer IP
                ip = self._extract_ip(host)
                
                # Extraer hostname si existe
                hostname = self._extract_hostname(host)
                
                # Extraer puertos
                ports = self._extract_ports(host)
                
                for port in ports:
                    if not port:
                        continue
                    
                    state = port.get('state', {}).get('@state', '')
                    if state == 'open':
                        finding = self._create_finding(port, ip, hostname)
                        findings.append(finding)
            
            self.logger.info(f"Parsed {len(findings)} open ports from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error parsing Nmap XML {file_path}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        return findings
    
    def _extract_ip(self, host: dict) -> str:
        """Extrae la IP del host."""
        address = host.get('address', {})
        if isinstance(address, list):
            return address[0].get('@addr', 'unknown')
        return address.get('@addr', 'unknown')
    
    def _extract_hostname(self, host: dict) -> str:
        """Extrae el hostname del host."""
        hostnames = host.get('hostnames', {})
        hostname_data = hostnames.get('hostname', {})
        
        if isinstance(hostname_data, dict):
            return hostname_data.get('@name', '')
        elif isinstance(hostname_data, list) and hostname_data:
            return hostname_data[0].get('@name', '')
        return ''
    
    def _extract_ports(self, host: dict) -> List[dict]:
        """Extrae la lista de puertos del host."""
        ports_data = host.get('ports', {})
        ports = ports_data.get('port', [])
        if not isinstance(ports, list):
            return [ports] if ports else []
        return ports
    
    def _create_finding(
        self, 
        port: dict, 
        ip: str, 
        hostname: str
    ) -> ParsedFinding:
        """
        Crea un ParsedFinding a partir de un puerto abierto.
        
        Args:
            port: Diccionario con datos del puerto
            ip: IP del host
            hostname: Hostname del host (puede estar vacío)
            
        Returns:
            ParsedFinding con la información del puerto
        """
        port_id = port.get('@portid', '')
        protocol = port.get('@protocol', 'tcp')
        
        service = port.get('service', {})
        service_name = service.get('@name', 'unknown')
        service_product = service.get('@product', '')
        service_version = service.get('@version', '')
        
        # Construir descripción
        description_parts = [f"Service: {service_name}"]
        if service_product:
            description_parts.append(service_product)
        if service_version:
            description_parts.append(service_version)
        description = ' '.join(description_parts)
        
        # Determinar severidad básica por puerto
        severity = self._assess_port_severity(int(port_id), service_name)
        
        # Construir target
        target = f"{ip} ({hostname})" if hostname else ip
        
        return ParsedFinding(
            title=f"Open Port: {port_id}/{protocol}",
            severity=severity,
            description=description,
            category='port_scan',
            affected_target=target,
            raw_data={
                'port': port_id,
                'protocol': protocol,
                'service': service_name,
                'product': service_product,
                'version': service_version,
                'ip': ip,
                'hostname': hostname
            }
        )
    
    def _assess_port_severity(self, port: int, service: str) -> str:
        """
        Asigna severidad básica según el puerto/servicio.
        
        Heurística simple basada en puertos comunes.
        La severidad real depende del contexto del pentest.
        
        Args:
            port: Número de puerto
            service: Nombre del servicio
            
        Returns:
            Severidad: critical, high, medium, low, info
        """
        # Puertos de administración remota
        if port in [22, 23, 3389, 5900, 5901]:  # SSH, Telnet, RDP, VNC
            return 'medium'
        
        # Bases de datos expuestas
        if port in [3306, 5432, 1433, 27017, 6379]:  # MySQL, PostgreSQL, MSSQL, MongoDB, Redis
            return 'medium'
        
        # Servicios comunes (menos críticos)
        if port in [80, 443, 8080, 8443]:  # HTTP/HTTPS
            return 'info'
        
        # Default
        return 'low'
