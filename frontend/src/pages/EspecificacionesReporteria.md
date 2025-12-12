# ESPECIFICACIÓN TÉCNICA - MÓDULO DE REPORTERÍA
## Plataforma de Ethical Hacking

---

## 📋 ÍNDICE

1. [Visión General](#visión-general)
2. [Objetivos](#objetivos)
3. [Arquitectura del Módulo](#arquitectura-del-módulo)
4. [Stack Tecnológico](#stack-tecnológico)
5. [Estructura de Archivos](#estructura-de-archivos)
6. [Parsers por Herramienta](#parsers-por-herramienta)
7. [Tipos de Reportes](#tipos-de-reportes)
8. [Flujo de Generación](#flujo-de-generación)
9. [Modelo de Datos](#modelo-de-datos)
10. [API Endpoints](#api-endpoints)
11. [Prioridades de Implementación](#prioridades-de-implementación)

---

## 1. VISIÓN GENERAL

### Problema Actual
- Los resultados de scans se guardan en archivos dispersos
- 42+ herramientas generan diferentes formatos (JSON, XML, TXT, JSONL, CSV)
- No hay registro de rutas de archivos en la BD
- El reporte actual es básico y poco útil para clientes

### Solución Propuesta
Crear un **módulo de reportería profesional** que:
- Auto-descubra y parsee todos los archivos de resultados
- Consolide información de múltiples herramientas
- Calcule métricas de riesgo y estadísticas
- Genere reportes profesionales en múltiples formatos (PDF, DOCX, HTML)
- Proporcione valor real a clientes técnicos y ejecutivos

---

## 2. OBJETIVOS

### Objetivos Funcionales
1. ✅ Parsear resultados de las 42+ herramientas actuales
2. ✅ Generar 3 tipos de reportes: Executive, Technical, Compliance
3. ✅ Exportar en 3 formatos: PDF, DOCX, HTML
4. ✅ Incluir gráficos profesionales y visualizaciones
5. ✅ Calcular risk scores automáticamente
6. ✅ Proporcionar evidencias técnicas detalladas

### Objetivos Técnicos
1. ✅ Sistema modular y extensible
2. ✅ Parsers independientes por herramienta
3. ✅ Performance: generar reportes en <30 segundos
4. ✅ Manejo robusto de errores
5. ✅ Logs detallados de procesamiento

### Objetivos de Negocio
1. ✅ Aumentar valor percibido del servicio
2. ✅ Facilitar venta de servicios (reportes profesionales)
3. ✅ Reducir tiempo de post-procesamiento manual
4. ✅ Diferenciación competitiva

---

## 3. ARQUITECTURA DEL MÓDULO

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (Flask)                         │
│  /api/v1/reporting/generate                                  │
│  /api/v1/reporting/download/{report_id}                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  ReportService (Orquestador)                 │
│  - Coordina todo el proceso de generación                    │
│  - Maneja estado y errores                                   │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ FileScanner  │   │ DataAggregator│   │ RiskCalculator│
│              │   │               │   │              │
│ Descubre     │   │ Consolida     │   │ Calcula      │
│ archivos     │   │ datos         │   │ scores       │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Parser Manager                            │
│  - Detecta tipo de archivo                                   │
│  - Selecciona parser apropiado                               │
│  - Maneja errores de parsing                                 │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Parsers (42+)                             │
│  ReconParsers | ScanParsers | VulnParsers | EnumParsers    │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Consolidación                             │
│  - Findings deduplicados                                     │
│  - Vulnerabilidades agrupadas                                │
│  - Métricas calculadas                                       │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Report Generators                         │
│  PDFGenerator | DOCXGenerator | HTMLGenerator               │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Output Files                              │
│  /workspaces/{name}/reports/executive_summary.pdf           │
│  /workspaces/{name}/reports/technical_report.pdf            │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. STACK TECNOLÓGICO

### Core
- **Python 3.10+**
- **Flask** - API endpoints
- **SQLAlchemy** - ORM

### Parsing
- **xmltodict** - Para Nmap XML
- **json** (stdlib) - Para JSON
- **csv** (stdlib) - Para CSV
- **re** (stdlib) - Para TXT con regex

### Generación de Reportes
- **WeasyPrint** 60.1+ - PDFs profesionales desde HTML/CSS
- **python-docx** 1.1.0+ - Generación de DOCX
- **Jinja2** 3.1.2+ - Templates HTML

### Visualizaciones
- **Plotly** 5.18.0+ - Gráficos interactivos
- **Kaleido** 0.2.1+ - Export de gráficos a PNG

### Análisis de Datos
- **Pandas** 2.1.4+ - Manipulación de datos
- **numpy** - Cálculos estadísticos

### Utilidades
- **pathlib** (stdlib) - Manejo de rutas
- **typing** (stdlib) - Type hints
- **dataclasses** (stdlib) - Estructuras de datos

---

## 5. ESTRUCTURA DE ARCHIVOS

**NOTA**: Alineado con la estructura actual del proyecto que usa `services/` en lugar de `modules/`

```
services/reporting/
├── __init__.py
├── routes.py                           # API endpoints
├── report_service.py                   # Servicio principal (orquestador)
│
├── core/                               # Componentes core
│   ├── __init__.py
│   ├── file_scanner.py                 # Descubre archivos en workspace
│   ├── data_aggregator.py              # Consolida datos parseados
│   ├── risk_calculator.py              # Calcula risk scores
│   └── report_builder.py               # Construye estructura del reporte
│
├── parsers/                            # Parsers por categoría
│   ├── __init__.py
│   ├── base_parser.py                  # Clase base abstracta
│   ├── parser_manager.py               # Gestiona selección de parsers
│   │
│   ├── reconnaissance/                 # 9 herramientas
│   │   ├── __init__.py
│   │   ├── subfinder_parser.py
│   │   ├── amass_parser.py
│   │   ├── theharvester_parser.py
│   │   ├── dnsrecon_parser.py
│   │   ├── shodan_parser.py
│   │   ├── gitleaks_parser.py
│   │   ├── trufflehog_parser.py
│   │   ├── hunter_io_parser.py
│   │   └── censys_parser.py
│   │
│   ├── scanning/                       # 4 herramientas
│   │   ├── __init__.py
│   │   ├── nmap_parser.py              # PRIORITARIO (XML)
│   │   ├── rustscan_parser.py
│   │   ├── masscan_parser.py
│   │   └── naabu_parser.py
│   │
│   ├── enumeration/                    # 4+ herramientas
│   │   ├── __init__.py
│   │   ├── nmap_service_parser.py
│   │   ├── enum4linux_parser.py
│   │   ├── smbmap_parser.py
│   │   └── sslscan_parser.py
│   │
│   ├── vulnerability/                  # 9 herramientas
│   │   ├── __init__.py
│   │   ├── nuclei_parser.py            # PRIORITARIO (JSONL)
│   │   ├── nikto_parser.py
│   │   ├── sqlmap_parser.py
│   │   ├── testssl_parser.py
│   │   ├── wpscan_parser.py
│   │   ├── whatweb_parser.py
│   │   ├── zap_parser.py
│   │   ├── xsser_parser.py
│   │   └── xsstrike_parser.py
│   │
│   ├── active_directory/               # 5 herramientas
│   │   ├── __init__.py
│   │   ├── crackmapexec_parser.py
│   │   ├── kerbrute_parser.py
│   │   ├── getnpusers_parser.py
│   │   ├── ldapdomaindump_parser.py
│   │   └── adidnsdump_parser.py
│   │
│   ├── cloud/                          # 5 herramientas
│   │   ├── __init__.py
│   │   ├── prowler_parser.py
│   │   ├── scoutsuite_parser.py
│   │   ├── pacu_parser.py
│   │   ├── azurehound_parser.py
│   │   └── roadtools_parser.py
│   │
│   └── container/                      # 6 herramientas
│       ├── __init__.py
│       ├── trivy_parser.py
│       ├── grype_parser.py
│       ├── syft_parser.py
│       ├── kubebench_parser.py
│       ├── kubehunter_parser.py
│       └── kubescape_parser.py
│
├── generators/                         # Generadores de reportes
│   ├── __init__.py
│   ├── base_generator.py               # Clase base
│   ├── pdf_generator.py                # WeasyPrint (PRIORITARIO)
│   ├── docx_generator.py               # python-docx
│   └── html_generator.py               # HTML standalone
│
├── templates/                          # Templates Jinja2
│   ├── base.html                       # Template base
│   ├── components/                     # Componentes reutilizables
│   │   ├── header.html
│   │   ├── footer.html
│   │   ├── vulnerability_card.html
│   │   ├── risk_badge.html
│   │   └── chart_container.html
│   │
│   ├── executive/                      # Reporte ejecutivo
│   │   ├── summary.html
│   │   ├── risk_overview.html
│   │   └── recommendations.html
│   │
│   ├── technical/                      # Reporte técnico
│   │   ├── methodology.html
│   │   ├── findings.html
│   │   ├── vulnerability_details.html
│   │   └── raw_data.html
│   │
│   └── compliance/                     # Reporte de compliance
│       ├── framework_mapping.html
│       └── controls_assessment.html
│
├── static/                             # CSS y assets
│   ├── css/
│   │   ├── report.css                  # Estilos para reportes
│   │   └── print.css                   # Estilos para PDF
│   └── images/
│       └── logo.png                    # Logo de la plataforma
│
├── utils/                              # Utilidades
│   ├── __init__.py
│   ├── cvss_calculator.py              # Calcula CVSS scores
│   ├── severity_mapper.py              # Mapea severidades
│   ├── deduplicator.py                 # Deduplica findings
│   └── chart_builder.py                # Construye gráficos Plotly
│
└── tests/                              # Tests unitarios
    ├── __init__.py
    ├── test_parsers.py
    ├── test_generators.py
    └── fixtures/                       # Archivos de ejemplo
        ├── nmap_sample.xml
        ├── nuclei_sample.jsonl
        └── nikto_sample.json
```

---

## 6. MANEJO DE ERRORES Y EDGE CASES

### 6.1. Estrategia General

**Principio**: "Fail gracefully" - Los errores en parsers individuales NO deben detener la generación completa del reporte.

### 6.2. Casos de Error y Soluciones

#### A. Parser Falla

**Problema**: Un parser lanza excepción al procesar un archivo.

**Solución**:
```python
# En ParserManager.parse_file()
try:
    findings = parser.parse(file_path)
    return findings
except Exception as e:
    logger.error(f"Parser {parser.__class__.__name__} failed for {file_path}: {e}")
    logger.error(traceback.format_exc())
    
    # Retornar lista vacía, NO propagar excepción
    return []
```

**Resultado**: Se continúa con otros archivos, se logea el error detalladamente.

#### B. Archivo Corrupto o Malformado

**Problema**: JSON inválido, XML mal formado, encoding incompatible.

**Solución**:
```python
# En BaseParser._safe_parse_json()
try:
    return json.loads(content)
except json.JSONDecodeError as e:
    logger.error(f"JSON parse error in {file_path}: {e}")
    # Intentar reparación automática (opcional)
    # return self._attempt_json_repair(content)
    return None
```

**Resultado**: El parser retorna lista vacía o findings parciales.

#### C. No Hay Archivos en Workspace

**Problema**: Workspace vacío o sin archivos parseables.

**Solución**:
```python
# En ReportService.generate_report()
files = file_scanner.scan_workspace(workspace_id, workspace_name)

if not files or all(len(f) == 0 for f in files.values()):
    # Generar reporte "vacío" informativo
    return self._generate_empty_report(workspace_id, report_type)
```

**Resultado**: Se genera reporte indicando "No se encontraron resultados de scans".

#### D. Archivo Muy Grande (>100MB)

**Problema**: Archivo consume demasiada memoria, riesgo de OOM.

**Solución**:
```python
# Límite configurable
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

def parse(self, file_path: Path) -> List[ParsedFinding]:
    file_size = file_path.stat().st_size
    
    if file_size > MAX_FILE_SIZE:
        logger.warning(f"File too large ({file_size} bytes): {file_path}")
        # Opción 1: Skip
        return []
        # Opción 2: Procesar por chunks (streaming)
        # return self._parse_large_file(file_path)
```

**Resultado**: Se skipea el archivo o se procesa por streaming.

#### E. Workspace con Miles de Archivos

**Problema**: Timeouts, exceso de memoria, >30 segundos de procesamiento.

**Solución**:
```python
# Límites configurables
MAX_FILES_PER_CATEGORY = 100
MAX_TOTAL_FILES = 500
PROCESSING_TIMEOUT = 300  # 5 minutos

# En FileScanner
def scan_workspace(self, workspace_id, workspace_name):
    files_by_category = {}
    total_count = 0
    
    for category in self.CATEGORIES:
        category_files = self._scan_category(category_dir)
        
        # Limitar por categoría
        if len(category_files) > MAX_FILES_PER_CATEGORY:
            logger.warning(f"Too many files in {category}: {len(category_files)}, limiting to {MAX_FILES_PER_CATEGORY}")
            category_files = category_files[:MAX_FILES_PER_CATEGORY]
        
        files_by_category[category] = category_files
        total_count += len(category_files)
        
        # Limitar total
        if total_count >= MAX_TOTAL_FILES:
            logger.warning(f"Reached max total files limit: {MAX_TOTAL_FILES}")
            break
    
    return files_by_category
```

**Resultado**: Se procesan máximo N archivos, se logea advertencia.

#### F. Generación de Reporte Excede Timeout

**Problema**: Generación toma >5 minutos.

**Solución**: Usar generación asíncrona (Fase 2):
```python
# En routes.py
@reporting_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_report():
    # Crear tarea asíncrona
    task = report_service.generate_report_async.delay(
        workspace_id=workspace_id,
        report_type=report_type,
        format=format
    )
    
    return jsonify({
        'success': True,
        'task_id': task.id,
        'status': 'processing',
        'status_url': f'/api/v1/reporting/status/{task.id}'
    }), 202  # Accepted
```

### 6.3. Logging de Errores

Estructura de logs:
```python
import logging
import traceback

logger = logging.getLogger(__name__)

# Niveles de logging
logger.debug("Detailed debug info")     # Desarrollo
logger.info("Normal operation")          # Información general
logger.warning("Recoverable issue")      # Warnings que no detienen proceso
logger.error("Serious error")            # Errores que afectan funcionalidad
logger.critical("System failure")        # Fallos críticos

# Formato de logs de error
logger.error(f"""
Parser Error Details:
- Parser: {parser.__class__.__name__}
- File: {file_path}
- Size: {file_path.stat().st_size} bytes
- Error: {str(e)}
- Traceback:
{traceback.format_exc()}
""")
```

### 6.4. Validación de Seguridad

#### Path Traversal Prevention
```python
from pathlib import Path

def validate_file_path(file_path: Path, workspace_dir: Path) -> bool:
    """Valida que file_path esté dentro de workspace_dir."""
    try:
        # Resolver paths absolutos
        file_absolute = file_path.resolve()
        workspace_absolute = workspace_dir.resolve()
        
        # Verificar que file está dentro de workspace
        return str(file_absolute).startswith(str(workspace_absolute))
    except Exception:
        return False

# Uso en FileScanner
for item in category_dir.iterdir():
    if not validate_file_path(item, workspace_dir):
        logger.warning(f"Security: Invalid path detected: {item}")
        continue
```

#### Sanitización de Nombres
```python
import re

def sanitize_filename(filename: str) -> str:
    """Sanitiza nombre de archivo para prevenir inyecciones."""
    # Permitir solo caracteres seguros
    safe_filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
    # Limitar longitud
    return safe_filename[:255]
```

### 6.5. Estrategia de Deduplicación

#### Criterios de Deduplicación

**Definición**: Dos findings son duplicados si representan el mismo hallazgo.

**Criterios por tipo**:

1. **Vulnerabilidades (CVE)**:
   ```python
   # Mismo CVE + mismo target = duplicado
   key = (finding.cve_id, finding.affected_target)
   ```

2. **Vulnerabilidades (sin CVE)**:
   ```python
   # Mismo título (normalizado) + mismo target + misma severidad
   title_normalized = finding.title.lower().strip()
   key = (title_normalized, finding.affected_target, finding.severity)
   ```

3. **Puertos abiertos**:
   ```python
   # Mismo IP + puerto + protocolo
   key = (finding.affected_target, finding.raw_data['port'], finding.raw_data['protocol'])
   ```

4. **Subdominios**:
   ```python
   # Mismo dominio (case-insensitive)
   key = finding.affected_target.lower()
   ```

#### Implementación Mejorada

```python
# En DataAggregator._deduplicate()

def _deduplicate(self, findings: List[ParsedFinding]) -> List[ParsedFinding]:
    """Deduplica findings usando criterios específicos por tipo."""
    
    seen = {}  # key -> finding (guardamos el primero)
    deduplicated = []
    
    for finding in findings:
        key = self._generate_dedup_key(finding)
        
        if key not in seen:
            seen[key] = finding
            deduplicated.append(finding)
        else:
            # Opcional: Mergear evidencia
            existing = seen[key]
            if finding.evidence and finding.evidence not in (existing.evidence or ''):
                existing.evidence = f"{existing.evidence}\n\n---\n\n{finding.evidence}"
    
    return deduplicated

def _generate_dedup_key(self, finding: ParsedFinding) -> tuple:
    """Genera clave de deduplicación según tipo de finding."""
    
    # CVE-based
    if finding.cve_id:
        return ('cve', finding.cve_id, finding.affected_target)
    
    # Port scan
    if finding.category == 'port_scan':
        port = finding.raw_data.get('port')
        protocol = finding.raw_data.get('protocol', 'tcp')
        return ('port', finding.affected_target, port, protocol)
    
    # Subdomain
    if finding.category == 'reconnaissance':
        return ('recon', finding.affected_target.lower())
    
    # Vulnerability (generic)
    if finding.category in ['vulnerability', 'web_vulnerability']:
        title_norm = finding.title.lower().strip()[:100]  # Truncar
        return ('vuln', title_norm, finding.affected_target, finding.severity)
    
    # Default
    return ('default', finding.title.lower()[:50], finding.affected_target)
```

---

## 7. PARSERS POR HERRAMIENTA

### 6.1. Parser Base (Abstracto)

```python
# parsers/base_parser.py

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class ParsedFinding:
    """Estructura estándar para un hallazgo."""
    title: str
    severity: str  # critical, high, medium, low, info
    description: str
    category: str  # recon, vuln, port, service, etc.
    affected_target: str  # IP, domain, URL
    evidence: Optional[str] = None
    remediation: Optional[str] = None
    cvss_score: Optional[float] = None
    cve_id: Optional[str] = None
    references: Optional[List[str]] = None
    raw_data: Optional[Dict[str, Any]] = None

class BaseParser(ABC):
    """Clase base para todos los parsers."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si este parser puede manejar el archivo."""
        pass
    
    @abstractmethod
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """Parsea el archivo y retorna lista de findings."""
        pass
    
    def _read_file(self, file_path: Path, encoding: str = 'utf-8') -> str:
        """Lee archivo con manejo de errores."""
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            self.logger.warning(f"UTF-8 decode failed for {file_path}, trying latin-1")
            return file_path.read_text(encoding='latin-1')
    
    def _safe_parse_json(self, file_path: Path) -> Optional[Dict]:
        """Parsea JSON con manejo de errores."""
        import json
        try:
            content = self._read_file(file_path)
            return json.loads(content)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error in {file_path}: {e}")
            return None
```

### 6.2. Parsers PRIORITARIOS (Fase 1)

#### A. Nmap Parser (XML)

```python
# parsers/scanning/nmap_parser.py

import xmltodict
from pathlib import Path
from typing import List
from ..base_parser import BaseParser, ParsedFinding

class NmapParser(BaseParser):
    """Parser para archivos XML de Nmap."""
    
    def can_parse(self, file_path: Path) -> bool:
        return (
            file_path.suffix == '.xml' and 
            'nmap' in file_path.stem.lower()
        )
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        findings = []
        
        try:
            content = self._read_file(file_path)
            data = xmltodict.parse(content)
            
            # Puede ser un host único o múltiples
            hosts = data.get('nmaprun', {}).get('host', [])
            if not isinstance(hosts, list):
                hosts = [hosts]
            
            for host in hosts:
                if not host:
                    continue
                
                # Extraer IP
                address = host.get('address', {})
                ip = address.get('@addr') if isinstance(address, dict) else address[0].get('@addr')
                
                # Extraer puertos
                ports = host.get('ports', {}).get('port', [])
                if not isinstance(ports, list):
                    ports = [ports]
                
                for port in ports:
                    state = port.get('state', {}).get('@state')
                    if state == 'open':
                        port_id = port.get('@portid')
                        service = port.get('service', {})
                        service_name = service.get('@name', 'unknown')
                        version = service.get('@version', '')
                        
                        finding = ParsedFinding(
                            title=f"Open Port: {port_id}/{port.get('@protocol', 'tcp')}",
                            severity='info',
                            description=f"Service: {service_name} {version}".strip(),
                            category='port_scan',
                            affected_target=ip,
                            raw_data={
                                'port': port_id,
                                'protocol': port.get('@protocol'),
                                'service': service_name,
                                'version': version
                            }
                        )
                        findings.append(finding)
            
            self.logger.info(f"Parsed {len(findings)} findings from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error parsing Nmap XML {file_path}: {e}")
        
        return findings
```

#### B. Nuclei Parser (JSONL)

```python
# parsers/vulnerability/nuclei_parser.py

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
        'info': 'info'
    }
    
    def can_parse(self, file_path: Path) -> bool:
        return (
            file_path.suffix == '.jsonl' and 
            'nuclei' in file_path.stem.lower()
        )
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        findings = []
        
        try:
            content = self._read_file(file_path)
            
            # JSONL = una línea JSON por línea
            for line_num, line in enumerate(content.strip().split('\n'), 1):
                if not line.strip():
                    continue
                
                try:
                    data = json.loads(line)
                    
                    info = data.get('info', {})
                    template_id = data.get('template-id', 'unknown')
                    matched_at = data.get('matched-at', '')
                    
                    severity = info.get('severity', 'info').lower()
                    severity = self.SEVERITY_MAP.get(severity, 'info')
                    
                    finding = ParsedFinding(
                        title=info.get('name', template_id),
                        severity=severity,
                        description=info.get('description', ''),
                        category='vulnerability',
                        affected_target=matched_at,
                        evidence=data.get('matched-line', ''),
                        references=info.get('reference', []),
                        raw_data=data
                    )
                    findings.append(finding)
                    
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Invalid JSON at line {line_num} in {file_path}: {e}")
            
            self.logger.info(f"Parsed {len(findings)} vulnerabilities from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error parsing Nuclei JSONL {file_path}: {e}")
        
        return findings
```

#### C. Nikto Parser (JSON)

```python
# parsers/vulnerability/nikto_parser.py

from pathlib import Path
from typing import List
from ..base_parser import BaseParser, ParsedFinding

class NiktoParser(BaseParser):
    """Parser para archivos JSON de Nikto."""
    
    def can_parse(self, file_path: Path) -> bool:
        return (
            file_path.suffix == '.json' and 
            'nikto' in file_path.stem.lower()
        )
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        findings = []
        
        try:
            data = self._safe_parse_json(file_path)
            if not data:
                return findings
            
            vulnerabilities = data.get('vulnerabilities', [])
            host = data.get('host', 'unknown')
            port = data.get('port', 80)
            
            for vuln in vulnerabilities:
                finding = ParsedFinding(
                    title=f"Nikto: {vuln.get('msg', 'Unknown vulnerability')}",
                    severity=self._map_nikto_severity(vuln),
                    description=vuln.get('msg', ''),
                    category='web_vulnerability',
                    affected_target=f"{host}:{port}{vuln.get('url', '')}",
                    references=[vuln.get('OSVDB', '')] if vuln.get('OSVDB') else None,
                    raw_data=vuln
                )
                findings.append(finding)
            
            self.logger.info(f"Parsed {len(findings)} findings from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error parsing Nikto JSON {file_path}: {e}")
        
        return findings
    
    def _map_nikto_severity(self, vuln: dict) -> str:
        """Mapea severidad de Nikto (no tiene campo severity nativo)."""
        msg = vuln.get('msg', '').lower()
        
        if any(word in msg for word in ['sql injection', 'rce', 'remote code']):
            return 'critical'
        elif any(word in msg for word in ['xss', 'csrf', 'authentication']):
            return 'high'
        elif any(word in msg for word in ['disclosure', 'directory listing']):
            return 'medium'
        else:
            return 'low'
```

#### D. Subfinder Parser (TXT)

```python
# parsers/reconnaissance/subfinder_parser.py

from pathlib import Path
from typing import List
from ..base_parser import BaseParser, ParsedFinding

class SubfinderParser(BaseParser):
    """Parser para archivos TXT de Subfinder."""
    
    def can_parse(self, file_path: Path) -> bool:
        return (
            file_path.suffix == '.txt' and 
            'subfinder' in file_path.stem.lower()
        )
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        findings = []
        
        try:
            content = self._read_file(file_path)
            subdomains = [line.strip() for line in content.split('\n') if line.strip()]
            
            for subdomain in subdomains:
                finding = ParsedFinding(
                    title=f"Subdomain: {subdomain}",
                    severity='info',
                    description=f"Discovered subdomain: {subdomain}",
                    category='reconnaissance',
                    affected_target=subdomain,
                    raw_data={'subdomain': subdomain}
                )
                findings.append(finding)
            
            self.logger.info(f"Parsed {len(findings)} subdomains from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error parsing Subfinder TXT {file_path}: {e}")
        
        return findings
```

---

## 7. TIPOS DE REPORTES

### 7.1. Reporte Ejecutivo (Executive Summary)

**Audiencia**: C-level, Management, Decision makers

**Contenido**:
1. **Portada**
   - Logo
   - Título del reporte
   - Cliente
   - Fecha
   - Confidencialidad

2. **Executive Summary** (1 página)
   - Risk Score global (0-10)
   - Indicador visual de riesgo
   - Top 3-5 vulnerabilidades críticas
   - Impacto potencial al negocio
   - Recomendaciones prioritarias (bullets)

3. **Risk Overview** (1 página)
   - Gráfico de distribución de vulnerabilidades por severidad (pie chart)
   - Timeline de remediación sugerido (gantt/bars)
   - Comparación con industry benchmarks (opcional)

4. **Key Findings** (2-3 páginas)
   - Solo las vulnerabilidades critical y high
   - Descripción no técnica
   - Impacto de negocio
   - Pasos de remediación (alto nivel)

5. **Methodology Overview** (1 página)
   - Scope del assessment
   - Herramientas utilizadas (resumen)
   - Fechas de ejecución

**Características**:
- Máximo 8-10 páginas
- Lenguaje no técnico
- Muchos gráficos y visualizaciones
- Colores según severidad
- Executive friendly

---

### 7.2. Reporte Técnico (Technical Report)

**Audiencia**: Security team, DevOps, Engineers, Pentesters

**Contenido**:
1. **Portada**

2. **Executive Summary** (breve)

3. **Methodology** (2-3 páginas)
   - Scope detallado
   - Herramientas y versiones
   - Técnicas utilizadas
   - Limitaciones y assumptions
   - Testing timeline

4. **Detailed Findings** (bulk del reporte)
   Para cada vulnerabilidad:
   - **Título y severity** (con CVSS score si aplica)
   - **Affected systems/URLs** (lista completa)
   - **Technical description**
   - **Proof of Concept** (comandos, requests, screenshots)
   - **Evidence** (output de herramientas, logs)
   - **Impact analysis** (técnico y de negocio)
   - **Remediation steps** (detallados, con código si aplica)
   - **References** (CVE, CWE, OWASP, etc.)

5. **Summary Statistics**
   - Total hosts scanned
   - Total ports open
   - Total vulnerabilities by severity
   - Total services enumerated
   - Gráficos de distribución

6. **Appendices**
   - A: Scan outputs (puertos abiertos completo)
   - B: Service enumeration (lista completa)
   - C: Raw tool outputs (si es relevante)
   - D: Glossary

**Características**:
- 30-100+ páginas (depende de findings)
- Lenguaje técnico
- Evidencias detalladas
- Código y comandos
- Referencias técnicas

---

### 7.3. Reporte de Compliance (Compliance Report)

**Audiencia**: Auditors, Compliance officers, Risk management

**Contenido**:
1. **Portada**

2. **Executive Summary**

3. **Compliance Framework Mapping**
   - Mapeo a controles de framework (ej: ISO 27001, NIST, PCI-DSS)
   - Estado de cada control (Pass/Fail/Partial)
   - Findings asociados a cada control

4. **Controls Assessment**
   - Por cada control:
     - Descripción del control
     - Evidencia de testing
     - Resultado (compliant/non-compliant)
     - Gaps identificados
     - Remediación requerida

5. **Risk Assessment**
   - Risk register
   - Inherent vs residual risk
   - Risk treatment plan

6. **Attestation** (opcional)
   - Firma del pentester
   - Scope statement
   - Limitations

**Características**:
- Estructura según framework específico
- Lenguaje formal
- Evidencias de compliance
- Trazabilidad a controles

---

## 8. FLUJO DE GENERACIÓN

```python
# Pseudocódigo del flujo completo

def generate_report(workspace_id: int, report_type: str, format: str) -> str:
    """
    Genera un reporte completo.
    
    Args:
        workspace_id: ID del workspace
        report_type: 'executive' | 'technical' | 'compliance'
        format: 'pdf' | 'docx' | 'html'
    
    Returns:
        Path al archivo generado
    """
    
    # 1. FASE: Descubrimiento de archivos
    scanner = FileScanner()
    files = scanner.scan_workspace(workspace_id)
    # Output: {
    #   'recon': [Path('subfinder_123.txt'), ...],
    #   'scans': [Path('nmap_456.xml'), ...],
    #   'vuln_scans': [Path('nuclei_789.jsonl'), ...],
    #   ...
    # }
    
    # 2. FASE: Parsing
    parser_manager = ParserManager()
    all_findings = []
    
    for category, file_list in files.items():
        for file_path in file_list:
            parser = parser_manager.get_parser(file_path)
            if parser:
                findings = parser.parse(file_path)
                all_findings.extend(findings)
    
    # Output: List[ParsedFinding] (~1000+ findings)
    
    # 3. FASE: Consolidación y deduplicación
    aggregator = DataAggregator()
    consolidated = aggregator.consolidate(all_findings)
    # Output: {
    #   'vulnerabilities': List[ParsedFinding],  # Deduplicado
    #   'open_ports': List[ParsedFinding],
    #   'subdomains': List[ParsedFinding],
    #   'services': List[ParsedFinding],
    #   'secrets': List[ParsedFinding],
    # }
    
    # 4. FASE: Cálculo de métricas
    calculator = RiskCalculator()
    metrics = calculator.calculate(consolidated)
    # Output: {
    #   'risk_score': 7.8,
    #   'severity_distribution': {'critical': 5, 'high': 12, ...},
    #   'affected_hosts': 23,
    #   'total_findings': 145,
    #   ...
    # }
    
    # 5. FASE: Construcción del reporte
    builder = ReportBuilder(report_type)
    report_data = builder.build(
        workspace_id=workspace_id,
        findings=consolidated,
        metrics=metrics
    )
    # Output: Dict con toda la estructura del reporte
    
    # 6. FASE: Generación de gráficos
    chart_builder = ChartBuilder()
    charts = chart_builder.generate_charts(metrics, consolidated)
    report_data['charts'] = charts
    
    # 7. FASE: Generación del documento
    generator = get_generator(format)  # PDFGenerator | DOCXGenerator | HTMLGenerator
    output_file = generator.generate(report_data)
    
    # 8. FASE: Guardar en BD
    report_record = Report(
        workspace_id=workspace_id,
        title=report_data['title'],
        report_type=report_type,
        format=format,
        file_path=str(output_file),
        file_size=output_file.stat().st_size,
        status='completed',
        generated_at=datetime.utcnow()
    )
    db.session.add(report_record)
    db.session.commit()
    
    return str(output_file)
```

---

## 9. MODELO DE DATOS

### 9.1. Extensión del Modelo Report

```python
# models/report.py

from datetime import datetime
from extensions import db
import hashlib

class Report(db.Model):
    """Modelo de reporte generado."""
    
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Identificación
    title = db.Column(db.String(255), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # executive, technical, compliance
    format = db.Column(db.String(20), nullable=False)  # pdf, docx, html
    
    # Versionado (NUEVO)
    version = db.Column(db.Integer, default=1, nullable=False)  # Incrementa al regenerar
    is_latest = db.Column(db.Boolean, default=True, nullable=False)  # Solo una versión latest=True
    
    # Contenido
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # bytes
    file_hash = db.Column(db.String(64))  # SHA-256 para verificación de integridad (NUEVO)
    
    # Metadata del reporte
    total_findings = db.Column(db.Integer, default=0)
    critical_count = db.Column(db.Integer, default=0)
    high_count = db.Column(db.Integer, default=0)
    medium_count = db.Column(db.Integer, default=0)
    low_count = db.Column(db.Integer, default=0)
    info_count = db.Column(db.Integer, default=0)
    risk_score = db.Column(db.Float)  # 0-10
    
    # Metadata adicional (NUEVO)
    files_processed = db.Column(db.Integer, default=0)  # Cantidad de archivos parseados
    tools_used = db.Column(db.JSON)  # Lista de herramientas detectadas ['nmap', 'nuclei', ...]
    scan_date_range = db.Column(db.JSON)  # {'start': '...', 'end': '...'}
    generation_time_seconds = db.Column(db.Float)  # Tiempo que tomó generar
    
    # Estado
    status = db.Column(db.String(20), default='pending', nullable=False)
    # Estados: pending, generating, completed, failed
    
    error_message = db.Column(db.Text)  # Si falla
    
    # Timestamps
    generated_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    workspace = db.relationship('Workspace', back_populates='reports')
    user = db.relationship('User', back_populates='reports')
    
    def calculate_file_hash(self):
        """Calcula SHA-256 hash del archivo para verificación de integridad."""
        from pathlib import Path
        
        file_path = Path(self.file_path)
        if not file_path.exists():
            return None
        
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Leer en chunks para archivos grandes
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verifica integridad del archivo usando el hash guardado."""
        if not self.file_hash:
            return False
        
        current_hash = self.calculate_file_hash()
        return current_hash == self.file_hash
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'report_type': self.report_type,
            'format': self.format,
            'version': self.version,
            'is_latest': self.is_latest,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'total_findings': self.total_findings,
            'severity_counts': {
                'critical': self.critical_count,
                'high': self.high_count,
                'medium': self.medium_count,
                'low': self.low_count,
                'info': self.info_count
            },
            'risk_score': self.risk_score,
            'files_processed': self.files_processed,
            'tools_used': self.tools_used,
            'scan_date_range': self.scan_date_range,
            'generation_time_seconds': self.generation_time_seconds,
            'status': self.status,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'created_at': self.created_at.isoformat()
        }
```

---

## 10. API ENDPOINTS

```python
# modules/reporting/routes.py

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from .report_service import ReportService
from pathlib import Path

reporting_bp = Blueprint('reporting', __name__, url_prefix='/api/v1/reporting')
report_service = ReportService()

@reporting_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_report():
    """
    Genera un nuevo reporte.
    
    Body:
    {
        "workspace_id": 123,
        "report_type": "executive",  // executive | technical | compliance
        "format": "pdf",              // pdf | docx | html
        "title": "Security Assessment Report" // opcional
    }
    
    Returns:
    {
        "success": true,
        "report_id": 456,
        "message": "Report generated successfully",
        "download_url": "/api/v1/reporting/download/456"
    }
    """
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Validaciones
        workspace_id = data.get('workspace_id')
        report_type = data.get('report_type', 'technical')
        format = data.get('format', 'pdf')
        title = data.get('title')
        
        if not workspace_id:
            return jsonify({
                'success': False,
                'error': 'workspace_id is required'
            }), 400
        
        if report_type not in ['executive', 'technical', 'compliance']:
            return jsonify({
                'success': False,
                'error': 'Invalid report_type'
            }), 400
        
        if format not in ['pdf', 'docx', 'html']:
            return jsonify({
                'success': False,
                'error': 'Invalid format'
            }), 400
        
        # Generar reporte (puede tomar tiempo, considerar async)
        report = report_service.generate_report(
            workspace_id=workspace_id,
            report_type=report_type,
            format=format,
            title=title,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'report_id': report.id,
            'message': 'Report generated successfully',
            'download_url': f'/api/v1/reporting/download/{report.id}',
            'report': report.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reporting_bp.route('/download/<int:report_id>', methods=['GET'])
@jwt_required()
def download_report(report_id):
    """
    Descarga un reporte generado.
    
    Returns: Archivo (PDF/DOCX/HTML)
    """
    try:
        user_id = get_jwt_identity()
        report = report_service.get_report(report_id, user_id)
        
        if not report:
            return jsonify({
                'success': False,
                'error': 'Report not found'
            }), 404
        
        file_path = Path(report.file_path)
        
        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': 'Report file not found'
            }), 404
        
        mimetype_map = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'html': 'text/html'
        }
        
        return send_file(
            file_path,
            mimetype=mimetype_map.get(report.format, 'application/octet-stream'),
            as_attachment=True,
            download_name=f"{report.title}.{report.format}"
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reporting_bp.route('/list/<int:workspace_id>', methods=['GET'])
@jwt_required()
def list_reports(workspace_id):
    """
    Lista todos los reportes de un workspace.
    
    Returns:
    {
        "success": true,
        "reports": [...]
    }
    """
    try:
        user_id = get_jwt_identity()
        reports = report_service.list_reports(workspace_id, user_id)
        
        return jsonify({
            'success': True,
            'reports': [r.to_dict() for r in reports]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reporting_bp.route('/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """Elimina un reporte."""
    try:
        user_id = get_jwt_identity()
        report_service.delete_report(report_id, user_id)
        
        return jsonify({
            'success': True,
            'message': 'Report deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

## 11. PRIORIDADES DE IMPLEMENTACIÓN

### FASE 1: MVP (Minimum Viable Product) - 1-2 semanas

**Objetivo**: Generar reporte técnico básico en PDF con parsers core y tests

**Tareas**:
1. ✅ Estructura base del módulo (en `services/reporting/`)
2. ✅ BaseParser + ParserManager
3. ✅ 4 parsers prioritarios:
   - NmapParser (puertos)
   - NucleiParser (vulnerabilidades)
   - SubfinderParser (recon)
   - NiktoParser (web vulns)
4. ✅ FileScanner (auto-descubrimiento con límites)
5. ✅ DataAggregator con deduplicación mejorada
6. ✅ RiskCalculator básico
7. ✅ Manejo de errores robusto (fail gracefully)
8. ✅ Validación de seguridad (path traversal, sanitización)
9. ✅ Template HTML simple para reporte técnico
10. ✅ PDFGenerator con WeasyPrint
11. ✅ API endpoint /generate (solo technical + pdf, sync)
12. ✅ Modelo Report en BD (con versioning, hash, metadata)
13. ✅ **Tests unitarios** para parsers y componentes core
14. ✅ **Fixtures de prueba** (archivos de ejemplo)

**Entregable**: Reporte técnico PDF funcional con datos de 4 herramientas principales, manejo robusto de errores y tests.

**Limitaciones conocidas**:
- Generación síncrona (puede tomar tiempo en workspaces grandes)
- Solo 4 parsers (suficiente para validar arquitectura)
- Solo formato PDF

---

### FASE 2: Generación Asíncrona y Más Parsers - 1 semana

**Objetivo**: Soportar workspaces grandes y agregar más herramientas

**Tareas**:
1. ✅ **Generación asíncrona con Celery**:
   ```python
   # services/reporting/tasks.py
   from celery import shared_task
   
   @shared_task(bind=True)
   def generate_report_async(self, workspace_id, report_type, format, user_id):
       # Implementación...
       pass
   ```
2. ✅ Endpoint de status: `/api/v1/reporting/status/<task_id>`
3. ✅ Notificaciones (email/websocket) cuando reporte está listo
4. ✅ Cola de prioridad para reportes urgentes
5. ✅ 10 parsers adicionales:
   - Reconnaissance: Amass, theHarvester, DNSRecon
   - Scanning: RustScan, Masscan
   - Vulnerability: SQLMap, TestSSL, WPScan
   - Enumeration: Enum4linux, SMBMap
6. ✅ Procesamiento por chunks para archivos grandes
7. ✅ Progress bar / porcentaje de completitud
8. ✅ Tests de integración

**Entregable**: Sistema asíncrono robusto que maneja workspaces con miles de archivos.

**Mejoras**:
- Timeouts configurables
- Cancelación de tareas
- Retry automático en fallos

---

### FASE 3: Reporte Ejecutivo y Visualizaciones - 3-4 días

**Objetivo**: Reporte para management con gráficos profesionales

**Tareas**:
1. ✅ Template HTML para executive summary
2. ✅ Generación de gráficos con Plotly:
   - Pie chart de severidades
   - Bar chart de findings por categoría
   - Risk score gauge
   - Timeline de escaneos
3. ✅ Cálculo de risk score mejorado (con benchmarks)
4. ✅ Top 5 vulnerabilidades críticas
5. ✅ Recomendaciones priorizadas con ROI
6. ✅ Comparación con industry standards (opcional)
7. ✅ API endpoint para executive report
8. ✅ Export de gráficos como PNG (con Kaleido)

**Entregable**: Reporte ejecutivo PDF profesional con visualizaciones de calidad.

---

### FASE 4: Parsers Completos - 1 semana

**Objetivo**: Soportar todas las 42+ herramientas

**Tareas**:
1. ✅ Parsers restantes de reconnaissance (5 tools)
2. ✅ Parsers restantes de scanning (2 tools)
3. ✅ Parsers restantes de enumeration (2 tools)
4. ✅ Parsers restantes de vulnerability (4 tools)
5. ✅ Parsers de Active Directory (5 tools)
6. ✅ Parsers de Cloud (5 tools)
7. ✅ Parsers de Container (6 tools)
8. ✅ Tests para cada parser nuevo
9. ✅ Documentación de cada parser

**Entregable**: Todos los archivos de la plataforma son parseables.

---

### FASE 5: Formatos Adicionales - 2-3 días

**Objetivo**: DOCX y HTML standalone

**Tareas**:
1. ✅ DOCXGenerator con python-docx
2. ✅ Estilos de Word personalizables
3. ✅ HTMLGenerator standalone (con CSS embebido)
4. ✅ Adaptación de templates para cada formato
5. ✅ API soporta múltiples formatos
6. ✅ Compresión de reportes grandes (ZIP)

**Entregable**: Reportes en PDF, DOCX y HTML.

---

### FASE 6: Reporte de Compliance - 1 semana

**Objetivo**: Mapeo a frameworks de seguridad

**Tareas**:
1. ✅ Mapeo de findings a controles:
   - ISO 27001
   - NIST CSF
   - PCI-DSS
   - CIS Controls
2. ✅ Template de compliance
3. ✅ Assessment de controles (Pass/Fail/Partial)
4. ✅ Gap analysis
5. ✅ Risk register
6. ✅ Generador de compliance report
7. ✅ API endpoint para compliance

**Entregable**: Reporte de compliance mapeado a frameworks estándar.

---

### FASE 7: Mejoras y Optimización - Ongoing

**Tareas**:
1. ✅ Cache de parsers (Redis)
2. ✅ Compresión inteligente de reportes
3. ✅ Customización de templates por cliente:
   - Logo personalizado
   - Colores corporativos
   - Footer/header customizados
4. ✅ Exportar raw data (CSV, JSON, Excel)
5. ✅ Comparación de reportes (trends):
   - Vulnerabilidades nuevas vs resueltas
   - Mejora de risk score
   - Gráficos de tendencia
6. ✅ Integración con ticketing (Jira, ServiceNow)
7. ✅ Multi-idioma (i18n):
   - Español
   - Inglés
   - Portugués
8. ✅ Generación de reportes periódicos (scheduled)
9. ✅ API para consultar findings sin generar reporte completo
10. ✅ Webhooks cuando reporte está listo

---

## 12. DEPENDENCIAS Y REQUIREMENTS

### requirements.txt - Módulo de Reportería

```txt
# Core parsing
xmltodict==0.13.0              # Nmap XML parsing
pandas==2.1.4                  # Data manipulation
numpy==1.26.2                  # Numerical operations

# Report generation
weasyprint==60.1               # PDF generation from HTML/CSS
python-docx==1.1.0             # DOCX generation
jinja2==3.1.2                  # HTML templating (ya incluido con Flask)

# Visualizations
plotly==5.18.0                 # Interactive charts
kaleido==0.2.1                 # Static image export for Plotly

# Async processing (Fase 2)
celery==5.3.4                  # Task queue
redis==5.0.1                   # Celery broker/backend

# Utilities
pathlib                        # stdlib - Path manipulation
typing                         # stdlib - Type hints
dataclasses                    # stdlib - Data structures
logging                        # stdlib - Logging
json                           # stdlib - JSON parsing
csv                            # stdlib - CSV parsing
hashlib                        # stdlib - File hashing

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.12.0
```

### Verificación de Compatibilidad

```bash
# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python -c "import weasyprint; print(weasyprint.__version__)"
python -c "import plotly; print(plotly.__version__)"
python -c "import xmltodict; print(xmltodict.__version__)"
```

---

## 13. INTEGRACIÓN CON CÓDIGO EXISTENTE

### 13.1. Estructura Actual vs Nueva

**Actual**:
```
services/
└── reporting/
    └── reporting_service.py  # Servicio existente (básico)
```

**Nueva**:
```
services/
└── reporting/
    ├── reporting_service.py     # EXTENDER (no reemplazar)
    ├── routes.py                # NUEVO
    ├── core/                    # NUEVO
    ├── parsers/                 # NUEVO
    ├── generators/              # NUEVO
    └── templates/               # NUEVO
```

### 13.2. Estrategia de Migración

**Opción 1: Extensión** (RECOMENDADO)
```python
# services/reporting/reporting_service.py (ACTUAL)

class ReportingService:
    """Servicio existente - mantener compatibilidad."""
    
    def generate_basic_report(self, workspace_id):
        """Método existente - NO TOCAR."""
        # Código actual...
        pass

# services/reporting/report_service.py (NUEVO)

from .reporting_service import ReportingService as LegacyReportingService

class ReportService:
    """Nuevo servicio con funcionalidad completa."""
    
    def __init__(self):
        self.legacy_service = LegacyReportingService()
    
    def generate_report(self, workspace_id, report_type, format):
        """Nueva implementación completa."""
        # Nueva lógica...
        pass
    
    def generate_basic_report_legacy(self, workspace_id):
        """Wrapper al método legacy por compatibilidad."""
        return self.legacy_service.generate_basic_report(workspace_id)
```

**Opción 2: Reemplazo gradual**
1. Mantener `reporting_service.py` actual sin cambios
2. Crear `report_service_v2.py` con nueva implementación
3. Actualizar rutas para usar v2
4. Deprecar v1 gradualmente
5. Eliminar v1 después de 2-3 sprints

### 13.3. Backwards Compatibility

```python
# En routes.py - mantener endpoint legacy

@reporting_bp.route('/generate_basic', methods=['POST'])
@jwt_required()
def generate_basic_report_legacy():
    """
    Endpoint legacy para compatibilidad.
    DEPRECATED: Usar /generate en su lugar.
    """
    # Usar servicio legacy
    pass
```

---

## 14. CONSIDERACIONES DE PERFORMANCE

### 14.1. Benchmarks Esperados

| Escenario | Archivos | Findings | Tiempo Esperado | Status |
|-----------|----------|----------|-----------------|--------|
| Small workspace | 10-50 | <500 | <10 segundos | ✅ Sync OK |
| Medium workspace | 50-200 | 500-2000 | 10-30 segundos | ⚠️ Sync límite |
| Large workspace | 200-500 | 2000-5000 | 30-120 segundos | ❌ Requiere Async |
| Very large workspace | >500 | >5000 | >120 segundos | ❌ Requiere Async + Limits |

### 14.2. Optimizaciones

1. **Parsing paralelo** (Fase 2):
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor(max_workers=4) as executor:
       futures = [executor.submit(parser.parse, file) for file in files]
       results = [f.result() for f in futures]
   ```

2. **Cache de parsers** (Fase 7):
   - Redis cache de findings ya parseados
   - TTL: 1 hora
   - Invalidar al crear nuevo scan

3. **Lazy loading de gráficos**:
   - Generar gráficos solo si se solicita executive report
   - Technical report puede omitir gráficos pesados

---

## MÉTRICAS DE ÉXITO (ACTUALIZADAS)

### Técnicas
- ✅ Parsear ≥90% de archivos generados (100% puede no ser realista)
- ✅ Generar reporte small workspace en <10 segundos
- ✅ Generar reporte medium workspace en <30 segundos (con async desde Fase 2)
- ✅ 0 errores críticos que detengan la generación completa
- ✅ Test coverage ≥80% (incluido desde Fase 1)
- ✅ Logs detallados para debugging
- ✅ Manejo robusto de edge cases (archivos corruptos, muy grandes, etc.)

### Funcionales
- ✅ 3 tipos de reportes (executive, technical, compliance)
- ✅ 3 formatos (PDF, DOCX, HTML)
- ✅ Gráficos profesionales (Plotly)
- ✅ Deduplicación efectiva (>80% de duplicados eliminados)
- ✅ Versionado de reportes
- ✅ Verificación de integridad (hash)
- ✅ Generación asíncrona para workspaces grandes

### Negocio
- ✅ Clientes satisfechos con reportes (feedback positivo)
- ✅ Reducción de tiempo manual >80% vs proceso actual
- ✅ Diferenciación competitiva clara
- ✅ Facilita ventas (demos con reportes profesionales)

### Seguridad
- ✅ Path traversal prevention implementado
- ✅ Sanitización de inputs
- ✅ Validación de permisos de workspace
- ✅ Hash de archivos para verificación de integridad

---

## PREGUNTAS PARA ACLARAR (PENDIENTES)

1. **¿Se mantiene el módulo actual o se reemplaza completamente?**
   - **Recomendación**: Extensión gradual, mantener compatibilidad con legacy

2. **¿Hay presupuesto de tiempo realista?**
   - Fase 1 (MVP): 1-2 semanas ✅ Realista con desarrollador experimentado
   - Fase 2 (Async): 1 semana ✅ Realista
   - Fases 3-6: 2-3 semanas ✅ Realista
   - **Total**: ~5-6 semanas para sistema completo

3. **¿Se necesita soporte para reportes multi-idioma?**
   - **Respuesta pendiente**: Considerar para Fase 7 si es necesario

4. **¿Hay requisitos de branding/plantillas personalizadas por cliente?**
   - **Respuesta pendiente**: Considerar para Fase 7 si hay clientes enterprise

5. **¿Qué hacer con reportes existentes al migrar?**
   - **Recomendación**: Mantener backward compatibility, no migrar reportes viejos

---

## RIESGOS Y MITIGACIONES

### Riesgo 1: Performance en workspaces muy grandes
**Mitigación**: 
- Límites configurables de archivos
- Generación asíncrona (Fase 2)
- Timeouts y cancelación

### Riesgo 2: Parsers fallan con formatos inesperados
**Mitigación**:
- Fail gracefully (no detener generación completa)
- Logging detallado
- Tests con fixtures variados

### Riesgo 3: WeasyPrint tiene limitaciones con CSS complejo
**Mitigación**:
- Usar CSS simple y testeado
- Fallback a HTML si PDF falla
- Considerar ReportLab como alternativa en Fase 7

### Riesgo 4: Sobrecarga del servidor con múltiples reportes simultáneos
**Mitigación**:
- Cola de prioridad con Celery
- Límite de workers
- Rate limiting en API

### Riesgo 5: Archivos de resultados cambian formato
**Mitigación**:
- Parsers versionados
- Validación de formato antes de parsear
- Alertas cuando formato no reconocido

---

## NOTAS FINALES

Este documento es la **especificación completa ACTUALIZADA** del módulo de reportería, incorporando:

✅ Observaciones de seguridad y robustez
✅ Manejo detallado de errores y edge cases
✅ Estrategia de deduplicación mejorada
✅ Modelo de datos extendido (versioning, hash, metadata)
✅ Generación asíncrona desde Fase 2
✅ Tests incluidos desde Fase 1
✅ Integración con código existente documentada
✅ Consideraciones de performance realistas
✅ Dependencias completas y verificadas

**Próximos pasos**:
1. Revisar y aprobar esta especificación actualizada
2. Usar el PROMPT actualizado para Cursor
3. Implementar en fases según prioridades
4. Iterar basado en feedback y métricas

**Autor**: Claude AI + Equipo
**Fecha**: Diciembre 2025
**Versión**: 2.0 (con mejoras sustanciales)