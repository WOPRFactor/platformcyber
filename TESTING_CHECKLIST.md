# ✅ Testing Checklist - Workspace Separation

## 🧪 Test Plan

### Prerequisitos
- [ ] Backend corriendo
- [ ] Frontend corriendo
- [ ] Al menos 2 workspaces creados
- [ ] Usuario autenticado

---

## Test 1: Separación Básica de Scans

### Setup
1. [ ] Seleccionar "Workspace A"
2. [ ] Verificar que el selector muestra "Workspace A"

### Acciones
1. [ ] Crear un scan en Workspace A (ej: nmap 8.8.8.8)
2. [ ] Verificar que el scan aparece en el Dashboard
3. [ ] Verificar que el scan aparece en la página de Scanning

### Verificación Workspace B
1. [ ] Cambiar a "Workspace B"
2. [ ] **CRÍTICO:** El scan de Workspace A NO debe aparecer
3. [ ] Dashboard debe mostrar 0 scans (o solo los de B)
4. [ ] Crear un scan diferente en Workspace B (ej: nmap 1.1.1.1)

### Verificación de Vuelta
1. [ ] Volver a "Workspace A"
2. [ ] El scan original debe aparecer
3. [ ] El scan de Workspace B NO debe aparecer

**Status:** [ ] PASS / [ ] FAIL

---

## Test 2: Network Requests

### Verificar en DevTools (F12 → Network)

1. [ ] Seleccionar Workspace A (id=1)
2. [ ] Refrescar Dashboard
3. [ ] Buscar request a `/api/v1/scanning/sessions`
4. [ ] **Verificar URL:** Debe incluir `?workspace_id=1`

**Expected:**
```
GET /api/v1/scanning/sessions?workspace_id=1
```

5. [ ] Cambiar a Workspace B (id=2)
6. [ ] Buscar nuevo request
7. [ ] **Verificar URL:** Debe incluir `?workspace_id=2`

**Status:** [ ] PASS / [ ] FAIL

---

## Test 3: Error Handling

### Sin Workspace Seleccionado

1. [ ] Abrir DevTools → Console
2. [ ] En código, temporalmente hacer `currentWorkspace = null`
3. [ ] Intentar cargar Dashboard

**Expected Behavior:**
- [ ] NO debe hacer request al backend (enabled: false)
- [ ] Dashboard debe mostrar estado vacío/loading
- [ ] NO debe haber errores 500 en console

**Status:** [ ] PASS / [ ] FAIL

---

## Test 4: React Query Cache

### Verificar Invalidación de Cache

1. [ ] Abrir React Query DevTools (si está instalado)
2. [ ] Seleccionar Workspace A
3. [ ] Verificar query key: `['scan-sessions', 1]`
4. [ ] Cambiar a Workspace B
5. [ ] **Verificar:** Nueva query con key `['scan-sessions', 2]`
6. [ ] **Verificar:** Cache de Workspace A se mantiene separado

**Status:** [ ] PASS / [ ] FAIL

---

## Test 5: Múltiples Páginas

### Dashboard
1. [ ] Seleccionar Workspace A
2. [ ] Verificar que muestra solo scans de A
**Status:** [ ] PASS / [ ] FAIL

### Scanning Page
1. [ ] Ir a /scanning
2. [ ] Verificar que muestra solo scans de A
**Status:** [ ] PASS / [ ] FAIL

### DashboardEnhanced
1. [ ] Ir a /dashboard-enhanced (si existe)
2. [ ] Verificar que muestra solo scans de A
**Status:** [ ] PASS / [ ] FAIL

---

## Test 6: Crear Scans con Workspace

### Verificar que nuevos scans se asocian al workspace correcto

1. [ ] Seleccionar Workspace A
2. [ ] Crear un nuevo scan
3. [ ] Verificar en Network que el POST incluye `workspace_id`

**Expected Request Body:**
```json
{
  "target": "192.168.1.1",
  "scan_type": "discovery",
  "workspace_id": 1  ← DEBE ESTAR PRESENTE
}
```

**Status:** [ ] PASS / [ ] FAIL

---

## Test 7: Vulnerabilities (si aplica)

### Si tu app tiene endpoints de vulnerabilities

1. [ ] Seleccionar Workspace A
2. [ ] Ver vulnerabilidades
3. [ ] Verificar que solo muestra de Workspace A
4. [ ] Cambiar a Workspace B
5. [ ] Vulnerabilidades deben ser diferentes

**Status:** [ ] PASS / [ ] FAIL / [ ] N/A

---

## Test 8: Reportes (si aplica)

### Si tu app tiene reportes

1. [ ] Generar reporte en Workspace A
2. [ ] Cambiar a Workspace B
3. [ ] Reporte NO debe aparecer en lista de Workspace B

**Status:** [ ] PASS / [ ] FAIL / [ ] N/A

---

## Test 9: Performance

### Verificar que no hay requests innecesarios

1. [ ] Abrir Network tab
2. [ ] Seleccionar un workspace
3. [ ] **Contar requests** a `/scanning/sessions`
4. [ ] Cambiar a otro workspace
5. [ ] **Verificar:** Solo 1 nuevo request (no múltiples)

**Expected:** 1 request por cambio de workspace

**Status:** [ ] PASS / [ ] FAIL

---

## Test 10: Edge Cases

### Workspace sin scans
1. [ ] Crear nuevo Workspace vacío
2. [ ] Seleccionarlo
3. [ ] Dashboard debe mostrar "No scans" o similar
4. [ ] NO debe crashear

**Status:** [ ] PASS / [ ] FAIL

### Cambio rápido entre workspaces
1. [ ] Cambiar rápidamente entre 3+ workspaces
2. [ ] Verificar que no hay race conditions
3. [ ] Verificar que siempre muestra datos correctos

**Status:** [ ] PASS / [ ] FAIL

---

## 📊 Resumen de Resultados

| Test | Status | Notas |
|------|--------|-------|
| 1. Separación Básica | [ ] | |
| 2. Network Requests | [ ] | |
| 3. Error Handling | [ ] | |
| 4. React Query Cache | [ ] | |
| 5. Múltiples Páginas | [ ] | |
| 6. Crear Scans | [ ] | |
| 7. Vulnerabilities | [ ] | |
| 8. Reportes | [ ] | |
| 9. Performance | [ ] | |
| 10. Edge Cases | [ ] | |

**Tests Passed:** ___ / 10

---

## 🐛 Bugs Encontrados

| # | Descripción | Severidad | Status |
|---|-------------|-----------|--------|
| 1 | | [ ] Critical / [ ] High / [ ] Medium / [ ] Low | [ ] Open / [ ] Fixed |
| 2 | | [ ] Critical / [ ] High / [ ] Medium / [ ] Low | [ ] Open / [ ] Fixed |
| 3 | | [ ] Critical / [ ] High / [ ] Medium / [ ] Low | [ ] Open / [ ] Fixed |

---

## ✅ Sign-Off

**Tester:** _________________  
**Date:** _________________  
**Status:** [ ] APPROVED / [ ] NEEDS WORK  

**Notas Adicionales:**
```




```

---

## 🔄 Regression Testing

Después de cualquier cambio futuro, re-ejecutar:
- [ ] Test 1 (Separación Básica)
- [ ] Test 2 (Network Requests)
- [ ] Test 6 (Crear Scans)

Estos 3 tests cubren la funcionalidad core del fix.
