# Frontend - dev3-refactor

Frontend adaptado de `dev2/` para integración con el backend refactorizado de `dev3-refactor`.

---

## 🔧 CONFIGURACIÓN INICIAL

### 1. Instalar dependencias

```bash
cd /home/kali/Proyectos/cybersecurity/environments/dev3-refactor/platform/frontend
npm install
```

### 2. Configurar variables de entorno (OPCIONAL)

El frontend ya está configurado para apuntar al backend en `http://127.0.0.1:5000/api` por defecto.

Si necesitas cambiar algo, crea un archivo `.env`:

```bash
# .env
VITE_ENV=dev
VITE_API_URL=http://127.0.0.1:5000/api
VITE_PORT=5176
VITE_ENABLE_DEBUG=true
```

---

## 🚀 EJECUTAR FRONTEND

### Desarrollo (puerto 5176)

```bash
npm run dev
```

El frontend estará disponible en: `http://localhost:5176` o `http://192.168.0.11:5176`

### Build para producción

```bash
npm run build
npm run preview
```

---

## 🔌 INTEGRACIÓN CON BACKEND

### Backend dev3-refactor

El frontend está configurado para conectarse al backend de `dev3-refactor`:

```
Backend URL: http://127.0.0.1:5000/api
Endpoints disponibles: /api/v1/*
```

### Verificar conexión

1. **Asegúrate de que el backend esté corriendo:**

```bash
cd /home/kali/Proyectos/cybersecurity/environments/dev3-refactor/platform/backend
python app.py
```

2. **Verifica que el backend responda:**

```bash
curl http://127.0.0.1:5000/api/v1/auth/health
```

3. **Levanta el frontend:**

```bash
npm run dev
```

---

## 📂 ESTRUCTURA

```
frontend/
├── src/
│   ├── components/        # Componentes reutilizables (Atomic Design)
│   │   ├── atoms/        # Componentes básicos
│   │   ├── molecules/    # Componentes compuestos
│   │   ├── organisms/    # Componentes complejos
│   │   └── templates/    # Layouts
│   ├── features/         # Módulos por funcionalidad
│   │   ├── scanning/
│   │   ├── vulnerability/
│   │   ├── reconnaissance/
│   │   ├── exploitation/        ✅ Adaptado
│   │   ├── active-directory/    ✅ Adaptado
│   │   ├── cloud-pentest/       ✅ Adaptado
│   │   └── reporting/           ✅ Adaptado
│   ├── lib/
│   │   └── api/         # Cliente API organizado por módulos
│   │       ├── shared/
│   │       │   └── client.ts    ⚠️ MODIFICADO (puerto 5000)
│   │       ├── scanning/
│   │       ├── vulnerability/
│   │       ├── exploitation/
│   │       └── ...
│   ├── pages/           # Páginas principales
│   ├── contexts/        # React contexts (Auth, Theme, etc)
│   └── hooks/           # Custom hooks
```

---

## 🔄 CAMBIOS RESPECTO A dev2

### Modificaciones principales:

1. **client.ts** - URL del backend cambiada a puerto 5000
   - Antes: `http://127.0.0.1:5003/api` (dev2)
   - Ahora: `http://127.0.0.1:5000/api` (dev3)

2. **Módulos adaptados:**
   - ✅ Exploitation (Hydra, CrackMapExec, Impacket)
   - ✅ Active Directory (Kerberoasting, DCSync, etc)
   - ✅ Cloud Pentesting (Prowler, ScoutSuite)
   - ✅ Reporting (Executive, Technical, JSON export)

3. **Endpoints nuevos integrados:**
   - `/api/v1/exploitation/*`
   - `/api/v1/post-exploitation/*`
   - `/api/v1/active-directory/*`
   - `/api/v1/cloud/*`
   - `/api/v1/reporting/*`

---

## ✅ VERIFICAR INTEGRACIÓN

### 1. Login

```bash
# Test de login
curl -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 2. Endpoints funcionales

Una vez logueado, verifica que los endpoints respondan:

```bash
# Scanning
GET /api/v1/scanning/scans?workspace_id=1

# Vulnerability
GET /api/v1/vulnerability/list?workspace_id=1

# Reporting
GET /api/v1/reporting/list?workspace_id=1
```

---

## 🧪 TESTING

```bash
# Tests unitarios
npm run test

# Tests con UI
npm run test:ui

# Cobertura
npm run test:coverage
```

---

## 📝 NOTAS IMPORTANTES

1. **dev2 NO fue modificado** - Este frontend es una copia independiente
2. **Backend dev3 requerido** - El frontend no funcionará sin el backend
3. **Puerto 5176** - El frontend corre en puerto 5176 (diferente de dev2: 5173)
4. **JWT Auth** - Todos los endpoints requieren token Bearer

---

## 🐛 TROUBLESHOOTING

### Error: "Network Error" en login

**Causa:** Backend no está corriendo o URL incorrecta

**Solución:**
```bash
# Verificar backend
curl http://127.0.0.1:5000/api/v1/auth/health

# Si no responde, levantar backend:
cd ../backend
python app.py
```

### Error: "CORS policy"

**Causa:** Backend no tiene CORS configurado correctamente

**Solución:** Verificar en `backend/app.py` que CORS esté habilitado:
```python
from flask_cors import CORS
CORS(app)
```

### Error: "401 Unauthorized"

**Causa:** Token expiró o no existe

**Solución:** Limpiar localStorage y volver a loguearse:
```javascript
// En consola del navegador:
localStorage.clear()
// Luego recargar la página
```

---

## 🚀 PRÓXIMOS PASOS

1. ✅ Instalar dependencias (`npm install`)
2. ✅ Verificar backend corriendo (puerto 5000)
3. ✅ Levantar frontend (`npm run dev`)
4. ✅ Probar login en http://localhost:5176
5. 🔄 Verificar módulos nuevos (Exploitation, AD, Cloud)
6. 🔄 Reportar bugs o mejoras

---

**Última actualización:** 22 de Noviembre de 2025


