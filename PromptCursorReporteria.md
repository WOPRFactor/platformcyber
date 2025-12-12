# PROMPT PARA CURSOR - IMPLEMENTACIÓN MÓDULO DE REPORTERÍA

---

## 📋 CONTEXTO

Estás trabajando en una **plataforma de ethical hacking** que actualmente genera resultados de scans en archivos (no en BD). Hay 42+ herramientas que producen diferentes formatos: JSON, XML, TXT, JSONL, CSV.

**Problema**: El sistema de reportería actual es muy básico y poco útil para clientes.

**Solución**: Crear un módulo profesional de reportería que parsee todos los archivos, consolide datos y genere reportes profesionales en PDF/DOCX/HTML.

**Documentación de referencia**: `ESPECIFICACION_MODULO_REPORTERIA.md`

---

## 🎯 OBJETIVO GENERAL

Implementar un módulo completo de reportería que:
1. Auto-descubra archivos de resultados en workspaces
2. Parsee 42+ herramientas con diferentes formatos
3. Consolide y deduplique findings
4. Calcule métricas de riesgo
5. Genere reportes profesionales en múltiples formatos

---

## 🚀 IMPLEMENTACIÓN POR FASES

---

## FASE 1: ESTRUCTURA BASE Y PARSERS CORE (PRIORITARIO)

### Tarea 1.1: Crear estructura del módulo

Crea la siguiente estructura de directorios y archivos iniciales:

```
modules/reporting/
├── __init__.py
├── routes.py
├── report_service.py
├── core/
│   ├── __init__.py
│   ├── file_scanner.py
│   ├── data_aggregator.py
│   └── risk_calculator.py
├── parsers/
│   ├── __init__.py
│   ├── base_parser.py
│   ├── parser_manager.py
│   ├── reconnaissance/
│   │   └── __init__.py
│   ├── scanning/
│   │   └── __init__.py
│   ├── vulnerability/
│   │   └── __init__.py
│   └── enumeration/
│       └── __init__.py
├── generators/
│   ├── __init__.py
│   ├── base_generator.py
│   └── pdf_generator.py
├── templates/
│   ├── base.html
│   └── technical/
│       └── report.html
└── static/
    └── css/
        └── report.css
```

**Instrucciones específicas**:
- Usa la estructura exacta documentada en `ESPECIFICACION_MODULO_REPORTERIA.md` sección 5
- Cada `__init__.py` debe importar las clases principales de ese módulo
- Sigue las convenciones de naming de Python (snake_case para archivos, PascalCase para clases)

---

### Tarea 1.2: Implementar BaseParser

**Archivo**: `modules/reporting/parsers/base_parser.py`

**Requisitos**:
1. Crea una clase abstracta `BaseParser` con:
   - Método abstracto `can_parse(file_path: Path) -> bool`
   - Método abstracto `parse(file_path: Path) -> List[ParsedFinding]`
   - Método helper `_read_file()` con manejo de encoding
   - Método helper `_safe_parse_json()` con manejo de errores
   - Logger por clase

2. Crea un dataclass `ParsedFinding` con:
   - title: str
   - severity: str (critical, high, medium, low, info)
   - description: str
   - category: str
   - affected_target: str
   - evidence: Optional[str]
   - remediation: Optional[str]
   - cvss_score: Optional[float]
   - cve_id: Optional[str]
   - references: Optional[List[str]]
   - raw_data: Optional[Dict[str, Any]]

**Código base**:
```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging
import json

@dataclass
class ParsedFinding:
    """Estructura estándar para un hallazgo."""
    title: str
    severity: str
    description: str
    category: str
    affected_target: str
    evidence: Optional[str] = None
    remediation: Optional[str] = None
    cvss_score: Optional[float] = None
    cve_id: Optional[str] = None
    references: Optional[List[str]] = field(default_factory=list)
    raw_data: Optional[Dict[str, Any]] = field(default_factory=dict)

class BaseParser(ABC):
    """Clase base abstracta para todos los parsers."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """
        Verifica si este parser puede manejar el archivo.
        
        Args:
            file_path: Ruta al archivo a evaluar
            
        Returns:
            True si el parser puede procesar el archivo
        """
        pass
    
    @abstractmethod
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea el archivo y retorna lista de findings.
        
        Args:
            file_path: Ruta al archivo a parsear
            
        Returns:
            Lista de ParsedFinding
        """
        pass
    
    def _read_file(self, file_path: Path, encoding: str = 'utf-8') -> str:
        """
        Lee archivo con manejo robusto de encoding.
        
        Args:
            file_path: Ruta al archivo
            encoding: Encoding a usar (default: utf-8)
            
        Returns:
            Contenido del archivo como string
        """
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            self.logger.warning(f"UTF-8 decode failed for {file_path}, trying latin-1")
            try:
                return file_path.read_text(encoding='latin-1')
            except Exception as e:
                self.logger.error(f"Failed to read {file_path}: {e}")
                return ""
    
    def _safe_parse_json(self, file_path: Path) -> Optional[Dict]:
        """
        Parsea JSON con manejo robusto de errores.
        
        Args:
            file_path: Ruta al archivo JSON
            
        Returns:
            Diccionario parseado o None si falla
        """
        try:
            content = self._read_file(file_path)
            return json.loads(content)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error in {file_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error parsing JSON {file_path}: {e}")
            return None
```

**Validación**:
- Verifica que la clase es abstracta y no se puede instanciar
- Verifica que los métodos helper funcionan con archivos de prueba
- Agrega tests en `tests/test_base_parser.py`

---

### Tarea 1.3: Implementar NmapParser

**Archivo**: `modules/reporting/parsers/scanning/nmap_parser.py`

**Requisitos**:
1. Hereda de `BaseParser`
2. Implementa `can_parse()`: Verifica que sea XML y contenga 'nmap' en el nombre
3. Implementa `parse()`: 
   - Usa `xmltodict` para parsear XML
   - Extrae hosts y puertos abiertos
   - Crea un `ParsedFinding` por cada puerto abierto
   - Maneja casos de host único y múltiples hosts
   - Captura: IP, puerto, protocolo, servicio, versión

**Instalación requerida**:
```bash
pip install xmltodict
```

**Código base**:
```python
import xmltodict
from pathlib import Path
from typing import List
from ..base_parser import BaseParser, ParsedFinding

class NmapParser(BaseParser):
    """Parser para archivos XML de Nmap."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si es un archivo XML de Nmap."""
        return (
            file_path.suffix.lower() == '.xml' and 
            'nmap' in file_path.stem.lower()
        )
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """Parsea archivo XML de Nmap y extrae puertos abiertos."""
        findings = []
        
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
                address = host.get('address', {})
                if isinstance(address, list):
                    ip = address[0].get('@addr', 'unknown')
                else:
                    ip = address.get('@addr', 'unknown')
                
                # Extraer hostname si existe
                hostnames = host.get('hostnames', {})
                hostname_data = hostnames.get('hostname', {})
                hostname = ''
                if isinstance(hostname_data, dict):
                    hostname = hostname_data.get('@name', '')
                elif isinstance(hostname_data, list) and hostname_data:
                    hostname = hostname_data[0].get('@name', '')
                
                # Extraer puertos
                ports_data = host.get('ports', {})
                ports = ports_data.get('port', [])
                if not isinstance(ports, list):
                    ports = [ports] if ports else []
                
                for port in ports:
                    if not port:
                        continue
                    
                    state = port.get('state', {}).get('@state', '')
                    if state == 'open':
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
                        
                        finding = ParsedFinding(
                            title=f"Open Port: {port_id}/{protocol}",
                            severity=severity,
                            description=description,
                            category='port_scan',
                            affected_target=f"{ip} ({hostname})" if hostname else ip,
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
                        findings.append(finding)
            
            self.logger.info(f"Parsed {len(findings)} open ports from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error parsing Nmap XML {file_path}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        return findings
    
    def _assess_port_severity(self, port: int, service: str) -> str:
        """
        Asigna severidad básica según el puerto/servicio.
        Esto es una heurística simple, la severidad real depende del contexto.
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
```

**Validación**:
- Crea un archivo XML de Nmap de prueba en `tests/fixtures/nmap_sample.xml`
- Verifica que parsea correctamente hosts, puertos y servicios
- Test con archivo vacío, malformado, host único, múltiples hosts

---

### Tarea 1.4: Implementar NucleiParser

**Archivo**: `modules/reporting/parsers/vulnerability/nuclei_parser.py`

**Requisitos**:
1. Hereda de `BaseParser`
2. Implementa `can_parse()`: Verifica extensión `.jsonl` y 'nuclei' en nombre
3. Implementa `parse()`:
   - Lee archivo línea por línea (JSONL = JSON Lines)
   - Cada línea es un JSON independiente
   - Extrae: template-id, info, matched-at, severity
   - Mapea severidades de Nuclei a estándar

**Código base**:
```python
import json
from pathlib import Path
from typing import List
from ..base_parser import BaseParser, ParsedFinding

class NucleiParser(BaseParser):
    """Parser para archivos JSONL de Nuclei."""
    
    SEVERITY_MAP = {
        'critical': 'critical',
        'high': 'high',
        'medium': 'medium',
        'low': 'low',
        'info': 'info',
        'unknown': 'info'
    }
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si es un archivo JSONL de Nuclei."""
        return (
            file_path.suffix.lower() == '.jsonl' and 
            'nuclei' in file_path.stem.lower()
        )
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """Parsea archivo JSONL de Nuclei (un JSON por línea)."""
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            # JSONL = una línea JSON por línea
            for line_num, line in enumerate(content.strip().split('\n'), 1):
                if not line.strip():
                    continue
                
                try:
                    data = json.loads(line)
                    
                    # Extraer campos principales
                    template_id = data.get('template-id', 'unknown')
                    info = data.get('info', {})
                    matched_at = data.get('matched-at', data.get('host', ''))
                    
                    # Severity
                    severity = info.get('severity', 'info').lower()
                    severity = self.SEVERITY_MAP.get(severity, 'info')
                    
                    # Nombre y descripción
                    name = info.get('name', template_id)
                    description = info.get('description', '')
                    
                    # Referencias
                    references = info.get('reference', [])
                    if isinstance(references, str):
                        references = [references]
                    
                    # Tags
                    tags = info.get('tags', [])
                    if isinstance(tags, str):
                        tags = tags.split(',')
                    
                    # CVE si existe
                    cve_id = None
                    for ref in references:
                        if 'CVE-' in ref.upper():
                            cve_id = ref.split('/')[-1].upper()
                            break
                    
                    # Evidencia
                    evidence = data.get('matched-line', '')
                    if not evidence:
                        evidence = data.get('extracted-results', [])
                        if evidence:
                            evidence = str(evidence)
                    
                    finding = ParsedFinding(
                        title=name,
                        severity=severity,
                        description=description,
                        category='vulnerability',
                        affected_target=matched_at,
                        evidence=evidence,
                        cve_id=cve_id,
                        references=references,
                        raw_data={
                            'template_id': template_id,
                            'tags': tags,
                            'matcher_name': data.get('matcher-name'),
                            'type': data.get('type')
                        }
                    )
                    findings.append(finding)
                    
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Invalid JSON at line {line_num} in {file_path}: {e}")
                    continue
            
            self.logger.info(f"Parsed {len(findings)} vulnerabilities from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error parsing Nuclei JSONL {file_path}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        return findings
```

**Validación**:
- Crea archivo de prueba `tests/fixtures/nuclei_sample.jsonl`
- Verifica parsing de múltiples líneas
- Test con JSON malformado en alguna línea
- Verifica mapeo de severidades

---

### Tarea 1.5: Implementar SubfinderParser

**Archivo**: `modules/reporting/parsers/reconnaissance/subfinder_parser.py`

**Requisitos**:
1. Hereda de `BaseParser`
2. Lee archivo TXT plano (un subdominio por línea)
3. Crea un finding por cada subdominio

**Código base**:
```python
from pathlib import Path
from typing import List
from ..base_parser import BaseParser, ParsedFinding

class SubfinderParser(BaseParser):
    """Parser para archivos TXT de Subfinder."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si es un archivo TXT de Subfinder."""
        return (
            file_path.suffix.lower() == '.txt' and 
            'subfinder' in file_path.stem.lower()
        )
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """Parsea archivo TXT de Subfinder (un dominio por línea)."""
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            # Extraer dominios (un dominio por línea)
            subdomains = [
                line.strip() 
                for line in content.split('\n') 
                if line.strip() and not line.startswith('#')
            ]
            
            for subdomain in subdomains:
                # Validación básica de formato de dominio
                if '.' not in subdomain:
                    continue
                
                finding = ParsedFinding(
                    title=f"Subdomain: {subdomain}",
                    severity='info',
                    description=f"Discovered subdomain through reconnaissance",
                    category='reconnaissance',
                    affected_target=subdomain,
                    raw_data={'subdomain': subdomain, 'tool': 'subfinder'}
                )
                findings.append(finding)
            
            self.logger.info(f"Parsed {len(findings)} subdomains from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error parsing Subfinder TXT {file_path}: {e}")
        
        return findings
```

---

### Tarea 1.6: Implementar NiktoParser

**Archivo**: `modules/reporting/parsers/vulnerability/nikto_parser.py`

**Requisitos**:
1. Lee archivo JSON de Nikto
2. Extrae vulnerabilidades
3. Mapea severidad (Nikto no tiene campo severity nativo, usar heurística)

**Código base**:
```python
from pathlib import Path
from typing import List
from ..base_parser import BaseParser, ParsedFinding

class NiktoParser(BaseParser):
    """Parser para archivos JSON de Nikto."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si es un archivo JSON de Nikto."""
        return (
            file_path.suffix.lower() == '.json' and 
            'nikto' in file_path.stem.lower()
        )
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """Parsea archivo JSON de Nikto."""
        findings = []
        
        try:
            data = self._safe_parse_json(file_path)
            if not data:
                return findings
            
            # Nikto puede tener múltiples scans (array) o uno solo (dict)
            scans = data if isinstance(data, list) else [data]
            
            for scan in scans:
                host = scan.get('host', 'unknown')
                port = scan.get('port', 80)
                ip = scan.get('ip', '')
                
                vulnerabilities = scan.get('vulnerabilities', [])
                
                for vuln in vulnerabilities:
                    msg = vuln.get('msg', 'Unknown vulnerability')
                    osvdb = vuln.get('OSVDB', '')
                    method = vuln.get('method', 'GET')
                    url = vuln.get('url', '')
                    
                    # Severidad heurística basada en el mensaje
                    severity = self._assess_severity(msg, vuln)
                    
                    # Construir target completo
                    target = f"{host}:{port}{url}" if url else f"{host}:{port}"
                    
                    finding = ParsedFinding(
                        title=f"Nikto: {msg[:80]}",  # Truncar títulos largos
                        severity=severity,
                        description=msg,
                        category='web_vulnerability',
                        affected_target=target,
                        references=[f"OSVDB-{osvdb}"] if osvdb else None,
                        raw_data={
                            'method': method,
                            'url': url,
                            'osvdb': osvdb,
                            'host': host,
                            'port': port,
                            'ip': ip
                        }
                    )
                    findings.append(finding)
            
            self.logger.info(f"Parsed {len(findings)} findings from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error parsing Nikto JSON {file_path}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        return findings
    
    def _assess_severity(self, msg: str, vuln: dict) -> str:
        """
        Asigna severidad basada en palabras clave en el mensaje.
        Nikto no tiene campo de severidad nativo.
        """
        msg_lower = msg.lower()
        
        # Critical
        critical_keywords = [
            'sql injection', 'rce', 'remote code execution', 
            'arbitrary code', 'shell upload'
        ]
        if any(kw in msg_lower for kw in critical_keywords):
            return 'critical'
        
        # High
        high_keywords = [
            'xss', 'cross-site scripting', 'csrf', 'command injection',
            'file inclusion', 'lfi', 'rfi', 'authentication bypass',
            'default credentials'
        ]
        if any(kw in msg_lower for kw in high_keywords):
            return 'high'
        
        # Medium
        medium_keywords = [
            'information disclosure', 'directory listing', 'backup file',
            'sensitive', 'phpinfo', 'configuration file'
        ]
        if any(kw in msg_lower for kw in medium_keywords):
            return 'medium'
        
        # Low por default
        return 'low'
```

---

### Tarea 1.7: Implementar ParserManager

**Archivo**: `modules/reporting/parsers/parser_manager.py`

**Requisitos**:
1. Gestiona todos los parsers disponibles
2. Selecciona el parser apropiado para cada archivo
3. Permite registro dinámico de nuevos parsers

**Código base**:
```python
from pathlib import Path
from typing import List, Optional, Type
from .base_parser import BaseParser, ParsedFinding
import logging

# Importar parsers implementados
from .scanning.nmap_parser import NmapParser
from .vulnerability.nuclei_parser import NucleiParser
from .vulnerability.nikto_parser import NiktoParser
from .reconnaissance.subfinder_parser import SubfinderParser

class ParserManager:
    """Gestiona la selección y ejecución de parsers."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.parsers: List[BaseParser] = []
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """Registra los parsers por defecto."""
        default_parsers = [
            NmapParser(),
            NucleiParser(),
            NiktoParser(),
            SubfinderParser(),
            # Agregar más parsers aquí según se implementen
        ]
        
        for parser in default_parsers:
            self.register_parser(parser)
        
        self.logger.info(f"Registered {len(self.parsers)} parsers")
    
    def register_parser(self, parser: BaseParser):
        """
        Registra un nuevo parser.
        
        Args:
            parser: Instancia del parser a registrar
        """
        self.parsers.append(parser)
        self.logger.debug(f"Registered parser: {parser.__class__.__name__}")
    
    def get_parser(self, file_path: Path) -> Optional[BaseParser]:
        """
        Obtiene el parser apropiado para un archivo.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Parser capaz de procesar el archivo, o None si no hay ninguno
        """
        for parser in self.parsers:
            if parser.can_parse(file_path):
                self.logger.debug(f"Selected {parser.__class__.__name__} for {file_path.name}")
                return parser
        
        self.logger.warning(f"No parser found for {file_path}")
        return None
    
    def parse_file(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea un archivo usando el parser apropiado.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Lista de findings parseados
        """
        parser = self.get_parser(file_path)
        
        if parser is None:
            self.logger.warning(f"Cannot parse {file_path}: no suitable parser")
            return []
        
        try:
            findings = parser.parse(file_path)
            self.logger.info(f"Parsed {len(findings)} findings from {file_path.name}")
            return findings
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
```

---

### Tarea 1.8: Implementar FileScanner

**Archivo**: `modules/reporting/core/file_scanner.py`

**Requisitos**:
1. Descubre todos los archivos de resultados en un workspace
2. Organiza por categorías (recon, scans, vuln_scans, etc.)
3. Maneja workspace_name o workspace_id

**Código base**:
```python
from pathlib import Path
from typing import Dict, List
import logging
from utils.workspace_filesystem import get_workspace_dir

class FileScanner:
    """Escanea y descubre archivos de resultados en un workspace."""
    
    CATEGORIES = [
        'recon',
        'scans',
        'enumeration',
        'vuln_scans',
        'exploitation',
        'postexploit',
        'ad_scans',
        'cloud_scans'
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def scan_workspace(
        self, 
        workspace_id: int, 
        workspace_name: str
    ) -> Dict[str, List[Path]]:
        """
        Escanea un workspace y retorna archivos organizados por categoría.
        
        Args:
            workspace_id: ID del workspace
            workspace_name: Nombre del workspace
            
        Returns:
            Diccionario con categorías como keys y listas de Path como values
            Ejemplo: {
                'recon': [Path('subfinder_123.txt'), Path('amass_124.txt')],
                'scans': [Path('nmap_456.xml')],
                'vuln_scans': [Path('nuclei_789.jsonl'), Path('nikto_790.json')]
            }
        """
        files_by_category = {}
        
        try:
            # Obtener directorio del workspace
            workspace_dir = get_workspace_dir(workspace_id, workspace_name)
            
            if not workspace_dir.exists():
                self.logger.warning(f"Workspace directory not found: {workspace_dir}")
                return files_by_category
            
            self.logger.info(f"Scanning workspace directory: {workspace_dir}")
            
            # Escanear cada categoría
            for category in self.CATEGORIES:
                category_dir = workspace_dir / category
                
                if not category_dir.exists():
                    self.logger.debug(f"Category directory not found: {category_dir}")
                    continue
                
                # Buscar todos los archivos (no directorios)
                files = []
                for item in category_dir.iterdir():
                    if item.is_file():
                        files.append(item)
                    elif item.is_dir():
                        # Algunos tools generan directorios (ej: sqlmap)
                        # Buscar archivos dentro
                        for subitem in item.rglob('*'):
                            if subitem.is_file():
                                files.append(subitem)
                
                if files:
                    files_by_category[category] = files
                    self.logger.info(f"Found {len(files)} files in {category}")
            
            total_files = sum(len(files) for files in files_by_category.values())
            self.logger.info(f"Total files found: {total_files}")
            
        except Exception as e:
            self.logger.error(f"Error scanning workspace: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        return files_by_category
```

**Validación**:
- Test con workspace que tiene archivos
- Test con workspace vacío
- Test con workspace que no existe
- Verifica que encuentra archivos en subdirectorios (sqlmap)

---

### Tarea 1.9: Implementar DataAggregator

**Archivo**: `modules/reporting/core/data_aggregator.py`

**Requisitos**:
1. Consolida findings de múltiples parsers
2. Deduplica findings similares
3. Agrupa por categoría y severidad

**Código base**:
```python
from typing import List, Dict
from ..parsers.base_parser import ParsedFinding
import logging

class DataAggregator:
    """Consolida y deduplica findings de múltiples parsers."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def consolidate(self, findings: List[ParsedFinding]) -> Dict[str, List[ParsedFinding]]:
        """
        Consolida findings por categoría y deduplica.
        
        Args:
            findings: Lista de todos los findings parseados
            
        Returns:
            Diccionario organizado por categoría
        """
        self.logger.info(f"Consolidating {len(findings)} findings")
        
        # Deduplicar primero
        deduplicated = self._deduplicate(findings)
        self.logger.info(f"After deduplication: {len(deduplicated)} findings")
        
        # Agrupar por categoría
        by_category = {}
        for finding in deduplicated:
            category = finding.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(finding)
        
        # Ordenar cada categoría por severidad (critical primero)
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        
        for category in by_category:
            by_category[category].sort(
                key=lambda f: (severity_order.get(f.severity, 999), f.title)
            )
        
        self.logger.info(f"Consolidated into {len(by_category)} categories")
        
        return by_category
    
    def _deduplicate(self, findings: List[ParsedFinding]) -> List[ParsedFinding]:
        """
        Deduplica findings similares.
        
        Criterio: Mismo título, severidad y target
        """
        seen = set()
        deduplicated = []
        
        for finding in findings:
            # Crear clave única
            key = (
                finding.title.lower().strip(),
                finding.severity.lower(),
                finding.affected_target.lower().strip()
            )
            
            if key not in seen:
                seen.add(key)
                deduplicated.append(finding)
        
        duplicates_removed = len(findings) - len(deduplicated)
        if duplicates_removed > 0:
            self.logger.info(f"Removed {duplicates_removed} duplicate findings")
        
        return deduplicated
    
    def get_statistics(self, consolidated: Dict[str, List[ParsedFinding]]) -> Dict:
        """
        Calcula estadísticas de los findings.
        
        Returns:
            Dict con estadísticas: totales, por severidad, por categoría
        """
        all_findings = []
        for findings in consolidated.values():
            all_findings.extend(findings)
        
        # Por severidad
        by_severity = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        for finding in all_findings:
            severity = finding.severity.lower()
            if severity in by_severity:
                by_severity[severity] += 1
        
        # Por categoría
        by_category = {
            category: len(findings)
            for category, findings in consolidated.items()
        }
        
        # Targets únicos
        unique_targets = set(f.affected_target for f in all_findings)
        
        return {
            'total_findings': len(all_findings),
            'by_severity': by_severity,
            'by_category': by_category,
            'unique_targets': len(unique_targets),
            'targets': list(unique_targets)
        }
```

---

### Tarea 1.10: Implementar RiskCalculator

**Archivo**: `modules/reporting/core/risk_calculator.py`

**Requisitos**:
1. Calcula risk score global (0-10)
2. Basado en cantidad y severidad de vulnerabilidades
3. Formula ponderada

**Código base**:
```python
from typing import Dict, List
from ..parsers.base_parser import ParsedFinding
import logging

class RiskCalculator:
    """Calcula métricas de riesgo basadas en findings."""
    
    # Pesos por severidad (para cálculo de risk score)
    SEVERITY_WEIGHTS = {
        'critical': 10.0,
        'high': 7.5,
        'medium': 5.0,
        'low': 2.5,
        'info': 0.5
    }
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def calculate(self, consolidated: Dict[str, List[ParsedFinding]]) -> Dict:
        """
        Calcula métricas de riesgo.
        
        Args:
            consolidated: Findings consolidados por categoría
            
        Returns:
            Dict con métricas: risk_score, severity_distribution, etc.
        """
        # Obtener todos los findings
        all_findings = []
        for findings in consolidated.values():
            all_findings.extend(findings)
        
        if not all_findings:
            return {
                'risk_score': 0.0,
                'risk_level': 'none',
                'total_findings': 0,
                'severity_distribution': {
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0,
                    'info': 0
                }
            }
        
        # Contar por severidad
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        for finding in all_findings:
            severity = finding.severity.lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Calcular risk score (0-10)
        risk_score = self._calculate_risk_score(severity_counts)
        risk_level = self._assess_risk_level(risk_score)
        
        self.logger.info(f"Risk Score: {risk_score:.2f} ({risk_level})")
        
        return {
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'total_findings': len(all_findings),
            'severity_distribution': severity_counts,
            'vulnerabilities_only': sum(
                1 for f in all_findings 
                if f.category in ['vulnerability', 'web_vulnerability']
            )
        }
    
    def _calculate_risk_score(self, severity_counts: Dict[str, int]) -> float:
        """
        Calcula risk score ponderado (0-10).
        
        Fórmula:
        - Si hay critical: automáticamente alto (8-10)
        - Si hay high: 6-8
        - Si hay medium: 4-6
        - Si solo low/info: 0-4
        
        Escala logarítmica para evitar saturación con muchos findings.
        """
        import math
        
        # Score ponderado
        weighted_sum = 0.0
        for severity, count in severity_counts.items():
            weight = self.SEVERITY_WEIGHTS.get(severity, 0)
            # Usar logaritmo para reducir impacto de muchos findings de misma severidad
            weighted_sum += weight * math.log1p(count)
        
        # Normalizar a escala 0-10
        # Valor máximo teórico: 100 critical = ~46, normalizar a 10
        max_theoretical = 50.0
        risk_score = min(10.0, (weighted_sum / max_theoretical) * 10)
        
        # Ajustes específicos
        if severity_counts['critical'] > 0:
            # Al menos 7.5 si hay critical
            risk_score = max(7.5, risk_score)
        elif severity_counts['high'] > 5:
            # Al menos 6.0 si hay muchos high
            risk_score = max(6.0, risk_score)
        
        return risk_score
    
    def _assess_risk_level(self, risk_score: float) -> str:
        """Convierte risk score numérico a nivel categórico."""
        if risk_score >= 8.0:
            return 'critical'
        elif risk_score >= 6.0:
            return 'high'
        elif risk_score >= 4.0:
            return 'medium'
        elif risk_score >= 2.0:
            return 'low'
        else:
            return 'info'
```

---

## CONTINÚA EN EL SIGUIENTE MENSAJE...

**IMPORTANTE**: 
- Este es el inicio de la FASE 1
- Implementa estas tareas en orden
- Valida cada componente con tests antes de continuar
- Una vez completada esta fase, pide las siguientes instrucciones

**CHECKLIST FASE 1**:
- [ ] Estructura de directorios creada
- [ ] BaseParser implementado
- [ ] NmapParser implementado y testeado
- [ ] NucleiParser implementado y testeado
- [ ] SubfinderParser implementado y testeado
- [ ] NiktoParser implementado y testeado
- [ ] ParserManager implementado
- [ ] FileScanner implementado
- [ ] DataAggregator implementado
- [ ] RiskCalculator implementado
- [ ] Tests unitarios para cada componente