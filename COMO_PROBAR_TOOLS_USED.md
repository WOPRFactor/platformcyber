# Cómo Probar `tools_used`

**Fecha:** Enero 2025  
**Ambiente:** dev4-improvements

---

## 🧪 Método 1: Generar Reporte y Verificar en BD

### Paso 1: Generar un Reporte

**Opción A: Desde el Frontend**
1. Ir a la página de Reporting
2. Seleccionar un workspace que tenga archivos de diferentes herramientas (nmap, nuclei, nikto, etc.)
3. Generar un reporte técnico
4. Esperar a que termine la generación

**Opción B: Desde la API (curl)**
```bash
# Obtener token de autenticación primero
TOKEN="tu_token_aqui"

# Generar reporte
curl -X POST http://localhost:5001/api/v1/reporting/generate-v2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": 1,
    "report_type": "technical",
    "format": "pdf"
  }'
```

**Opción C: Desde Python**
```python
import requests

token = "tu_token"
headers = {"Authorization": f"Bearer {token}"}
data = {
    "workspace_id": 1,
    "report_type": "technical",
    "format": "pdf"
}

response = requests.post(
    "http://localhost:5001/api/v1/reporting/generate-v2",
    json=data,
    headers=headers
)
print(response.json())
```

---

### Paso 2: Verificar `tools_used` en la Base de Datos

**Opción A: Consulta SQL Directa**
```sql
-- Ver últimos reportes generados
SELECT 
    id,
    title,
    tools_used,
    files_processed,
    total_findings,
    created_at
FROM reports
ORDER BY created_at DESC
LIMIT 5;
```

**Opción B: Desde Python (Flask Shell)**
```bash
cd /home/kali/Proyectos/cybersecurity/environments/dev4-improvements/platform/backend
source venv/bin/activate  # o el venv que uses
flask shell
```

```python
from models.report import Report

# Ver último reporte
last_report = Report.query.order_by(Report.created_at.desc()).first()
print(f"ID: {last_report.id}")
print(f"Título: {last_report.title}")
print(f"Tools Used: {last_report.tools_used}")
print(f"Files Processed: {last_report.files_processed}")
print(f"Total Findings: {last_report.total_findings}")

# Ver todos los reportes recientes
reports = Report.query.order_by(Report.created_at.desc()).limit(5).all()
for r in reports:
    print(f"\nReporte {r.id}:")
    print(f"  Tools: {r.tools_used}")
    print(f"  Files: {r.files_processed}")
```

**Opción C: Script Python Independiente**
```python
#!/usr/bin/env python3
"""Script para verificar tools_used en reportes"""

from app import create_app
from models.report import Report

app = create_app()

with app.app_context():
    # Último reporte
    last = Report.query.order_by(Report.created_at.desc()).first()
    
    if last:
        print("=" * 60)
        print("ÚLTIMO REPORTE GENERADO")
        print("=" * 60)
        print(f"ID: {last.id}")
        print(f"Título: {last.title}")
        print(f"Workspace ID: {last.workspace_id}")
        print(f"Tipo: {last.report_type}")
        print(f"Formato: {last.format}")
        print(f"\n📊 METADATA:")
        print(f"  Files Processed: {last.files_processed}")
        print(f"  Total Findings: {last.total_findings}")
        print(f"  Risk Score: {last.risk_score}")
        print(f"\n🔧 TOOLS USED:")
        if last.tools_used:
            print(f"  ✅ {len(last.tools_used)} herramientas detectadas:")
            for tool in last.tools_used:
                print(f"     - {tool}")
        else:
            print(f"  ⚠️  Ninguna herramienta detectada (vacío)")
        print(f"\n📅 Generado: {last.created_at}")
        print("=" * 60)
    else:
        print("No hay reportes en la base de datos")
    
    # Estadísticas
    print("\n📈 ESTADÍSTICAS:")
    total_reports = Report.query.count()
    reports_with_tools = Report.query.filter(Report.tools_used.isnot(None)).filter(Report.tools_used != []).count()
    print(f"  Total reportes: {total_reports}")
    print(f"  Con tools_used: {reports_with_tools}")
    print(f"  Sin tools_used: {total_reports - reports_with_tools}")
```

Guardar como `check_tools_used.py` y ejecutar:
```bash
cd /home/kali/Proyectos/cybersecurity/environments/dev4-improvements/platform/backend
python3 check_tools_used.py
```

---

## 🧪 Método 2: Verificar Durante la Generación (Logs)

### Ver Logs en Tiempo Real

```bash
# Ver logs del Celery worker
tail -f logs/celery.log | grep -E "tools|parser|Parsed"

# O ver logs de la aplicación
tail -f logs/app.log | grep -E "tools|parser|Parsed"
```

**Qué buscar en los logs:**
```
Parsed 15 findings from nmap_scan.xml using nmap
Parsed 8 findings from nuclei_results.jsonl using nuclei
Parsed 3 findings from nikto_output.json using nikto
...
Report saved to database with ID: 123
```

---

## 🧪 Método 3: Test Unitario Rápido

Crear archivo `test_tools_detection.py`:

```python
#!/usr/bin/env python3
"""Test rápido de detección de herramientas"""

from pathlib import Path
from services.reporting.parsers.parser_manager import ParserManager

pm = ParserManager()

# Test con nombres de archivos conocidos
test_files = [
    ("nmap_scan.xml", "nmap"),
    ("nuclei_results.jsonl", "nuclei"),
    ("nikto_output.json", "nikto"),
    ("subfinder_domains.txt", "subfinder"),
    ("enum4linux_output.txt", "enum4linux"),
]

print("🧪 TEST DE DETECCIÓN DE HERRAMIENTAS\n")
print("=" * 60)

for filename, expected_tool in test_files:
    file_path = Path(f"/tmp/{filename}")
    file_path.touch()  # Crear archivo vacío para test
    
    findings, parser_name = pm.parse_file_with_parser(file_path)
    
    status = "✅" if parser_name == expected_tool else "❌"
    print(f"{status} {filename:30} → {parser_name or 'None':20} (esperado: {expected_tool})")

print("=" * 60)
```

Ejecutar:
```bash
cd /home/kali/Proyectos/cybersecurity/environments/dev4-improvements/platform/backend
python3 test_tools_detection.py
```

---

## 🧪 Método 4: Verificar con Workspace Real

### Requisitos Previos

1. **Workspace con archivos de diferentes herramientas:**
   - `nmap_scan.xml` (Nmap)
   - `nuclei_results.jsonl` (Nuclei)
   - `nikto_output.json` (Nikto)
   - `subfinder_domains.txt` (Subfinder)
   - `enum4linux_output.txt` (Enum4linux)
   - etc.

2. **Backend y Celery corriendo:**
   ```bash
   # Backend
   cd platform/backend
   python app.py
   
   # Celery worker (otra terminal)
   celery -A celery_app worker --loglevel=info --hostname=celery_dev4@%h
   ```

### Pasos

1. **Generar reporte** (desde frontend o API)
2. **Esperar a que termine** (ver progreso en frontend o logs)
3. **Verificar en BD** usando uno de los métodos anteriores

---

## ✅ Resultado Esperado

### Si funciona correctamente:

```json
{
  "id": 123,
  "title": "Reporte Technical - Mi Workspace",
  "tools_used": ["enum4linux", "nmap", "nuclei", "nikto", "subfinder"],
  "files_processed": 5,
  "total_findings": 45
}
```

### Si NO funciona:

```json
{
  "id": 123,
  "title": "Reporte Technical - Mi Workspace",
  "tools_used": [],  // ⚠️ Vacío
  "files_processed": 5,
  "total_findings": 45
}
```

---

## 🔍 Troubleshooting

### Si `tools_used` está vacío:

1. **Verificar logs del Celery:**
   ```bash
   tail -f logs/celery.log | grep "tools\|parser"
   ```

2. **Verificar que los archivos existen:**
   ```bash
   # Ver archivos en el workspace
   ls -la workspaces/[nombre_workspace]/
   ```

3. **Verificar que hay parsers registrados:**
   ```python
   from services.reporting.parsers.parser_manager import ParserManager
   pm = ParserManager()
   print(f"Parsers registrados: {len(pm.parsers)}")
   ```

4. **Verificar logs durante parsing:**
   Buscar líneas como:
   ```
   Parsed X findings from archivo.xml using nmap
   ```

---

## 📝 Checklist de Prueba

- [ ] Workspace tiene archivos de múltiples herramientas
- [ ] Backend está corriendo
- [ ] Celery worker está corriendo
- [ ] Reporte se genera exitosamente
- [ ] `tools_used` en BD contiene las herramientas correctas
- [ ] Logs muestran detección de herramientas durante parsing

---

**Última actualización:** Enero 2025

