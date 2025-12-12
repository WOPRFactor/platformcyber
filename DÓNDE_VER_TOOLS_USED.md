# Dónde Verás `tools_used` - Guía Visual

**Fecha:** Enero 2025

---

## 📍 DÓNDE VERÁS LA DIFERENCIA

### 1. ✅ EN EL FRONTEND (Página de Reporting)

**Ubicación:** Componente `ReportGeneratorV2` en la página de Reporting

**Cuándo aparece:**
- Cuando generas un reporte
- Cuando el reporte termina de generarse (`status === 'completed'`)

**Qué verás:**

```
┌─────────────────────────────────────────────┐
│ ✅ Reporte generado exitosamente          │
├─────────────────────────────────────────────┤
│                                             │
│  Hallazgos  │  Archivos  │  Risk Score     │
│     45      │     5      │     7.2         │
│                                             │
├─────────────────────────────────────────────┤
│ 🔧 Herramientas Usadas                      │
│                                             │
│  [enum4linux]  [nmap]  [nuclei]            │
│  [nikto]  [subfinder]                       │
│                                             │
└─────────────────────────────────────────────┘
```

**Badges azules** con cada herramienta detectada.

---

### 2. ✅ EN EL REPORTE PDF

**Ubicación:** Sección de "Metadata del Reporte" en el PDF

**Dónde está:**
- En la tabla de información general del reporte
- Fila: "Herramientas Utilizadas"

**Qué verás:**

```
┌─────────────────────────────────────────┐
│ Metadata del Reporte                    │
├─────────────────────────────────────────┤
│ Total de Hallazgos:        45           │
│ Archivos Procesados:       5            │
│ Risk Score:                7.2         │
│ Herramientas Utilizadas:   nmap, nuclei,│
│                            nikto,       │
│                            subfinder,   │
│                            enum4linux   │
└─────────────────────────────────────────┘
```

**Antes:** `Herramientas Utilizadas: N/A`  
**Después:** `Herramientas Utilizadas: nmap, nuclei, nikto, subfinder, enum4linux`

---

### 3. ✅ EN LA BASE DE DATOS

**Campo:** `tools_used` (tipo JSON)

**Cómo verlo:**

**Opción A: Script Python**
```bash
cd platform/backend
python3 check_tools_used.py
```

**Opción B: Consulta SQL**
```sql
SELECT tools_used FROM reports ORDER BY created_at DESC LIMIT 1;
```

**Resultado:**
```json
["enum4linux", "nmap", "nuclei", "nikto", "subfinder"]
```

---

### 4. ✅ EN LOS LOGS DEL CELERY

**Ubicación:** Logs del worker Celery

**Qué buscar:**
```bash
tail -f logs/celery.log | grep "using"
```

**Verás:**
```
Parsed 15 findings from nmap_scan.xml using nmap
Parsed 8 findings from nuclei_results.jsonl using nuclei
Parsed 3 findings from nikto_output.json using nikto
```

**Antes:** Solo `Parsed X findings from archivo.xml`  
**Después:** `Parsed X findings from archivo.xml using nmap`

---

## 📊 RESUMEN: Dónde Verás la Diferencia

| Lugar | Qué Verás | Cuándo |
|-------|-----------|--------|
| **Frontend** | Badges azules con herramientas | Cuando el reporte termine |
| **PDF** | Fila "Herramientas Utilizadas" con lista | Al abrir el PDF generado |
| **Base de Datos** | Campo `tools_used` con array JSON | Consultando la BD |
| **Logs Celery** | "using nmap", "using nuclei", etc. | Durante la generación |

---

## 🎯 Lo Más Visible

**El cambio más visible será:**

1. **En el Frontend:** Los badges azules con las herramientas (inmediatamente después de generar)
2. **En el PDF:** La fila "Herramientas Utilizadas" con la lista completa

---

## ⚠️ IMPORTANTE

- Solo los reportes generados **DESPUÉS** de reiniciar el Celery worker tendrán `tools_used` correcto
- Los reportes antiguos seguirán con `tools_used = []` o `NULL`

---

**Para verlo:** Genera un reporte nuevo y verás las herramientas en el frontend y en el PDF.

