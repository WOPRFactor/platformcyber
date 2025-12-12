# Análisis del Sistema de Archivos de Resultados

## 1. ESTRUCTURA DE DIRECTORIOS

### Ruta Base
- **Directorio principal de workspaces**: `/workspaces/` (configurable con `WORKSPACES_BASE_DIR`)
- **Fallback si no hay permisos**: `{proyecto}/platform/backend/workspaces/`
- **Directorio temporal del proyecto**: `{proyecto}/platform/backend/tmp/` (usado como fallback)

### Estructura por Workspace

Cada workspace tiene su propio directorio con estructura:

```
/workspaces/{workspace_name_sanitizado}/
├── recon/              # Reconnaissance (reconocimiento)
├── scans/              # Port scanning (escaneo de puertos)
├── enumeration/        # Enumeración de servicios
├── vuln_scans/         # Vulnerability scanning (escaneo de vulnerabilidades)
├── exploitation/       # Explotación
├── postexploit/        # Post-explotación
├── ad_scans/           # Active Directory scans
└── cloud_scans/        # Cloud security scans
```

### Ejemplo Real

```
/workspaces/kopernicus_tech/
├── enumeration/
│   ├── nmap_ssh_863.xml
│   ├── nmap_ssh_863.xml.nmap
│   ├── nmap_ssh_863.xml.gnmap
│   ├── nmap_dns_866.xml
│   ├── enum4linux_860.txt
│   ├── smbmap_861.txt
│   └── sslscan_873.txt
├── recon/
├── scans/
├── vuln_scans/
│   ├── nuclei_877.jsonl
│   ├── nikto_875.json
│   ├── sqlmap_878/
│   │   ├── www.kopernicus.tech/
│   │   │   ├── target.txt
│   │   │   ├── log
│   │   │   └── session.sqlite
│   │   ├── results-12072025_0524am.csv
│   │   └── log
│   ├── testssl_880.json
│   └── testssl_880.html
└── ...
```

### Código de Generación de Estructura

**Archivo**: `utils/workspace_filesystem.py`

```python
def create_workspace_directory_structure(workspace_id: int, workspace_name: str) -> Path:
    """Crea estructura completa de directorios para un workspace."""
    workspace_dir = get_workspace_dir(workspace_id, workspace_name)
    
    categories = [
        'recon',
        'scans',
        'enumeration',
        'vuln_scans',
        'exploitation',
        'postexploit',
        'ad_scans',
        'cloud_scans'
    ]
    
    for category in categories:
        category_dir = workspace_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
    
    return workspace_dir
```

---

## 2. LISTA DE ARCHIVOS GENERADOS POR MÓDULO

### 2.1. RECONNAISSANCE (`recon/`)

| Herramienta | Formato | Nombre Archivo | Ejemplo |
|------------|---------|----------------|---------|
| Subfinder | `.txt` | `subfinder_{scan_id}.txt` | `subfinder_123.txt` |
| Amass | `.txt` | `amass_{scan_id}.txt` | `amass_124.txt` |
| theHarvester | `.json` | `theHarvester_{scan_id}.json` | `theHarvester_125.json` |
| DNSRecon | `.json` | `dnsrecon_{scan_id}.json` | `dnsrecon_126.json` |
| Shodan | `.json` | `shodan_{scan_id}.json` | `shodan_127.json` |
| GitLeaks | `.json` | `gitleaks_{scan_id}.json` | `gitleaks_128.json` |
| TruffleHog | `.json` | `trufflehog_{scan_id}.json` | `trufflehog_129.json` |
| Hunter.io | `.json` | `hunter_io_{scan_id}.json` | `hunter_io_130.json` |
| Censys | `.json` | `censys_{scan_id}.json` | `censys_131.json` |

**Código de generación** (`services/reconnaissance/base.py`):
```python
def _get_output_file(self, scan_id: int, tool: str, category: str = 'recon') -> Path:
    workspace_output_dir = get_workspace_output_dir_from_scan(scan_id, category)
    
    extensions = {
        'theHarvester': '.json',
        'dnsrecon': '.json',
        'shodan': '.json',
        'gitleaks': '.json',
        'trufflehog': '.json',
        'hunter_io': '.json',
        'censys': '.json'
    }
    ext = extensions.get(tool, '.txt')
    return workspace_output_dir / f'{tool}_{scan_id}{ext}'
```

### 2.2. PORT SCANNING (`scans/`)

| Herramienta | Formato | Nombre Archivo | Ejemplo |
|------------|---------|----------------|---------|
| Nmap | `.xml`, `.txt`, `.gnmap` | `nmap_{scan_id}.xml` | `nmap_863.xml` |
| RustScan | `.txt` | `rustscan_{scan_id}.txt` | `rustscan_864.txt` |
| Masscan | `.xml` | `masscan_{scan_id}.xml` | `masscan_865.xml` |
| Naabu | `.txt` | `naabu_{scan_id}.txt` | `naabu_866.txt` |

**Código de generación** (`services/scanning/tools/nmap_scanner.py`):
```python
workspace_output_dir = self._get_workspace_output_dir(scan.id, 'scans')
output_file = str(workspace_output_dir / f'nmap_{scan.id}')
# Genera múltiples formatos:
# - {output_file}.xml (XML estándar)
# - {output_file}.txt (formato normal)
# - {output_file}.gnmap (formato grepeable)
```

### 2.3. ENUMERATION (`enumeration/`)

| Herramienta | Formato | Nombre Archivo | Ejemplo |
|------------|---------|----------------|---------|
| Nmap (servicios específicos) | `.xml`, `.txt`, `.gnmap` | `nmap_{servicio}_{scan_id}.xml` | `nmap_ssh_863.xml` |
| Enum4linux | `.txt` | `enum4linux_{scan_id}.txt` | `enum4linux_860.txt` |
| SMBMap | `.txt` | `smbmap_{scan_id}.txt` | `smbmap_861.txt` |
| SSLScan | `.txt` | `sslscan_{scan_id}.txt` | `sslscan_873.txt` |
| SMBClient | `.txt` | `smbclient_{scan_id}.txt` | `smbclient_862.txt` |

**Ejemplo de contenido** (`enum4linux_860.txt`):
```
Starting enum4linux v0.9.1 on Sun Dec  7 05:20:19 2025

=========================================( Target Information )=========================================

Target ........... kopernicus.tech
RID Range ........ 500-550,1000-1050
Username ......... ''
Password ......... ''
Known Usernames .. administrator, guest, krbtgt, domain admins, root, bin, none
```

### 2.4. VULNERABILITY SCANNING (`vuln_scans/`)

| Herramienta | Formato | Nombre Archivo | Ejemplo |
|------------|---------|----------------|---------|
| Nuclei | `.jsonl` | `nuclei_{scan_id}.jsonl` | `nuclei_877.jsonl` |
| Nikto | `.json` | `nikto_{scan_id}.json` | `nikto_875.json` |
| SQLMap | Directorio + `.csv` | `sqlmap_{scan_id}/` | `sqlmap_878/results-*.csv` |
| TestSSL | `.json`, `.html` | `testssl_{scan_id}.json` | `testssl_880.json` |
| WPScan | `.json` | `wpscan_{scan_id}.json` | `wpscan_881.json` |
| WhatWeb | `.json` | `whatweb_{scan_id}.json` | `whatweb_882.json` |
| ZAP | `.json` | `zap_{scan_id}.json` | `zap_883.json` |
| XSSer | `.txt` | `xsser_{scan_id}.txt` | `xsser_884.txt` |
| XSStrike | `.txt` | `xsstrike_{scan_id}.txt` | `xsstrike_885.txt` |

**Código de generación** (`services/vulnerability/tools/nuclei_scanner.py`):
```python
workspace_output_dir = self._get_workspace_output_dir(scan.id)
output_file = str(workspace_output_dir / f'nuclei_{scan.id}.jsonl')
```

**Código de generación** (`services/vulnerability/tools/testssl_scanner.py`):
```python
workspace_output_dir = self._get_workspace_output_dir(scan.id)
output_file = str(workspace_output_dir / f'testssl_{scan.id}')

command = [
    testssl_path,
    '--jsonfile', f'{output_file}.json',
    '--htmlfile', f'{output_file}.html',
    f'{target}:{port}'
]
```

**Código de generación** (`services/vulnerability/tools/sqlmap_scanner.py`):
```python
workspace_output_dir = self._get_workspace_output_dir(scan.id)
output_dir = workspace_output_dir / f'sqlmap_{scan.id}'
output_dir.mkdir(exist_ok=True)
# SQLMap genera múltiples archivos dentro del directorio:
# - {target}/target.txt
# - {target}/log
# - {target}/session.sqlite
# - results-{timestamp}.csv
```

### 2.5. EXPLOITATION (`exploitation/`)

| Herramienta | Formato | Nombre Archivo | Ejemplo |
|------------|---------|----------------|---------|
| Metasploit | `.txt` | `metasploit_{scan_id}.txt` | `metasploit_900.txt` |
| SQLMap (exploit) | `.txt` | `sqlmap_exploit_{scan_id}.txt` | `sqlmap_exploit_901.txt` |

### 2.6. POST-EXPLOITATION (`postexploit/`)

| Herramienta | Formato | Nombre Archivo | Ejemplo |
|------------|---------|----------------|---------|
| LinPEAS | `.txt` | `linpeas_{scan_id}.txt` | `linpeas_910.txt` |
| WinPEAS | `.txt` | `winpeas_{scan_id}.txt` | `winpeas_911.txt` |
| Manual guides | `.txt` | `{tool}_{scan_id}.txt` | `payload_912.txt` |

### 2.7. ACTIVE DIRECTORY (`ad_scans/`)

| Herramienta | Formato | Nombre Archivo | Ejemplo |
|------------|---------|----------------|---------|
| CrackMapExec | `.json` | `crackmapexec_{scan_id}.json` | `crackmapexec_920.json` |
| Kerbrute | `.txt` | `kerbrute_{scan_id}.txt` | `kerbrute_921.txt` |
| GetNPUsers | `.txt` | `getnpusers_{scan_id}.txt` | `getnpusers_922.txt` |
| LDAPDomainDump | Directorio | `ldapdomaindump_{scan_id}/` | `ldapdomaindump_923/` |
| ADIDNSDump | `.txt` | `adidnsdump_{scan_id}.txt` | `adidnsdump_924.txt` |

### 2.8. CLOUD SECURITY (`cloud_scans/`)

| Herramienta | Formato | Nombre Archivo | Ejemplo |
|------------|---------|----------------|---------|
| Prowler | `.json` | `prowler_{scan_id}.json` | `prowler_930.json` |
| ScoutSuite | `.json` | `scoutsuite_{scan_id}.json` | `scoutsuite_931.json` |
| Pacu | `.json` | `pacu_{scan_id}.json` | `pacu_932.json` |
| AzureHound | `.json` | `azurehound_{scan_id}.json` | `azurehound_933.json` |
| RoadTools | `.json` | `roadtools_{scan_id}.json` | `roadtools_934.json` |

### 2.9. CONTAINER SECURITY (`container_security/`)

| Herramienta | Formato | Nombre Archivo | Ejemplo |
|------------|---------|----------------|---------|
| Trivy | `.json` | `trivy_{scan_id}.json` | `trivy_940.json` |
| Grype | `.json` | `grype_{scan_id}.json` | `grype_941.json` |
| Syft | `.json` | `syft_{scan_id}.json` | `syft_942.json` |
| KubeBench | `.json` | `kubebench_{scan_id}.json` | `kubebench_943.json` |
| KubeHunter | `.json` | `kubehunter_{scan_id}.json` | `kubehunter_944.json` |
| KubeEscape | `.json` | `kubescape_{scan_id}.json` | `kubescape_945.json` |

---

## 3. CONTENIDO DE ARCHIVOS DE EJEMPLO

### 3.1. Nmap XML (`nmap_postgresql_823.xml`)

```xml
<?xml version="1.0"?>
<?xml-stylesheet href="file:///usr/bin/../share/nmap/nmap.xsl" type="text/xsl"?>
<nmaprun scanner="nmap" args="nmap -sV -p 5432 kopernicus.tech -oX nmap_postgresql_823.xml" start="1733412345" startstr="2025-12-05 10:45 EST" version="7.95" xmloutputversion="1.06">
<scaninfo type="syn" protocol="tcp" numservices="1" services="5432"/>
<verbose level="0"/>
<debugging level="0"/>
<host starttime="1733412345" endtime="1733412351">
<status state="up" reason="echo-reply" reason_ttl="64"/>
<address addr="66.97.42.227" addrtype="ipv4"/>
<hostnames>
<hostname name="vps-1889901-x.dattaweb.com" type="PTR"/>
</hostnames>
<ports>
<port protocol="tcp" portid="5432">
<state state="filtered" reason="no-response" reason_ttl="0"/>
<service name="postgresql" method="table" conf="3"/>
</port>
</ports>
<times srtt="7890" rttvar="5000" to="100000"/>
</host>
<runstats>
<finished time="1733412351" timestr="Thu Dec  5 10:45:51 2025" summary="Nmap done: 1 IP address (1 host up) scanned in 6.53 seconds" exit="success"/>
<hosts up="1" down="0" total="1"/>
</runstats>
</nmaprun>
```

### 3.2. Enum4linux (`enum4linux_860.txt`)

```
Starting enum4linux v0.9.1 ( http://labs.portcullis.co.uk/application/enum4linux/ ) on Sun Dec  7 05:20:19 2025

 =========================================( Target Information )=========================================

Target ........... kopernicus.tech
RID Range ........ 500-550,1000-1050
Username ......... ''
Password ......... ''
Known Usernames .. administrator, guest, krbtgt, domain admins, root, bin, none

 ==========================( Enumerating Workgroup/Domain on kopernicus.tech )==========================

[E] Can't find workgroup/domain

 ==============================( Nbtstat Information for kopernicus.tech )==============================
```

### 3.3. Nuclei JSONL (`nuclei_877.jsonl`)

Formato: JSON Lines (un objeto JSON por línea)

```json
{"template-id":"cve-2024-1234","info":{"name":"SQL Injection","severity":"high"},"matched-at":"https://example.com/page?id=1","extracted-results":[],"request":"GET /page?id=1 HTTP/1.1\nHost: example.com\n","response":"HTTP/1.1 200 OK\n..."}
{"template-id":"xss-reflected","info":{"name":"Reflected XSS","severity":"medium"},"matched-at":"https://example.com/search?q=<script>","extracted-results":[],"request":"GET /search?q=<script> HTTP/1.1\nHost: example.com\n","response":"HTTP/1.1 200 OK\n..."}
```

### 3.4. SQLMap CSV (`sqlmap_878/results-12072025_0524am.csv`)

```csv
id,title,payload,where,vector,parameter,data,request,response,comment
1,"Boolean-based blind SQL injection","' AND '1'='1","WHERE clause","AND","id","GET","http://example.com/page?id=1' AND '1'='1","HTTP/1.1 200 OK...","Tested parameter: id"
```

---

## 4. CÓDIGO DE GENERACIÓN DE ARCHIVOS

### 4.1. Función Base para Obtener Directorio

**Archivo**: `utils/workspace_filesystem.py`

```python
def get_workspace_output_dir_from_scan(scan_id: int, category: str) -> Path:
    """
    Obtiene directorio de output desde un scan_id.
    
    Returns:
        Path al directorio de output, o Path('{proyecto}/tmp/{category}') como fallback
    """
    try:
        from repositories import ScanRepository
        
        scan_repo = ScanRepository()
        scan = scan_repo.find_by_id(scan_id)
        
        if not scan or not scan.workspace:
            logger.warning(f"Scan {scan_id} no tiene workspace, usando {PROJECT_TMP_DIR}/{category}")
            fallback_dir = PROJECT_TMP_DIR / category
            fallback_dir.mkdir(parents=True, exist_ok=True)
            return fallback_dir
        
        workspace = scan.workspace
        return get_workspace_output_dir(workspace.id, workspace.name, category)
        
    except Exception as e:
        logger.error(f"Error obteniendo workspace directory para scan {scan_id}: {e}")
        fallback_dir = PROJECT_TMP_DIR / category
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return fallback_dir
```

### 4.2. Ejecutor de Scans (Guarda Output)

**Archivo**: `services/scanning/executors/scan_executor.py`

```python
def execute_scan(
    self,
    scan_id: int,
    command: List[str],
    output_file: str,
    tool: str,
    workspace_id: int
) -> None:
    # ... ejecución del comando ...
    
    stdout, stderr = process.communicate()
    
    # Guardar stdout si no hay archivo de salida
    output_path = Path(output_file)
    if not output_path.exists() and stdout:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(stdout)
    
    # Esperar para herramientas que escriben directamente a archivo
    if tool in ['nmap', 'rustscan', 'masscan']:
        time.sleep(1)
```

### 4.3. Ejecutor de Reconnaissance

**Archivo**: `services/reconnaissance/executors.py`

```python
def execute_scan(
    self,
    scan_id: int,
    command: List[str],
    output_file: str,
    scan_type: str
) -> None:
    # ... ejecución ...
    
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    # Algunas herramientas (como amass con -o) escriben directamente al archivo
    if Path(output_file).exists():
        logger.info(f"Output file already exists for scan {scan_id}: {output_file}")
    elif result.stdout:
        # Guardar stdout si el archivo no existe
        output_content = result.stdout
        if '***' in output_content:
            output_content = filter_theharvester_banner(output_content)
        with open(output_file, 'w') as f:
            f.write(output_content)
        logger.info(f"Saved stdout to output file for scan {scan_id}: {output_file}")
```

### 4.4. Ejecutor de Enumeration

**Archivo**: `services/enumeration/base.py`

```python
def _execute_scan(
    self,
    scan_id: int,
    command: list,
    output_file: str,
    tool: str,
    timeout: Optional[int] = None
) -> None:
    # ... ejecución ...
    
    stdout, stderr = process.communicate()
    result = type('Result', (), {
        'returncode': process.returncode,
        'stdout': stdout,
        'stderr': stderr or ''
    })()
    
    # Guardar output (smbclient puede escribir errores en stdout)
    with open(output_file, 'w') as f:
        if result.stdout:
            f.write(result.stdout)
        if result.stderr:
            if result.stdout:
                f.write(f"\n=== STDERR ===\n")
            f.write(result.stderr)
    
    # Agregar return code al archivo
    with open(output_file, 'a') as f:
        f.write(f"\n=== RETURN CODE ===\n{result.returncode}\n")
```

---

## 5. BASE DE DATOS

### 5.1. Modelo Scan

**Archivo**: `models/scan.py`

```python
class Scan(db.Model):
    """Modelo de escaneo."""
    
    __tablename__ = 'scans'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_type = db.Column(db.String(50), nullable=False)
    target = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    options = db.Column(db.JSON)  # Opciones específicas del scan
    
    # Resultados
    progress = db.Column(db.Integer, default=0)  # 0-100
    output = db.Column(db.Text)  # Output del comando (resumen)
    error = db.Column(db.Text)   # Errores si falla
    
    # Timestamps
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    results = db.relationship('ScanResult', back_populates='scan', lazy='dynamic')
```

**Nota**: El modelo `Scan` NO guarda la ruta del archivo directamente. Solo guarda un resumen en `output` (texto).

### 5.2. Modelo ScanResult

**Archivo**: `models/scan.py`

```python
class ScanResult(db.Model):
    """Resultado individual de un escaneo."""
    
    __tablename__ = 'scan_results'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    
    # Datos del resultado
    result_type = db.Column(db.String(50), nullable=False)
    # Tipos: open_port, subdomain, vulnerability, credential, etc
    
    data = db.Column(db.JSON, nullable=False)  # Datos estructurados
    severity = db.Column(db.String(20))  # critical, high, medium, low, info
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
```

**Nota**: `ScanResult` guarda datos estructurados en JSON, NO la ruta del archivo.

### 5.3. Modelo Report

**Archivo**: `models/report.py`

```python
class Report(db.Model):
    """Modelo de reporte."""
    
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)
    format = db.Column(db.String(20), nullable=False)  # pdf, html, json, markdown
    
    # Contenido
    content = db.Column(db.Text)  # Contenido markdown/html
    file_path = db.Column(db.String(500))  # Path al archivo generado ✅
    file_size = db.Column(db.Integer)  # Tamaño en bytes
    
    # Estado
    status = db.Column(db.String(20), default='draft', nullable=False)
    
    # Timestamps
    generated_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
```

**Nota**: El modelo `Report` SÍ guarda `file_path` y `file_size` para reportes generados.

### 5.4. Resumen de Almacenamiento en BD

| Modelo | Guarda Ruta de Archivo | Guarda Contenido | Guarda Metadata |
|--------|------------------------|------------------|-----------------|
| `Scan` | ❌ No | ✅ Sí (resumen en `output`) | ✅ Sí (status, progress, options) |
| `ScanResult` | ❌ No | ✅ Sí (datos estructurados en `data` JSON) | ✅ Sí (result_type, severity) |
| `Report` | ✅ Sí (`file_path`) | ✅ Sí (`content`) | ✅ Sí (format, file_size, status) |

**Conclusión**: Los archivos de resultados de scans NO se registran en la BD con su ruta. Solo se guardan:
- Resúmenes en `Scan.output`
- Datos estructurados parseados en `ScanResult.data`
- Los reportes generados SÍ guardan `file_path`

---

## 6. HERRAMIENTAS Y OUTPUTS

### 6.1. Reconnaissance

| Herramienta | Genera | Formato | Ejemplo de Contenido |
|-------------|--------|---------|---------------------|
| **Subfinder** | `subfinder_{id}.txt` | Texto plano (un dominio por línea) | `subdomain1.example.com`<br>`subdomain2.example.com` |
| **Amass** | `amass_{id}.txt` | Texto plano (dominios) | `example.com`<br>`www.example.com` |
| **theHarvester** | `theHarvester_{id}.json` | JSON | `{"hosts": [...], "ips": [...], "emails": [...]}` |
| **DNSRecon** | `dnsrecon_{id}.json` | JSON | `{"A": [...], "MX": [...], "NS": [...]}` |
| **Shodan** | `shodan_{id}.json` | JSON | `{"matches": [...], "total": 100}` |
| **GitLeaks** | `gitleaks_{id}.json` | JSON | `[{"file": "...", "line": 10, "secret": "..."}]` |
| **TruffleHog** | `trufflehog_{id}.json` | JSON | `[{"path": "...", "reason": "...", "secret": "..."}]` |
| **Hunter.io** | `hunter_io_{id}.json` | JSON | `{"data": {"emails": [...], "domain": "..."}}` |
| **Censys** | `censys_{id}.json` | JSON | `{"results": [...], "metadata": {...}}` |

### 6.2. Port Scanning

| Herramienta | Genera | Formato | Ejemplo de Contenido |
|-------------|--------|---------|---------------------|
| **Nmap** | `nmap_{id}.xml`<br>`nmap_{id}.txt`<br>`nmap_{id}.gnmap` | XML estándar<br>Texto normal<br>Formato grepeable | XML: `<nmaprun>...</nmaprun>`<br>TXT: `Nmap scan report...`<br>GNMAP: `Host: 192.168.1.1 (up) ...` |
| **RustScan** | `rustscan_{id}.txt` | Texto plano (puertos) | `22/tcp open ssh`<br>`80/tcp open http` |
| **Masscan** | `masscan_{id}.xml` | XML | `<nmaprun>...</nmaprun>` |
| **Naabu** | `naabu_{id}.txt` | Texto plano | `192.168.1.1:22`<br>`192.168.1.1:80` |

### 6.3. Enumeration

| Herramienta | Genera | Formato | Ejemplo de Contenido |
|-------------|--------|---------|---------------------|
| **Nmap (servicios)** | `nmap_{servicio}_{id}.xml` | XML | `<nmaprun>...</nmaprun>` |
| **Enum4linux** | `enum4linux_{id}.txt` | Texto plano | `Target Information`<br>`Workgroup/Domain`<br>`User enumeration` |
| **SMBMap** | `smbmap_{id}.txt` | Texto plano | `Share permissions`<br>`Read/Write access` |
| **SSLScan** | `sslscan_{id}.txt` | Texto plano | `SSL/TLS protocols`<br>`Cipher suites`<br>`Certificate info` |

### 6.4. Vulnerability Scanning

| Herramienta | Genera | Formato | Ejemplo de Contenido |
|-------------|--------|---------|---------------------|
| **Nuclei** | `nuclei_{id}.jsonl` | JSON Lines (un JSON por línea) | `{"template-id": "cve-2024-1234", "info": {...}, "matched-at": "..."}` |
| **Nikto** | `nikto_{id}.json` | JSON | `{"hostname": "...", "port": 80, "vulnerabilities": [...]}` |
| **SQLMap** | `sqlmap_{id}/`<br>`results-*.csv` | Directorio + CSV | CSV: `id,title,payload,where,vector,parameter` |
| **TestSSL** | `testssl_{id}.json`<br>`testssl_{id}.html` | JSON + HTML | JSON: `{"ciphers": [...], "protocols": [...]}`<br>HTML: Reporte visual |
| **WPScan** | `wpscan_{id}.json` | JSON | `{"url": "...", "version": "...", "vulnerabilities": [...]}` |
| **WhatWeb** | `whatweb_{id}.json` | JSON | `[{"url": "...", "plugins": {...}, "version": "..."}]` |
| **ZAP** | `zap_{id}.json` | JSON | `{"site": [...], "alerts": [...], "spider": [...]}` |
| **XSSer** | `xsser_{id}.txt` | Texto plano | `XSS found at: ...`<br>`Payload: <script>alert(1)</script>` |
| **XSStrike** | `xsstrike_{id}.txt` | Texto plano | `XSS vulnerability detected`<br>`Payload: ...` |

### 6.5. Active Directory

| Herramienta | Genera | Formato | Ejemplo de Contenido |
|-------------|--------|---------|---------------------|
| **CrackMapExec** | `crackmapexec_{id}.json` | JSON | `{"targets": [...], "credentials": [...], "shares": [...]}` |
| **Kerbrute** | `kerbrute_{id}.txt` | Texto plano | `Valid credentials found`<br>`Username: admin` |
| **GetNPUsers** | `getnpusers_{id}.txt` | Texto plano | `AS-REP Roasting results`<br>`Hash: $krb5asrep$...` |
| **LDAPDomainDump** | `ldapdomaindump_{id}/` | Directorio (múltiples archivos) | `domain_users.json`<br>`domain_computers.json` |
| **ADIDNSDump** | `adidnsdump_{id}.txt` | Texto plano | `DNS records`<br>`A records: ...` |

### 6.6. Cloud Security

| Herramienta | Genera | Formato | Ejemplo de Contenido |
|-------------|--------|---------|---------------------|
| **Prowler** | `prowler_{id}.json` | JSON | `{"findings": [...], "summary": {...}}` |
| **ScoutSuite** | `scoutsuite_{id}.json` | JSON | `{"services": {...}, "findings": [...]}` |
| **Pacu** | `pacu_{id}.json` | JSON | `{"modules": [...], "results": [...]}` |
| **AzureHound** | `azurehound_{id}.json` | JSON | `{"nodes": [...], "edges": [...]}` |
| **RoadTools** | `roadtools_{id}.json` | JSON | `{"users": [...], "roles": [...]}` |

### 6.7. Container Security

| Herramienta | Genera | Formato | Ejemplo de Contenido |
|-------------|--------|---------|---------------------|
| **Trivy** | `trivy_{id}.json` | JSON | `{"Results": [{"Vulnerabilities": [...]}]}` |
| **Grype** | `grype_{id}.json` | JSON | `{"matches": [...], "source": {...}}` |
| **Syft** | `syft_{id}.json` | JSON | `{"artifacts": [...], "distro": {...}}` |
| **KubeBench** | `kubebench_{id}.json` | JSON | `{"controls": [...], "totals": {...}}` |
| **KubeHunter** | `kubehunter_{id}.json` | JSON | `{"vulnerabilities": [...], "services": [...]}` |
| **KubeEscape** | `kubescape_{id}.json` | JSON | `{"results": [...], "summary": {...}}` |

---

## RESUMEN EJECUTIVO

### Estructura de Almacenamiento

1. **Base**: `/workspaces/{workspace_name}/` o `{proyecto}/tmp/` (fallback)
2. **Categorías**: `recon/`, `scans/`, `enumeration/`, `vuln_scans/`, `exploitation/`, `postexploit/`, `ad_scans/`, `cloud_scans/`
3. **Nomenclatura**: `{herramienta}_{scan_id}.{ext}` o `{herramienta}_{scan_id}/` (directorios)

### Base de Datos

- **Scan**: Guarda resumen en `output` (texto), NO guarda ruta de archivo
- **ScanResult**: Guarda datos estructurados en `data` (JSON), NO guarda ruta de archivo
- **Report**: SÍ guarda `file_path` y `file_size` para reportes generados

### Formatos Principales

- **JSON**: Herramientas modernas (Nuclei, Nikto, Shodan, etc.)
- **JSONL**: Nuclei (un JSON por línea)
- **XML**: Nmap (formato estándar)
- **TXT**: Herramientas legacy (Subfinder, Enum4linux, SSLScan, etc.)
- **CSV**: SQLMap (resultados)
- **HTML**: TestSSL (reporte visual)
- **Directorios**: SQLMap, LDAPDomainDump (múltiples archivos)

### Total de Herramientas

- **Reconnaissance**: 9 herramientas
- **Port Scanning**: 4 herramientas
- **Enumeration**: 4+ herramientas
- **Vulnerability Scanning**: 9 herramientas
- **Active Directory**: 5 herramientas
- **Cloud Security**: 5 herramientas
- **Container Security**: 6 herramientas

**Total**: ~42 herramientas que generan archivos de resultados

