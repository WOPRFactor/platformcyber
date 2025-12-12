# 🚀 INSTRUCCIONES DE INICIO RÁPIDO - VALIDACIÓN REPORTERÍA V2

## ✅ ESTADO ACTUAL

### Backend ✅
- **Puerto**: 5001
- **Estado**: ✅ Running
- **PID**: 1070852

### Celery ✅
- **Workers**: 3 procesos
- **Estado**: ✅ celery@kali ready

### Redis ✅
- **Estado**: ✅ PONG

### Frontend ❌
- **Estado**: ❌ No está corriendo
- **Acción**: Necesitás levantarlo

---

## 📋 PASO A PASO PARA VALIDACIÓN

### 1. Iniciar Frontend

Abrí una **nueva terminal** y ejecutá:

```bash
# Ir al directorio del frontend
cd /home/kali/Proyectos/cybersecurity/environments/dev4-improvements/platform/frontend

# Instalar dependencias (si es la primera vez)
npm install

# Iniciar el servidor de desarrollo
npm run dev
```

**Esperá a ver**:
```
  VITE vX.X.X  ready in XXX ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

---

### 2. Acceder a la Aplicación

1. Abrí tu navegador
2. Andá a: **http://localhost:3000**
3. Iniciá sesión (si es necesario)

---

### 3. Navegar a Reportería V2

Dos opciones:

#### **Opción A**: URL Directa
```
http://localhost:3000/reporting-v2
```

#### **Opción B**: Desde el menú
1. Clic en el menú lateral
2. Buscar "Reporting V2" o "Reports"
3. Clic en la opción

---

### 4. Generar Reporte

1. **Seleccionar Workspace**
   - Elegí un workspace del dropdown
   - Cualquier workspace funciona (incluso vacío)

2. **Clic en "Generate Technical Report"**
   - Observá la barra de progreso
   - Esperá el mensaje "Completed"

3. **Descargar PDF**
   - Clic en el botón de descarga
   - El archivo se guarda en tu carpeta de Descargas

---

### 5. Verificar PDF

Abrí el PDF descargado y verificá:

#### ✅ CHECKLIST RÁPIDO:
- [ ] **Portada** profesional con workspace y fecha
- [ ] **Resumen ejecutivo** con risk score y estadísticas
- [ ] **3 GRÁFICOS** (NUEVO):
  - [ ] Risk Gauge (velocímetro)
  - [ ] Severity Pie Chart (torta)
  - [ ] Category Bar Chart (barras)
- [ ] **Hallazgos** agrupados por categoría
- [ ] **Formato** profesional y legible

---

## 🐛 SI ALGO FALLA

### Frontend no levanta
```bash
# Verificar puerto
lsof -i :3000

# Si está ocupado, matar el proceso
kill -9 $(lsof -t -i:3000)

# Reintentar
npm run dev
```

### Backend no responde
```bash
# Verificar puerto 5001
curl http://localhost:5001/api/health

# Si no responde, reiniciar
cd /home/kali/Proyectos/cybersecurity/environments/dev4-improvements/platform/backend
pkill -f "python.*app.py"
source venv/bin/activate
python app.py
```

### Celery no procesa
```bash
# Ver logs
tail -f /tmp/dev4_celery_fixed.log

# Reiniciar si es necesario
pkill -9 -f celery
cd /home/kali/Proyectos/cybersecurity/environments/dev4-improvements/platform/backend
source venv/bin/activate
celery -A celery_app worker --loglevel=info
```

---

## 📊 VALIDACIÓN COMPLETA

Para una validación detallada, seguí:
```
GUIA_VALIDACION_MANUAL.md
```

---

## ✅ CUANDO TODO FUNCIONE

Avisame y te doy el resumen final con:
- ✅ Status de las 3 fases
- ✅ Próximos pasos
- ✅ Documentación generada

---

**¡Suerte con la validación!** 🎯



