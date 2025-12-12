# Pendientes Reales del Módulo de Reportería

**Fecha:** Enero 2025  
**Base:** Verificación directa del código en `dev4-improvements`

---

## ✅ LO QUE YA ESTÁ IMPLEMENTADO

- ✅ Modelo Report completo (con todos los campos)
- ✅ ReportRepository completo
- ✅ Guardado en BD funcionando
- ✅ Endpoint de descarga por report_id
- ✅ Frontend usando report_id
- ✅ WeasyPrint en uso
- ✅ Gráficos con Plotly (pie, bar, gauge)
- ✅ 42+ parsers implementados
- ✅ Generación asíncrona con Celery
- ✅ Templates HTML profesionales

---

## ⚠️ PENDIENTES REALES (Priorizados)

### 🔴 PRIORIDAD ALTA

#### 1. ✅ Mejorar `tools_used` - Detección de Herramientas **COMPLETADO**

**Estado:** ✅ Implementado y funcionando

**Solución implementada:**
- ✅ `ParserManager.parse_file_with_parser()` retorna `(findings, parser_name)`
- ✅ `ParserManager._get_tool_name_from_parser()` extrae nombre del parser
- ✅ `ParserManager._extract_tool_from_filename()` fallback desde file_path
- ✅ `tasks/reporting_tasks.py` calcula `tools_used` ANTES de generar PDF
- ✅ `tools_used` se agrega a `metadata` para que aparezca en el PDF
- ✅ Frontend muestra `tools_used` como badges visuales
- ✅ Bug corregido: `tools_used` ahora aparece en el PDF (antes mostraba "N/A")

**Archivos modificados:**
- ✅ `parsers/parser_manager.py` - Método `parse_file_with_parser()` y helpers
- ✅ `tasks/reporting_tasks.py` - Cálculo de `tools_used` antes del PDF
- ✅ `frontend/src/pages/Reporting/components/ReportGeneratorV2.tsx` - Visualización

**Resultado:** `tools_used` funciona correctamente en BD, PDF y Frontend.

---

### 🟡 PRIORIDAD MEDIA

#### 2. Mejorar Diseño Visual del PDF

**Estado actual:**
- ✅ Template HTML profesional existe (`report_weasy.html`)
- ✅ CSS con colores por severidad
- ⚠️ Sin logo corporativo
- ⚠️ Sin portada dedicada profesional
- ⚠️ Colores básicos (sin branding)

**Mejoras propuestas:**
1. **Portada profesional:**
   - Logo de la empresa/cliente
   - Información del proyecto
   - Fecha y versión del reporte
   - Diseño visual atractivo

2. **Branding:**
   - Colores corporativos configurables
   - Logo en header/footer de cada página
   - Tipografía profesional

3. **Mejoras visuales:**
   - Mejor espaciado y tipografía
   - Íconos para diferentes tipos de findings
   - Tablas más profesionales
   - Mejor organización visual

**Archivos a modificar:**
- `templates/technical/report_weasy.html` - Agregar portada y branding
- `generators/pdf_generator_weasy.py` - Soporte para logo y colores configurables
- `config.py` o nuevo `branding_config.py` - Configuración de colores/logo

**Estimación:** 4-6 horas

---

#### 3. Reporte Ejecutivo Dedicado

**Estado actual:**
- ✅ Existe `report_type='executive'` en el modelo
- ⚠️ Usa el mismo template técnico
- ⚠️ No hay template específico para ejecutivos

**Mejoras propuestas:**
1. **Template ejecutivo nuevo:**
   - `templates/executive/report_weasy.html`
   - Enfoque en métricas y gráficos
   - Menos detalles técnicos
   - Top 5 vulnerabilidades críticas
   - Recomendaciones priorizadas

2. **Contenido ejecutivo:**
   - Resumen visual con gráficos grandes
   - Risk score prominente
   - Comparación con benchmarks (opcional)
   - ROI de remediación
   - Timeline de remediación sugerida

3. **Generador específico:**
   - `generators/executive_generator.py` o método en `pdf_generator_weasy.py`
   - Lógica diferente para seleccionar findings (solo críticos/altos)
   - Formato más visual y menos técnico

**Archivos a crear/modificar:**
- `templates/executive/report_weasy.html` - Nuevo template
- `generators/pdf_generator_weasy.py` - Método `generate_executive_report()`
- `report_service_v2.py` - Lógica para seleccionar contenido ejecutivo

**Estimación:** 6-8 horas

---

### 🟢 PRIORIDAD BAJA

#### 4. Más Parsers (Opcional)

**Estado actual:**
- ✅ 42+ parsers implementados
- ⚠️ Pueden faltar algunos según lista completa de herramientas

**Acción:**
- Revisar lista completa de herramientas del proyecto
- Identificar parsers faltantes
- Implementar según necesidad

**Estimación:** Variable (1-2 horas por parser)

---

#### 5. Formatos Adicionales

**Estado actual:**
- ✅ PDF con WeasyPrint
- ⚠️ DOCX mencionado pero no implementado
- ⚠️ HTML standalone mencionado pero no implementado

**Mejoras propuestas:**
1. **DOCX Generator:**
   - Usar `python-docx`
   - Template Word profesional
   - Mantener mismo contenido que PDF

2. **HTML Standalone:**
   - HTML con CSS embebido
   - Navegación interactiva
   - Filtros y búsqueda

**Archivos a crear:**
- `generators/docx_generator.py`
- `generators/html_generator.py`
- Templates correspondientes

**Estimación:** 8-10 horas por formato

---

#### 6. Componente Frontend de Historial

**Estado actual:**
- ✅ Backend tiene endpoints para listar reportes
- ⚠️ Frontend no tiene componente de historial completo

**Mejoras propuestas:**
1. **Componente ReportsHistory:**
   - Lista de reportes generados
   - Filtros por tipo, fecha, workspace
   - Descarga de reportes antiguos
   - Comparación de reportes
   - Eliminación de reportes

2. **Integración:**
   - Agregar a página de Reporting
   - Notificaciones cuando reporte está listo
   - Preview de reportes

**Archivos a crear/modificar:**
- `frontend/src/pages/Reporting/components/ReportsHistory.tsx`
- `frontend/src/pages/Reporting/components/ReportCard.tsx`
- Integración con API existente

**Estimación:** 6-8 horas

---

## 📊 RESUMEN DE PRIORIDADES

| # | Tarea | Prioridad | Estimación | Impacto | Estado |
|---|-------|-----------|------------|---------|--------|
| 1 | Mejorar `tools_used` | 🔴 Alta | 2-3h | Alto - Datos correctos en BD | ✅ **COMPLETADO** |
| 2 | Diseño visual PDF | 🟡 Media | 4-6h | Medio - Mejor presentación | ⏳ Pendiente |
| 3 | Reporte ejecutivo | 🟡 Media | 6-8h | Medio - Nuevo tipo de reporte | ⏳ Pendiente |
| 4 | Más parsers | 🟢 Baja | Variable | Bajo - Ya hay 42+ | ⏳ Pendiente |
| 5 | Formatos adicionales | 🟢 Baja | 16-20h | Bajo - Nice to have | ⏳ Pendiente |
| 6 | Frontend historial | 🟢 Baja | 6-8h | Bajo - Backend ya funciona | ⏳ Pendiente |

---

## 🎯 RECOMENDACIÓN: Continuar con #2 o #3

**Opción A: Mejorar Diseño Visual del PDF (#2)**
- **Razón:** Impacto visual inmediato, mejora la presentación profesional
- **Tiempo:** 4-6 horas
- **Incluye:** Logo, portada profesional, branding, mejor tipografía

**Opción B: Reporte Ejecutivo (#3)**
- **Razón:** Nuevo tipo de reporte con enfoque ejecutivo
- **Tiempo:** 6-8 horas
- **Incluye:** Template ejecutivo, métricas visuales, menos detalles técnicos

**Opción C: Componente Frontend de Historial (#6)**
- **Razón:** Backend ya funciona, solo falta UI
- **Tiempo:** 6-8 horas
- **Incluye:** Lista de reportes, filtros, re-descarga, comparación

---

**Última actualización:** Enero 2025  
**Estado:** Tarea #1 completada ✅

