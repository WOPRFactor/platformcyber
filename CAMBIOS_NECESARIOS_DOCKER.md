# Cambios Necesarios para Dockerizar dev4-improvements

**Fecha:** Enero 2025  
**Objetivo:** Identificar y documentar cambios en el código necesarios para dockerizar completamente el proyecto

---

## 📊 RESUMEN EJECUTIVO

**¿Modifica el proyecto actual?** ⚠️ **SÍ, requiere cambios menores pero importantes**

**Cambios necesarios:**
- 🔴 **Críticos:** 2 cambios en configuración
- 🟡 **Importantes:** 3 ajustes en rutas y variables de entorno
- 🟢 **Opcionales:** Mejoras de configuración

**Impacto:** ✅ **BAJO** - Cambios no rompen funcionalidad existente, solo hacen el código más flexible

---

## 🔴 CAMBIOS CRÍTICOS (Obligatorios)

### 1. **Eliminar Ruta Hardcodeada de SQLite en Desarrollo**

**Archivo:** `platform/backend/config/__init__.py`  
**Línea:** 75

**Problema actual:**
```python
# DevelopmentConfig
default_db_path = '/home/kali/Proyectos/cybersecurity/environments/dev4-improvements/platform/backend/dev4_pentest.db'
SQLALCHEMY_DATABASE_URI = os.getenv(
    'DATABASE_URL',
    f'sqlite:///{default_db_path}'
)
```

**Solución:**
```python
# DevelopmentConfig
# Usar ruta relativa o variable de entorno
default_db_path = os.getenv(
    'SQLITE_DB_PATH',
    str(Path(__file__).parent.parent / 'dev4_pentest.db')  # Relativo al backend
)
SQLALCHEMY_DATABASE_URI = os.getenv(
    'DATABASE_URL',
    f'sqlite:///{default_db_path}'
)
```

**Razón:** La ruta absoluta `/home/kali/...` no existe en contenedores Docker.

---

### 2. **Forzar PostgreSQL en Docker (Producción)**

**Archivo:** `platform/backend/config/__init__.py`  
**Línea:** 97-107

**Problema actual:**
```python
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is required in production")
```

**Estado:** ✅ **Ya está bien** - Requiere `DATABASE_URL` en producción

**Asegurar en Docker:**
- El `docker-compose.yml` ya configura `DATABASE_URL=postgresql://...`
- ✅ No requiere cambios en código

---

## 🟡 CAMBIOS IMPORTANTES (Recomendados)

### 3. **Hacer Configurable PROJECT_TMP_DIR**

**Archivo:** `platform/backend/utils/workspace_filesystem.py`  
**Línea:** 36-38

**Problema actual:**
```python
# Directorio temporal del proyecto (en lugar de /tmp para evitar llenar tmpfs)
PROJECT_TMP_DIR = Path(__file__).parent.parent.parent / 'tmp'
PROJECT_TMP_DIR.mkdir(parents=True, exist_ok=True)
```

**Solución:**
```python
# Directorio temporal configurable por variable de entorno
PROJECT_TMP_DIR = Path(os.getenv(
    'PROJECT_TMP_DIR',
    str(Path(__file__).parent.parent.parent / 'tmp')  # Fallback relativo
))
PROJECT_TMP_DIR.mkdir(parents=True, exist_ok=True)
```

**Razón:** Permite configurar `/tmp/scans` o `/app/tmp` en Docker según necesidad.

---

### 4. **Mejorar Fallback de WORKSPACES_BASE_DIR**

**Archivo:** `platform/backend/utils/workspace_filesystem.py`  
**Línea:** 20-33

**Problema actual:**
```python
_default_base = Path(__file__).parent.parent.parent / 'workspaces'
try:
    _default_base.mkdir(parents=True, exist_ok=True)
except (PermissionError, OSError) as e:
    logger.warning(f"No se pudo crear directorio de workspaces {_default_base}: {e}")
    # Fallback a /workspaces solo si falla crear el directorio del proyecto
    _default_base = Path('/workspaces')
```

**Solución:**
```python
# Priorizar variable de entorno, luego fallback relativo, luego /workspaces
_workspaces_base = os.getenv('WORKSPACES_BASE_DIR')
if _workspaces_base:
    _default_base = Path(_workspaces_base)
else:
    # Fallback 1: Relativo al proyecto
    _default_base = Path(__file__).parent.parent.parent / 'workspaces'
    try:
        _default_base.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        logger.warning(f"No se pudo crear directorio de workspaces {_default_base}: {e}")
        # Fallback 2: /workspaces (para Docker)
        _default_base = Path('/workspaces')

WORKSPACES_BASE_DIR = Path(_default_base)
```

**Razón:** Ya usa `WORKSPACES_BASE_DIR` pero el fallback puede mejorarse para Docker.

**Estado actual:** ✅ **Ya funciona** con `WORKSPACES_BASE_DIR`, solo mejora el fallback.

---

### 5. **Configurar LOG_DIR para Docker**

**Archivo:** `platform/backend/config/__init__.py`  
**Línea:** 53-54

**Problema actual:**
```python
LOG_DIR = os.getenv('LOG_DIR', 'logs')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
```

**Estado:** ✅ **Ya está bien** - Usa variables de entorno con fallback relativo

**Asegurar en Docker:**
```yaml
# docker-compose.yml
environment:
  - LOG_DIR=/app/logs  # O usar volumen para persistir
```

**Razón:** Los logs deben persistir en Docker, usar volumen o ruta configurable.

---

## 🟢 CAMBIOS OPCIONALES (Mejoras)

### 6. **Documentar Variables de Entorno Requeridas**

**Crear archivo:** `.env.example`

**Contenido sugerido:**
```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/pentesting_platform
# O para desarrollo local:
# DATABASE_URL=sqlite:///dev4_pentest.db
SQLITE_DB_PATH=./dev4_pentest.db

# Security
SECRET_KEY=change-this-in-production
JWT_SECRET_KEY=change-this-in-production

# CORS
CORS_ORIGINS=http://localhost:5177,http://localhost:5180

# Redis
REDIS_URL=redis://redis:6379/3
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Workspaces & Files
WORKSPACES_BASE_DIR=/workspaces
PROJECT_TMP_DIR=/tmp/scans

# Logging
LOG_DIR=logs
LOG_FILE=app.log
LOG_LEVEL=INFO

# Flask
FLASK_ENV=development
FLASK_DEBUG=1
```

---

### 7. **Validar Rutas al Iniciar Aplicación**

**Archivo:** `platform/backend/app.py`  
**Línea:** ~110 (después de `init_db`)

**Agregar validación:**
```python
def create_app(config_name: str = 'development') -> Flask:
    # ... código existente ...
    
    # Validar directorios necesarios al iniciar
    with app.app_context():
        init_db(app)
        
        # Validar directorios de workspaces y tmp
        from utils.workspace_filesystem import WORKSPACES_BASE_DIR, PROJECT_TMP_DIR
        try:
            WORKSPACES_BASE_DIR.mkdir(parents=True, exist_ok=True)
            PROJECT_TMP_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"Workspaces dir: {WORKSPACES_BASE_DIR}")
            logger.info(f"Tmp dir: {PROJECT_TMP_DIR}")
        except Exception as e:
            logger.error(f"Error validando directorios: {e}")
            raise
```

**Razón:** Falla rápido si los directorios no son accesibles en Docker.

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Fase 1: Cambios Críticos (30 minutos)
- [ ] **Cambio 1:** Eliminar ruta hardcodeada de SQLite
- [ ] **Cambio 2:** Verificar que PostgreSQL es obligatorio en producción (ya está)

### Fase 2: Cambios Importantes (1 hora)
- [ ] **Cambio 3:** Hacer `PROJECT_TMP_DIR` configurable
- [ ] **Cambio 4:** Mejorar fallback de `WORKSPACES_BASE_DIR`
- [ ] **Cambio 5:** Verificar configuración de `LOG_DIR` (ya está bien)

### Fase 3: Mejoras Opcionales (1 hora)
- [ ] **Cambio 6:** Crear `.env.example`
- [ ] **Cambio 7:** Agregar validación de directorios al inicio

### Fase 4: Testing (30 minutos)
- [ ] Probar con desarrollo local (sin Docker)
- [ ] Probar con Docker Compose
- [ ] Verificar que workspaces se crean correctamente
- [ ] Verificar que logs se escriben correctamente

**Tiempo total estimado:** 3 horas

---

## 🔍 ANÁLISIS DE IMPACTO

### ✅ **Cambios NO Rompen Funcionalidad Existente**

**Razones:**
1. Todos los cambios usan variables de entorno con fallbacks
2. Los fallbacks mantienen comportamiento actual
3. Solo se agrega flexibilidad, no se quita funcionalidad

### ✅ **Compatibilidad con Desarrollo Actual**

**Desarrollo local (sin Docker):**
- ✅ Sigue funcionando igual
- ✅ Usa rutas relativas como fallback
- ✅ No requiere configuración adicional

**Docker:**
- ✅ Requiere variables de entorno (ya configuradas en docker-compose.yml)
- ✅ Usa rutas absolutas configuradas en volúmenes

---

## 📝 RESUMEN DE ARCHIVOS A MODIFICAR

| Archivo | Cambios | Prioridad | Tiempo |
|---------|---------|-----------|--------|
| `config/__init__.py` | Eliminar ruta hardcodeada SQLite | 🔴 Crítico | 10 min |
| `utils/workspace_filesystem.py` | Hacer PROJECT_TMP_DIR configurable | 🟡 Importante | 15 min |
| `utils/workspace_filesystem.py` | Mejorar fallback WORKSPACES_BASE_DIR | 🟡 Importante | 15 min |
| `app.py` | Validar directorios al inicio | 🟢 Opcional | 20 min |
| `.env.example` | Crear archivo de ejemplo | 🟢 Opcional | 30 min |

**Total:** 5 archivos, ~1.5 horas de trabajo

---

## 🎯 CONCLUSIÓN

### **¿Modifica el proyecto actual?**

**SÍ**, pero los cambios son:
- ✅ **Mínimos** - Solo 2-3 archivos
- ✅ **No invasivos** - No rompen funcionalidad existente
- ✅ **Mejoran flexibilidad** - Código más configurable
- ✅ **Reversibles** - Fácil volver atrás si es necesario

### **Recomendación:**

**Implementar cambios críticos antes de dockerizar:**
1. Cambio 1 (SQLite) - **OBLIGATORIO**
2. Cambio 3 (PROJECT_TMP_DIR) - **RECOMENDADO**
3. Cambio 4 (WORKSPACES_BASE_DIR) - **RECOMENDADO**

Los cambios opcionales pueden hacerse después, pero mejoran la experiencia Docker.

---

**Documento generado:** Enero 2025  
**Última actualización:** Enero 2025

