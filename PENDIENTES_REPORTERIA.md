# 📋 PENDIENTES - MÓDULO DE REPORTERÍA

**Fecha**: 2024-12-XX  
**Ambiente**: dev4-improvements  
**Estado Fase 1**: ✅ Core implementado | ⏳ Tests pendientes

---

## ✅ COMPLETADO EN FASE 1

### Estructura y Componentes Core
- [x] Estructura de directorios creada en `services/reporting/`
- [x] Archivo de configuración con límites (`config.py`)
- [x] BaseParser implementado con manejo robusto de errores
- [x] NmapParser implementado
- [x] NucleiParser implementado
- [x] SubfinderParser implementado
- [x] NiktoParser implementado
- [x] ParserManager implementado
- [x] FileScanner implementado con límites y validación de seguridad
- [x] DataAggregator implementado con deduplicación
- [x] RiskCalculator implementado
- [x] Logging configurado correctamente
- [x] Validación de tamaño de archivo implementada
- [x] Manejo robusto de errores ("fail gracefully")

---

## ⏳ PENDIENTES DE FASE 1

### Tests y Validación
- [x] **Tests unitarios para CADA componente** (≥80% coverage)
  - [x] `tests/unit/test_base_parser.py` ✅
  - [x] `tests/unit/test_nmap_parser.py` ✅
  - [x] `tests/unit/test_nuclei_parser.py` ✅
  - [x] `tests/unit/test_subfinder_parser.py` ✅
  - [x] `tests/unit/test_nikto_parser.py` ✅
  - [x] `tests/unit/test_parser_manager.py` ✅
  - [x] `tests/unit/test_file_scanner.py` ✅
  - [x] `tests/unit/test_data_aggregator.py` ✅
  - [x] `tests/unit/test_risk_calculator.py` ✅

- [x] **Fixtures de prueba** (archivos de ejemplo)
  - [x] `tests/fixtures/nmap_sample.xml` ✅
  - [x] `tests/fixtures/nuclei_sample.jsonl` ✅
  - [x] `tests/fixtures/subfinder_sample.txt` ✅
  - [x] `tests/fixtures/nikto_sample.json` ✅
  - [ ] Archivos de prueba con casos edge (corruptos, vacíos, malformados) - Parcialmente cubierto en tests

### Seguridad Adicional
- [x] **Validación de path traversal** implementada ✅
  - [x] `FileScanner._is_safe_path()` implementado
  - [x] Validación de rutas antes de escanear
  - [x] Prevención de acceso a directorios fuera del workspace
  
- [x] **Sanitización de inputs** implementada ✅
  - [x] `FileScanner._is_safe_workspace_name()` implementado
  - [x] Validación de workspace_name e workspace_id

---

## 🚀 FASE 1B: TEMPLATES HTML Y GENERACIÓN DE PDF

**Objetivo**: Generar reportes técnicos en PDF usando templates HTML

### Pendientes:
- [ ] **BaseGenerator** (`generators/base_generator.py`)
  - Clase base abstracta para todos los generadores
  - Métodos comunes para renderizado

- [ ] **PDFGenerator** (`generators/pdf_generator.py`)
  - Usar WeasyPrint para convertir HTML a PDF
  - Manejo de errores robusto
  - Soporte para CSS embebido

- [ ] **Templates HTML**
  - [ ] `templates/base.html` - Template base con estructura común
  - [ ] `templates/technical/report.html` - Template para reporte técnico
  - [ ] `templates/static/css/report.css` - Estilos para reportes

- [ ] **Integración con componentes core**
  - ReportService que orquesta: FileScanner → Parsers → Aggregator → Generator
  - Endpoint API `/api/v1/reporting/generate` (síncrono por ahora)

- [ ] **Tests de generación**
  - Test de generación de PDF con datos de prueba
  - Validación de formato y contenido

---

## 🔄 FASE 2: GENERACIÓN ASÍNCRONA Y MÁS PARSERS

**Objetivo**: Soportar workspaces grandes y agregar más herramientas

### Generación Asíncrona:
- [ ] **Tarea Celery** (`tasks/reporting_tasks.py` o nuevo archivo)
  ```python
  @shared_task(bind=True)
  def generate_report_async(self, workspace_id, report_type, format, user_id):
      # Implementación...
  ```

- [ ] **Endpoint de status**: `/api/v1/reporting/status/<task_id>`
  - Retorna estado de la tarea (pending, processing, completed, failed)
  - Retorna progreso si está disponible

- [ ] **Notificaciones**
  - Email cuando reporte está listo
  - WebSocket para updates en tiempo real

- [ ] **Cola de prioridad** para reportes urgentes
  - Configurar Celery con múltiples colas
  - Asignar prioridad según tipo de reporte

- [ ] **Procesamiento por chunks** para archivos grandes
  - Dividir archivos grandes en chunks
  - Procesar chunks en paralelo

- [ ] **Progress bar / porcentaje de completitud**
  - Actualizar progreso durante parsing
  - Retornar progreso en endpoint de status

### Parsers Adicionales (10 parsers):
- [ ] **Reconnaissance**:
  - [ ] AmassParser (JSON)
  - [ ] TheHarvesterParser (JSON/XML)
  - [ ] DNSReconParser (XML)

- [ ] **Scanning**:
  - [ ] RustScanParser (JSON)
  - [ ] MasscanParser (JSON)

- [ ] **Vulnerability**:
  - [ ] SQLMapParser (JSON)
  - [ ] TestSSLParser (TXT/JSON)
  - [ ] WPScanParser (JSON)

- [ ] **Enumeration**:
  - [ ] Enum4linuxParser (TXT)
  - [ ] SMBMapParser (JSON)

- [ ] **Tests para cada parser nuevo**

---

## 📊 FASE 3: REPORTE EJECUTIVO Y VISUALIZACIONES

**Objetivo**: Reporte para management con gráficos profesionales

### Pendientes:
- [ ] **Template HTML para executive summary**
  - `templates/executive/report.html`
  - Diseño profesional y limpio

- [ ] **Generación de gráficos con Plotly**:
  - [ ] Pie chart de severidades
  - [ ] Bar chart de findings por categoría
  - [ ] Risk score gauge
  - [ ] Timeline de escaneos

- [ ] **Cálculo de risk score mejorado**
  - Con benchmarks de industria
  - Comparación con estándares

- [ ] **Top 5 vulnerabilidades críticas**
  - Algoritmo de ranking
  - Presentación visual

- [ ] **Recomendaciones priorizadas con ROI**
  - Cálculo de impacto
  - Priorización automática

- [ ] **Comparación con industry standards** (opcional)
  - Benchmarks de OWASP, NIST, etc.

- [ ] **API endpoint para executive report**
  - `/api/v1/reporting/generate/executive`

- [ ] **Export de gráficos como PNG** (con Kaleido)
  - Instalar `kaleido` en requirements.txt
  - Generar imágenes para PDF

---

## 🔧 FASE 4: PARSERS COMPLETOS

**Objetivo**: Soportar todas las 42+ herramientas

### Pendientes:
- [ ] **Parsers restantes de reconnaissance** (5 tools)
- [ ] **Parsers restantes de scanning** (2 tools)
- [ ] **Parsers restantes de enumeration** (2 tools)
- [ ] **Parsers restantes de vulnerability** (4 tools)
- [ ] **Parsers de Active Directory** (5 tools)
- [ ] **Parsers de Cloud** (5 tools)
- [ ] **Parsers de Container** (6 tools)
- [ ] **Tests para cada parser nuevo**
- [ ] **Documentación de cada parser**

---

## 📄 FASE 5: FORMATOS ADICIONALES

**Objetivo**: DOCX y HTML standalone

### Pendientes:
- [ ] **DOCXGenerator** con python-docx
  - `generators/docx_generator.py`
  - Estilos de Word personalizables

- [ ] **HTMLGenerator standalone** (con CSS embebido)
  - `generators/html_generator.py`
  - CSS inline o embebido

- [ ] **Adaptación de templates** para cada formato
  - Templates específicos para DOCX
  - Templates específicos para HTML standalone

- [ ] **API soporta múltiples formatos**
  - Parámetro `format` en endpoint
  - Validación de formatos soportados

---

## 🗄️ FASE 6: MODELO DE DATOS Y API

**Objetivo**: Extender modelo Report y crear endpoints completos

### Modelo de Datos:
- [ ] **Extender modelo Report** (`models/report.py`)
  - [ ] Campo `version` (Integer)
  - [ ] Campo `is_latest` (Boolean)
  - [ ] Campo `file_hash` (String, SHA-256)
  - [ ] Campo `files_processed` (Integer)
  - [ ] Campo `tools_used` (JSON)
  - [ ] Campo `scan_date_range` (JSON)
  - [ ] Campo `generation_time_seconds` (Float)
  - [ ] Método `calculate_file_hash()`
  - [ ] Método `verify_integrity()`

- [ ] **Migración de base de datos**
  - Crear migración Alembic
  - Actualizar schema

### API Endpoints:
- [ ] **POST `/api/v1/reporting/generate`**
  - Request body: `{workspace_id, report_type, format, start_date?, end_date?}`
  - Response: `{report_id, task_id?, status}`

- [ ] **GET `/api/v1/reporting/download/<report_id>`**
  - Retorna archivo del reporte
  - Headers apropiados para descarga

- [ ] **GET `/api/v1/reporting/list/<workspace_id>`**
  - Lista todos los reportes de un workspace
  - Filtros opcionales (tipo, formato, fecha)

- [ ] **GET `/api/v1/reporting/<report_id>`**
  - Retorna metadata del reporte
  - Incluye estadísticas y hash

- [ ] **DELETE `/api/v1/reporting/<report_id>`**
  - Elimina reporte (soft delete o hard delete)
  - Validación de permisos

- [ ] **GET `/api/v1/reporting/status/<task_id>`** (Fase 2)
  - Estado de generación asíncrona
  - Progreso si está disponible

---

## 🎨 FASE 7: INTEGRACIÓN FRONTEND

**Objetivo**: Integrar con interfaz existente

### Pendientes:
- [ ] **Componente de generación de reportes**
  - Formulario para seleccionar tipo y formato
  - Integración con API

- [ ] **Componente de historial de reportes**
  - Lista de reportes generados
  - Filtros y búsqueda

- [ ] **Componente de descarga**
  - Botón de descarga
  - Preview si es HTML

- [ ] **Notificaciones de reportes listos** (si es asíncrono)
  - Toast notifications
  - Badge en historial

---

## 📝 DOCUMENTACIÓN PENDIENTE

- [ ] **Documentación de uso** (README)
  - Cómo usar el módulo
  - Ejemplos de código
  - Guía de troubleshooting

- [ ] **Documentación de parsers**
  - Formato esperado de cada herramienta
  - Campos extraídos
  - Ejemplos de archivos

- [ ] **Documentación de API**
  - Swagger/OpenAPI
  - Ejemplos de requests/responses

---

## 🔍 VALIDACIONES PENDIENTES

### Seguridad:
- [ ] Validación de path traversal en FileScanner
- [ ] Sanitización de nombres de archivo
- [ ] Validación de permisos de workspace
- [ ] Rate limiting en endpoints de generación

### Performance:
- [ ] Tests de performance con workspaces grandes
- [ ] Optimización de parsing para archivos grandes
- [ ] Caching de resultados parseados (opcional)

### Calidad:
- [ ] Coverage ≥80% en todos los componentes
- [ ] Tests de integración end-to-end
- [ ] Tests de carga (stress testing)

---

## 📊 RESUMEN DE ESTADO

| Fase | Componentes | Estado | Progreso |
|------|-------------|--------|----------|
| **Fase 1** | Core + 4 parsers | ✅ Completada | 100% |
| **Fase 1B** | Templates + PDF | ⏳ Pendiente | 0% |
| **Fase 2** | Async + 10 parsers | ⏳ Pendiente | 0% |
| **Fase 3** | Executive + Charts | ⏳ Pendiente | 0% |
| **Fase 4** | Todos los parsers | ⏳ Pendiente | 0% |
| **Fase 5** | DOCX + HTML | ⏳ Pendiente | 0% |
| **Fase 6** | Modelo + API | ⏳ Pendiente | 0% |
| **Fase 7** | Frontend | ⏳ Pendiente | 0% |

---

## 🎯 PRIORIDADES INMEDIATAS

1. **Tests unitarios de Fase 1** (crítico para validar implementación)
2. **Fixtures de prueba** (necesarios para tests)
3. **Validación de path traversal** (seguridad crítica)
4. **Fase 1B: Templates y PDF** (primer reporte funcional)
5. **Fase 2: Async** (necesario para workspaces grandes)

---

**Última actualización**: 2024-12-XX  
**Próxima revisión**: Después de completar tests de Fase 1

