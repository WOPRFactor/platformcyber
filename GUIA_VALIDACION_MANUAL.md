# 🧪 GUÍA DE VALIDACIÓN MANUAL - REPORTERÍA V2

**Fecha**: 10 de diciembre de 2025  
**Estado**: ✅ Tests unitarios OK (38/38) - Listo para validación manual

---

## ✅ SERVICIOS ACTIVOS

### Backend (DEV4)
- **Puerto**: 5001 ✅
- **URL**: http://localhost:5001
- **Estado**: Running

### Celery Worker
- **Workers**: 3 procesos ✅
- **Estado**: celery@kali ready
- **Task registrada**: `tasks.reporting.generate_report_v2` ✅

### Redis
- **Estado**: PONG ✅

---

## 🎯 PLAN DE VALIDACIÓN

### FASE 1: Verificar Frontend

1. **Acceder a la página de reportería V2**
   ```
   http://localhost:3000/reporting-v2
   ```

2. **Verificar que la página cargue correctamente**
   - [ ] Página carga sin errores
   - [ ] Selector de workspace visible
   - [ ] Botones de generación visibles

---

### FASE 2: Generar Reporte Técnico

#### Paso 1: Seleccionar Workspace
- Elegir un workspace que tenga datos de escaneos/vulnerabilidades
- Si no tenés datos, usá cualquier workspace (el reporte se generará vacío pero funcional)

#### Paso 2: Generar Reporte
1. Clic en **"Generate Technical Report"**
2. **Observar progreso en tiempo real**:
   - [ ] Progress bar aparece
   - [ ] Mensajes de progreso se actualizan:
     - "Scanning files..." (0-20%)
     - "Parsing data..." (20-40%)
     - "Aggregating findings..." (40-60%)
     - "Calculating risk..." (60-80%)
     - "Generating PDF..." (80-100%)
   - [ ] Estado cambia a "Completed"

3. **Tiempo esperado**: 30-60 segundos

#### Paso 3: Verificar Resultado
- [ ] Mensaje de éxito aparece
- [ ] Botón de descarga aparece
- [ ] No hay errores en la consola del navegador

---

### FASE 3: Verificar Guardado en Base de Datos

Desde una terminal:

```bash
cd /home/kali/Proyectos/cybersecurity/environments/dev4-improvements/platform/backend

# Consultar reportes en BD
sqlite3 instance/pentest_platform.db << EOF
SELECT 
    id, 
    title, 
    report_type, 
    format,
    risk_score, 
    total_findings, 
    critical_count,
    high_count,
    status,
    datetime(generated_at) as generated_at
FROM reports 
ORDER BY created_at DESC 
LIMIT 5;
EOF
```

**Verificar**:
- [ ] El reporte aparece en la BD
- [ ] `status = 'completed'`
- [ ] `risk_score` tiene un valor
- [ ] `total_findings` > 0 (si hay datos)
- [ ] Contadores de severidad correctos

---

### FASE 4: Descargar y Verificar PDF

#### Paso 1: Descargar PDF
- Clic en el botón de descarga
- El archivo se descarga como `reporte_tecnico_[workspace]_[fecha].pdf`

#### Paso 2: Abrir PDF
Verificar la estructura del documento:

##### ✅ PÁGINA 1: PORTADA
- [ ] Título: "Reporte Técnico de Seguridad"
- [ ] Subtítulo: "Evaluación de Vulnerabilidades"
- [ ] Nombre del workspace
- [ ] Fecha y hora de generación
- [ ] Diseño profesional

##### ✅ PÁGINA 2: RESUMEN EJECUTIVO
- [ ] **Risk Score Box** con color (rojo/amarillo/verde)
- [ ] **Grid de Estadísticas**:
  - Total de hallazgos
  - Archivos procesados
  - Herramientas utilizadas
- [ ] **Tabla de Severidades**:
  - Critical (con emoji 🔴)
  - High (con emoji 🟠)
  - Medium (con emoji 🟡)
  - Low (con emoji 🔵)
  - Info (con emoji ⚪)

##### ✅ PÁGINA 3: VISUALIZACIONES (NUEVO - FASE 3)
- [ ] **Risk Gauge** (indicador tipo velocímetro):
  - Aguja apuntando al risk score
  - Colores: Verde (0-4), Amarillo (4-7), Rojo (7-10)
  - Bien centrado en la página
  - Tamaño: ~500px ancho

- [ ] **Severity Pie Chart** (torta de severidades):
  - Colores correctos:
    - Critical: Rojo (#e74c3c)
    - High: Naranja (#e67e22)
    - Medium: Amarillo (#f39c12)
    - Low: Azul (#3498db)
    - Info: Gris (#95a5a6)
  - Leyenda visible
  - Proporciones correctas

- [ ] **Category Bar Chart** (barras por categoría):
  - Ordenado de mayor a menor
  - Etiquetas legibles
  - Colores consistentes

- [ ] **Calidad de las imágenes**:
  - Nítidas (no pixeladas)
  - Bien integradas en el PDF
  - No cortadas ni superpuestas

##### ✅ PÁGINA 4+: HALLAZGOS CRÍTICOS Y HIGH
- [ ] Sección "Hallazgos Críticos y de Alta Severidad"
- [ ] Cada hallazgo muestra:
  - [ ] Título descriptivo
  - [ ] **Severity badge** con color
  - [ ] Categoría
  - [ ] Descripción
  - [ ] Affected Items
  - [ ] Recommendations

##### ✅ PÁGINAS SIGUIENTES: HALLAZGOS POR CATEGORÍA
- [ ] Hallazgos agrupados por categoría
- [ ] Ordenados por severidad (Critical → Info)
- [ ] Formato consistente
- [ ] Legible y profesional

##### ✅ ÚLTIMA PÁGINA: CONCLUSIÓN
- [ ] Resumen de métricas clave
- [ ] Mensaje de cierre profesional

---

### FASE 5: Verificar Archivos de Gráficos (Opcional)

Los gráficos se generan como PNG en el directorio del workspace:

```bash
# Buscar el directorio de reportes del workspace
find /home/kali/Proyectos/cybersecurity/environments/dev4-improvements/platform/backend/workspaces/ \
     -name "charts" -type d

# Listar los gráficos generados
ls -lh /path/to/workspace/reports/charts/
```

**Verificar**:
- [ ] `severity_distribution.png` existe
- [ ] `category_distribution.png` existe
- [ ] `risk_gauge.png` existe
- [ ] Tamaño de cada archivo: 50-200KB

---

## 🐛 TROUBLESHOOTING

### Error: "Task failed"
1. Verificar logs de Celery:
   ```bash
   tail -100 /tmp/dev4_celery_fixed.log
   ```
2. Buscar excepciones o errores

### Error: "No data found"
- Normal si el workspace está vacío
- El reporte se genera igual pero sin hallazgos

### Error: "PDF not generated"
1. Verificar que WeasyPrint esté instalado:
   ```bash
   cd /home/kali/Proyectos/cybersecurity/environments/dev4-improvements/platform/backend
   source venv/bin/activate
   python -c "import weasyprint; print('OK')"
   ```

### Los gráficos no aparecen en el PDF
1. Verificar Plotly y Kaleido:
   ```bash
   python -c "import plotly; import kaleido; print('OK')"
   ```
2. Verificar logs de generación de gráficos en Celery

### Frontend no conecta con Backend
1. Verificar puerto correcto: **5001** (no 5000)
2. Verificar CORS en backend
3. Revisar consola del navegador (F12)

---

## 📊 MÉTRICAS DE ÉXITO

### ✅ Validación Completa si:
- [ ] Reporte se genera sin errores
- [ ] Se guarda correctamente en BD
- [ ] PDF se descarga correctamente
- [ ] **3 gráficos aparecen en el PDF** (FASE 3)
- [ ] Portada y secciones son profesionales
- [ ] Hallazgos están bien formateados
- [ ] Severity badges con colores correctos

### ⚠️ Validación Parcial si:
- [ ] Reporte se genera pero con warnings
- [ ] Gráficos no aparecen (problema de Plotly/Kaleido)
- [ ] Algunos datos faltantes

### ❌ Validación Fallida si:
- [ ] Tarea falla con error
- [ ] PDF no se genera
- [ ] Backend no responde

---

## 📝 CHECKLIST FINAL

```
FASE 1: BASE DE DATOS
[ ] Modelo Report extendido funciona
[ ] ReportRepository guarda correctamente
[ ] Endpoints /list y /download funcionan
[ ] File hash se calcula correctamente

FASE 2: WEASYPRINT
[ ] PDF se genera con WeasyPrint
[ ] Template HTML renderiza correctamente
[ ] Estilos CSS se aplican
[ ] Portada profesional visible

FASE 3: PLOTLY CHARTS
[ ] Risk Gauge generado y visible
[ ] Severity Pie Chart generado y visible
[ ] Category Bar Chart generado y visible
[ ] Archivos PNG creados en /charts/
[ ] Imágenes nítidas en el PDF
```

---

## 🎉 PRÓXIMOS PASOS DESPUÉS DE VALIDACIÓN

### Si TODO funciona correctamente:
1. ✅ Marcar las 3 fases como validadas
2. ✅ Commit de los cambios
3. ✅ Actualizar documentación
4. ✅ Considerar deploy a producción

### Si hay problemas menores:
1. 📝 Documentar los problemas
2. 🔧 Crear issues para fix
3. ✅ Validar funcionalidad core

### Si hay problemas críticos:
1. 🐛 Revisar logs detallados
2. 🔍 Debuggear el problema específico
3. 🔧 Aplicar fix y re-validar

---

## 📞 CONTACTO

Si encontrás algún problema:
1. Copiá el error completo
2. Tomá screenshot del PDF (si se genera)
3. Compartí logs de Celery
4. Describí qué esperabas vs qué obtuviste

---

**¡Éxito en la validación!** 🚀



