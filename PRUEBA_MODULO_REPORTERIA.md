# 🧪 PRUEBA DEL MÓDULO DE REPORTERÍA

**Fecha**: 2024-12-XX  
**Ambiente**: dev4-improvements  
**Estado**: Listo para probar

---

## ✅ VERIFICACIONES PREVIAS

### 1. Verificar que el servidor esté corriendo
```bash
cd /home/kali/Proyectos/cybersecurity/environments/dev4-improvements/platform/backend
# Verificar que Flask esté corriendo en puerto 5001
curl http://localhost:5001/api/v1/system/health
```

### 2. Verificar que Celery esté corriendo (para generación asíncrona)
```bash
# Verificar workers de Celery
celery -A celery_app inspect active
```

### 3. Verificar que Redis esté corriendo
```bash
redis-cli ping
# Debe responder: PONG
```

---

## 🧪 PRUEBAS DISPONIBLES

### **Prueba 1: Generación Síncrona (Directa)**

**Endpoint**: `POST /api/v1/reporting/generate-v2`

**Request**:
```bash
curl -X POST http://localhost:5001/api/v1/reporting/generate-v2 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_JWT" \
  -d '{
    "workspace_id": 1,
    "report_type": "technical",
    "format": "pdf"
  }'
```

**Respuesta esperada**:
```json
{
  "task_id": "abc-123-def",
  "status": "pending",
  "message": "Report generation started",
  "workspace_id": 1,
  "report_type": "technical",
  "format": "pdf"
}
```

---

### **Prueba 2: Verificar Estado de Tarea**

**Endpoint**: `GET /api/v1/reporting/status/<task_id>`

**Request**:
```bash
curl -X GET http://localhost:5001/api/v1/reporting/status/abc-123-def \
  -H "Authorization: Bearer TU_TOKEN_JWT"
```

**Respuestas posibles**:

**Estado PENDING**:
```json
{
  "task_id": "abc-123-def",
  "status": "pending",
  "progress": 0,
  "message": "Task is waiting to be processed"
}
```

**Estado PROGRESS**:
```json
{
  "task_id": "abc-123-def",
  "status": "processing",
  "progress": 50,
  "message": "Parseando archivos... (25/50)",
  "step": "parsing",
  "files_parsed": 25,
  "files_total": 50
}
```

**Estado SUCCESS**:
```json
{
  "task_id": "abc-123-def",
  "status": "completed",
  "progress": 100,
  "result": {
    "workspace_id": 1,
    "report_path": "/workspaces/workspace_name/reports/report_technical_20241201_120000.pdf",
    "file_size": 123456,
    "statistics": {...},
    "risk_metrics": {...},
    "metadata": {...}
  },
  "message": "Report generated successfully"
}
```

---

### **Prueba 3: Verificar que el PDF se generó**

**Verificar archivo**:
```bash
# El reporte debería estar en:
/workspaces/{workspace_name}/reports/report_technical_*.pdf

# Verificar que existe:
ls -lh /workspaces/*/reports/*.pdf
```

---

## 📋 CHECKLIST DE PRUEBA

- [ ] Servidor Flask corriendo en puerto 5001
- [ ] Celery worker corriendo
- [ ] Redis corriendo
- [ ] Workspace existe y tiene archivos de resultados
- [ ] Token JWT válido obtenido
- [ ] Endpoint `/generate-v2` responde correctamente
- [ ] Tarea Celery se crea y se puede monitorear
- [ ] Endpoint `/status/<task_id>` muestra progreso
- [ ] PDF se genera correctamente
- [ ] PDF tiene contenido válido (no está vacío)

---

## 🔍 LOGS A REVISAR

### Backend Flask:
```bash
tail -f environments/dev4-improvements/platform/backend/logs/app.log
```

### Celery Worker:
```bash
tail -f environments/dev4-improvements/platform/backend/celery_worker.log
```

### Buscar logs específicos:
```bash
grep "Report V2" environments/dev4-improvements/platform/backend/logs/app.log
grep "generate_report_v2_task" environments/dev4-improvements/platform/backend/celery_worker.log
```

---

## ⚠️ PROBLEMAS COMUNES

### 1. "No files found in workspace"
**Solución**: Verificar que el workspace tenga archivos en las categorías:
- `/workspaces/{workspace_name}/recon/`
- `/workspaces/{workspace_name}/scans/`
- `/workspaces/{workspace_name}/vuln_scans/`
- etc.

### 2. "No findings parsed from files"
**Solución**: Verificar que los archivos sean de herramientas soportadas:
- Nmap (XML)
- Nuclei (JSONL)
- Subfinder (TXT)
- Nikto (JSON)
- Amass (JSON)

### 3. "Template not found"
**Solución**: Verificar que los templates existan:
- `services/reporting/templates/base.html`
- `services/reporting/templates/technical/report.html`
- `services/reporting/templates/static/css/report.css`

### 4. Error de WeasyPrint
**Solución**: Verificar que WeasyPrint esté instalado:
```bash
pip install weasyprint
```

---

## 📊 RESULTADO ESPERADO

Al finalizar exitosamente, deberías tener:

1. ✅ Tarea Celery completada con estado SUCCESS
2. ✅ Archivo PDF generado en `/workspaces/{workspace_name}/reports/`
3. ✅ PDF con contenido válido (más de 0 bytes)
4. ✅ Logs indicando éxito en cada paso:
   - Escaneo de archivos
   - Parsing de archivos
   - Consolidación
   - Generación de PDF

---

## 🚀 SIGUIENTE PASO

Una vez probado exitosamente, continuar con:
- Implementación de más parsers (Fase 2)
- Reporte ejecutivo con gráficos (Fase 3)
- Más formatos (DOCX, HTML standalone) (Fase 5)





