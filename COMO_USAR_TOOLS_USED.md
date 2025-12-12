# Cómo Usar la Mejora de `tools_used` - Guía Rápida

**Fecha:** Enero 2025  
**Estado:** ✅ Implementado y listo para usar

---

## ✅ Lo Que Ya Está Implementado

1. ✅ **Backend:** `ParserManager` detecta herramientas automáticamente
2. ✅ **Backend:** `reporting_tasks.py` guarda `tools_used` en BD
3. ✅ **Frontend:** Muestra `tools_used` visualmente cuando el reporte está completo

---

## 🚀 Pasos para Usarlo

### Paso 1: Reiniciar Celery Worker

**IMPORTANTE:** El Celery worker necesita reiniciarse para cargar el nuevo código.

```bash
# Detener el worker actual (si está corriendo)
pkill -f "celery.*dev4"

# O si usas supervisor:
sudo supervisorctl stop celery-dev4

# Iniciar el worker con el nuevo código
cd /home/kali/Proyectos/cybersecurity/environments/dev4-improvements/platform/backend
source venv/bin/activate  # o el venv que uses
celery -A celery_app worker --loglevel=info --hostname=celery_dev4@%h
```

**O si usas el script de inicio:**
```bash
cd /home/kali/Proyectos/cybersecurity/environments/dev4-improvements
./start-dev.sh  # Esto reinicia todo
```

---

### Paso 2: Generar un Reporte Nuevo

**Desde el Frontend:**
1. Ir a la página de Reporting
2. Seleccionar un workspace con archivos (nmap, nuclei, nikto, etc.)
3. Generar reporte técnico
4. Esperar a que termine

**Desde la API:**
```bash
curl -X POST http://localhost:5001/api/v1/reporting/generate-v2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": 1,
    "report_type": "technical",
    "format": "pdf"
  }'
```

---

### Paso 3: Verificar `tools_used`

**Opción A: En el Frontend**
- Cuando el reporte termine, verás la sección "Herramientas Usadas" con badges

**Opción B: En la Base de Datos**
```bash
cd platform/backend
python3 check_tools_used.py
```

**Opción C: Consulta SQL**
```sql
SELECT id, title, tools_used FROM reports ORDER BY created_at DESC LIMIT 1;
```

---

## ⚠️ IMPORTANTE

### Reportes Antiguos NO Tendrán `tools_used`

- Solo los reportes generados **DESPUÉS** de reiniciar el Celery worker tendrán `tools_used` correcto
- Los reportes antiguos seguirán con `tools_used = []`

### Para Verificar que Funciona

1. **Generar un reporte nuevo** (después de reiniciar Celery)
2. **Verificar en BD:**
   ```bash
   python3 check_tools_used.py
   ```
3. **Deberías ver:**
   ```
   🔧 TOOLS USED:
     ✅ 5 herramienta(s) detectada(s):
        • enum4linux
        • nmap
        • nuclei
        • nikto
        • subfinder
   ```

---

## 🔍 Verificar que el Código Está Cargado

**En los logs del Celery, deberías ver:**
```
Parsed 15 findings from nmap_scan.xml using nmap
Parsed 8 findings from nuclei_results.jsonl using nuclei
```

**Si ves "using" en los logs → El código nuevo está funcionando ✅**

---

## 📝 Resumen

| Paso | Acción | Estado |
|------|--------|--------|
| 1 | Reiniciar Celery worker | ⚠️ **NECESARIO** |
| 2 | Generar reporte nuevo | ✅ Listo |
| 3 | Verificar `tools_used` | ✅ Funciona |

---

**¿Listo para usar?** Solo necesitas reiniciar el Celery worker y generar un reporte nuevo.

