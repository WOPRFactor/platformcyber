# Dónde Buscar "Herramientas Utilizadas" en el PDF

**Fecha:** Enero 2025

---

## 📍 UBICACIÓN EN EL PDF

### Estructura del Reporte PDF:

```
┌─────────────────────────────────────────┐
│ PORTADA                                  │
│ - Título del Reporte                    │
│ - Workspace Name                        │
│ - Fecha                                 │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ TABLA DE METADATA ⭐ AQUÍ ESTÁ          │
│                                         │
│ Métrica              │ Valor            │
├──────────────────────┼──────────────────┤
│ Total de Hallazgos   │ 45               │
│ Archivos Procesados  │ 5                │
│ Targets Únicos       │ 3                │
│ Herramientas         │ nmap, nuclei,    │ ← AQUÍ
│ Utilizadas           │ nikto, subfinder │
│ Tiempo de Generación │ 12.34 segundos   │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ GRÁFICOS (si hay)                       │
│ - Distribución de Severidad            │
│ - Findings por Categoría               │
│ - Risk Score Gauge                     │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ HALLAZGOS CRÍTICOS Y ALTOS              │
│ - Finding 1                             │
│ - Finding 2                             │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ HALLAZGOS DETALLADOS POR CATEGORÍA      │
│ - Scanning                             │
│   • Traceroute hop 7                    │ ← LO QUE ESTÁS VIENDO
│   • Traceroute hop 8                    │
│   • Traceroute hop 9                    │
│ - Enumeration                           │
│ - Vulnerability Assessment              │
└─────────────────────────────────────────┘
```

---

## 🔍 DÓNDE BUSCAR

### En el PDF:

1. **Abre el PDF generado**
2. **Ve a la primera o segunda página** (después de la portada)
3. **Busca una tabla** con el título "Métrica" y "Valor"
4. **En esa tabla, busca la fila:** `Herramientas Utilizadas`

### Ejemplo Visual de la Tabla:

```
┌──────────────────────────────────────────────┐
│ Métrica              │ Valor                 │
├──────────────────────┼───────────────────────┤
│ Total de Hallazgos   │ 45                    │
│ Archivos Procesados  │ 5                     │
│ Targets Únicos       │ 3                     │
│ Herramientas         │ nmap, nuclei, nikto,  │ ← ESTA FILA
│ Utilizadas           │ subfinder, enum4linux │
│ Tiempo de Generación │ 12.34 segundos        │
└──────────────────────────────────────────────┘
```

---

## ⚠️ IMPORTANTE

### Si NO ves "Herramientas Utilizadas":

**Posibles razones:**

1. **El reporte fue generado ANTES de reiniciar el Celery worker**
   - **Solución:** Genera un reporte NUEVO

2. **El campo está vacío (`tools_used = []`)**
   - **Solución:** Verifica que el Celery worker tenga el código nuevo
   - **Verificación:** `tail -f /tmp/celery_dev4.log | grep "using"`

3. **El PDF no se regeneró**
   - **Solución:** Descarga el PDF nuevamente desde el frontend

---

## ✅ VERIFICACIÓN RÁPIDA

### ¿El reporte tiene `tools_used`?

**Opción 1: Desde el Frontend**
- Después de generar el reporte, deberías ver badges azules con las herramientas
- Si NO ves los badges → el reporte es antiguo o `tools_used` está vacío

**Opción 2: Desde la Base de Datos**
```bash
cd platform/backend
python3 check_tools_used.py
```

**Opción 3: Verificar el último reporte**
```bash
cd platform/backend
python3 -c "
from app import create_app
from models.report import Report
app = create_app()
with app.app_context():
    report = Report.query.order_by(Report.created_at.desc()).first()
    if report:
        print(f'Reporte ID: {report.id}')
        print(f'Tools Used: {report.tools_used}')
        print(f'Fecha: {report.created_at}')
"
```

---

## 📊 LO QUE ESTÁS VIENDO AHORA

Lo que muestras en la imagen son **hallazgos detallados** de la categoría **"Scanning"** o **"Network Services"**, específicamente resultados de **traceroute**.

Esto está en la sección:
- **"Hallazgos Detallados por Categoría"**
- **Subsección:** "Scanning" o "Network Services"
- **Tipo:** Traceroute hops

**Esto NO es donde está `tools_used`.**

`tools_used` está **ANTES** de esta sección, en la **tabla de metadata** al inicio del reporte.

---

## 🎯 RESUMEN

- **Lo que estás viendo:** Hallazgos detallados (traceroute)
- **Dónde está `tools_used`:** Tabla de metadata al inicio del PDF (página 1-2)
- **Qué buscar:** Tabla con fila "Herramientas Utilizadas"
- **Si no lo ves:** El reporte es antiguo o `tools_used` está vacío → Genera uno nuevo

