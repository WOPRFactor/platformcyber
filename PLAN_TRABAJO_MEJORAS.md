# Plan de Trabajo - Mejoras Frontend

**Fecha de inicio:** $(date)  
**Estado:** Pendiente de aprobación  
**Estimación total:** 5-7 días de trabajo

---

## 📋 Resumen Ejecutivo

Este plan detalla la implementación de las 23 mejoras identificadas en `DOCUMENTO_MEJORAS_FRONTEND.md`, organizadas en 4 fases con tareas específicas, archivos a modificar, y criterios de validación.

---

## 🎯 Fase 1: Correcciones Críticas (Día 1-2)

**Objetivo:** Corregir errores que afectan funcionalidad y legibilidad  
**Prioridad:** 🔴 ALTA  
**Estimación:** 1-2 días

### Tarea 1.1: Corregir FormField.tsx
**Archivo:** `components/FormField.tsx`  
**Tiempo estimado:** 30 minutos

**Cambios específicos:**
1. Línea 48: `text-white` → `text-gray-900`
2. Línea 50: `disabled:bg-gray-700` → `disabled:bg-gray-100`
3. Línea 50: `disabled:text-gray-500` → `disabled:text-gray-400`
4. Línea 55: Verificar `border-red-500` (ya correcto)
5. Línea 60: `focus:ring-blue-500/20` → `focus:ring-red-500/20`
6. Línea 60: `focus:border-blue-500` → `focus:border-red-500`
7. Líneas 68, 95, 110: `text-red-400` → `text-red-600`

**Validación:**
- [ ] Inputs tienen texto visible (text-gray-900)
- [ ] Estados disabled tienen fondo claro
- [ ] Focus ring es rojo (red-500/20)
- [ ] Errores tienen color rojo-600

**Comando de verificación:**
```bash
grep -n "text-white\|disabled:bg-gray-700\|focus:ring-blue" components/FormField.tsx
```

---

### Tarea 1.2: Eliminar clases `dark:` residuales
**Archivos:** 5 archivos  
**Tiempo estimado:** 1-2 horas

**Archivos a modificar:**
1. `components/GlobalSearch.tsx` (~15 instancias)
2. `components/ScanProgressMonitor.tsx`
3. `components/ThemeSelector.tsx`
4. `components/NotificationPanel.tsx`
5. `components/VulnerabilityAlerts.tsx`

**Estrategia:**
- Buscar todas las clases `dark:*`
- Eliminar la parte `dark:*` manteniendo solo la clase light
- Ejemplo: `bg-white dark:bg-gray-700` → `bg-white`

**Validación:**
- [ ] 0 instancias de `dark:` en estos archivos
- [ ] Componentes se ven correctamente en tema light

**Comando de verificación:**
```bash
grep -r "dark:" components/GlobalSearch.tsx components/ScanProgressMonitor.tsx components/ThemeSelector.tsx components/NotificationPanel.tsx components/VulnerabilityAlerts.tsx
```

---

### Tarea 1.3: Corregir `text-white` en fondos claros (muestra)
**Archivos:** ~53 archivos (empezar con los más críticos)  
**Tiempo estimado:** 2-3 horas

**Prioridad de archivos:**
1. `pages/IA/components/ChatbotTab.tsx`
2. `pages/Reporting/components/ExecutiveReportModal.tsx`
3. `pages/Reporting/components/ReportsHistory.tsx`
4. `pages/Reconnaissance/components/tools/CompleteReconSection.tsx`
5. Resto de archivos en `pages/*/components/**/*.tsx`

**Estrategia:**
- Buscar `text-white` en contexto de fondos claros (`bg-white`, `bg-gray-50`, etc.)
- Cambiar a `text-gray-900` o `text-gray-700` según jerarquía
- Títulos: `text-gray-900`
- Texto secundario: `text-gray-700`

**Validación:**
- [ ] Texto visible en todos los componentes revisados
- [ ] No hay texto blanco sobre fondo blanco

**Comando de verificación:**
```bash
# Buscar text-white en archivos de páginas
grep -r "text-white" pages/ --include="*.tsx" | grep -v "bg-red\|bg-blue\|bg-gray-900\|bg-slate-900"
```

---

## 🎨 Fase 2: Consistencia Visual (Día 3-4)

**Objetivo:** Estandarizar estilos según guía de diseño  
**Prioridad:** 🟡 MEDIA  
**Estimación:** 2 días

### Tarea 2.1: Estandarizar border-radius
**Archivos:** ~46 archivos  
**Tiempo estimado:** 2-3 horas

**Reglas:**
- Cards: `rounded-lg` → `rounded-xl`
- Botones: mantener `rounded-lg` (ya correcto en mayoría)
- Inputs: mantener `rounded-lg` (ya correcto)

**Estrategia:**
1. Buscar cards con `rounded-lg`
2. Cambiar a `rounded-xl`
3. Verificar que botones mantengan `rounded-lg`

**Validación:**
- [ ] Todas las cards usan `rounded-xl`
- [ ] Todos los botones usan `rounded-lg`
- [ ] Todos los inputs usan `rounded-lg`

**Comando de verificación:**
```bash
# Buscar cards con rounded-lg
grep -r "bg-white.*rounded-lg\|bg-gray-50.*rounded-lg" --include="*.tsx" | grep -v "button\|btn"
```

---

### Tarea 2.2: Eliminar `bg-gray-800/900` residuales
**Archivos:** ~20-30 instancias  
**Tiempo estimado:** 1-2 horas

**Estrategia:**
- Buscar `bg-gray-800` y `bg-gray-900`
- Cambiar a `bg-white` o `bg-gray-50` según contexto
- Excepción: Sidebar puede mantener `bg-slate-900` (correcto)

**Validación:**
- [ ] 0 instancias de `bg-gray-800` (excepto en comentarios/backups)
- [ ] 0 instancias de `bg-gray-900` (excepto sidebar)

**Comando de verificación:**
```bash
grep -r "bg-gray-800\|bg-gray-900" --include="*.tsx" | grep -v "backup\|\.bak\|sidebar\|slate"
```

---

### Tarea 2.3: Estandarizar botones
**Archivos:** Todos los componentes de páginas  
**Tiempo estimado:** 3-4 horas

**Estrategia:**
1. Identificar patrones de botones:
   - Primary: `bg-red-600 hover:bg-red-700 text-white rounded-lg`
   - Secondary: `bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg`
   - Ghost: `text-gray-600 hover:bg-gray-100 rounded-lg`

2. Reemplazar clases CSS (`.btn-primary`) por clases utilitarias según guía

3. Asegurar consistencia en:
   - Padding: `px-4 py-2`
   - Font: `font-medium`
   - Transitions: `transition-colors`

**Validación:**
- [ ] Todos los botones primary usan `bg-red-600`
- [ ] Todos los botones secondary usan `bg-gray-100`
- [ ] Transiciones consistentes

**Comando de verificación:**
```bash
# Buscar botones con estilos inconsistentes
grep -r "btn-primary\|btn-secondary" --include="*.tsx" | head -20
```

---

### Tarea 2.4: Corregir colores de severidad
**Archivos:** ~15-20 archivos  
**Tiempo estimado:** 2 horas

**Mapeo según guía:**
- Critical: `text-red-600 bg-red-50`
- High: `text-orange-600 bg-orange-50`
- Medium: `text-amber-600 bg-amber-50`
- Low: `text-blue-600 bg-blue-50`
- Info: `text-gray-500 bg-gray-50`

**Archivos a revisar:**
- Componentes de vulnerabilidades
- Badges de estado
- Alertas y notificaciones

**Validación:**
- [ ] Todos los badges de severidad usan colores de guía
- [ ] Consistencia en todos los componentes

**Comando de verificación:**
```bash
# Buscar badges de severidad
grep -r "critical\|high\|medium\|low" --include="*.tsx" | grep -i "bg-\|text-" | head -30
```

---

## ✨ Fase 3: Refinamiento (Día 5)

**Objetivo:** Mejorar UX y accesibilidad  
**Prioridad:** 🟢 BAJA  
**Estimación:** 1 día

### Tarea 3.1: Estandarizar espaciado
**Archivos:** Todos los componentes  
**Tiempo estimado:** 2-3 horas

**Reglas:**
- Page spacing: `space-y-6`
- Card padding: `p-6`
- Section spacing: `space-y-4` o `gap-4`
- Compact spacing: `space-y-2` o `gap-2`

**Estrategia:**
- Revisar y corregir espaciados inconsistentes
- Priorizar componentes más visibles

**Validación:**
- [ ] Espaciado consistente en páginas principales
- [ ] Cards tienen padding `p-6`

---

### Tarea 3.2: Estandarizar tipografía
**Archivos:** Todos los componentes  
**Tiempo estimado:** 2-3 horas

**Reglas:**
- Page Title: `text-2xl font-semibold text-gray-900`
- Section Title: `text-lg font-semibold text-gray-900`
- Card Title: `text-base font-semibold text-gray-900`
- Body: `text-sm text-gray-700`

**Validación:**
- [ ] Títulos de página consistentes
- [ ] Títulos de sección consistentes

---

### Tarea 3.3: Mejorar estados de focus
**Archivos:** Componentes con inputs  
**Tiempo estimado:** 1 hora

**Regla:**
- `focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500`

**Validación:**
- [ ] Todos los inputs tienen focus ring rojo

---

### Tarea 3.4: Mejorar estados disabled
**Archivos:** Botones e inputs  
**Tiempo estimado:** 1 hora

**Regla:**
- `disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed`

**Validación:**
- [ ] Estados disabled consistentes

---

### Tarea 3.5: Mejorar contraste
**Archivos:** Componentes con texto secundario  
**Tiempo estimado:** 1 hora

**Estrategia:**
- Cambiar `text-gray-400` → `text-gray-600` cuando contraste sea bajo
- Cambiar `text-gray-500` → `text-gray-700` cuando sea necesario

**Validación:**
- [ ] Texto legible en todos los componentes

---

## 🧹 Fase 4: Limpieza (Día 6-7, Opcional)

**Objetivo:** Limpieza y optimización  
**Prioridad:** 🟢 BAJA  
**Estimación:** 1-2 días

### Tarea 4.1: Limpiar clases CSS no usadas
**Archivo:** `index.css`  
**Tiempo estimado:** 1 hora

**Estrategia:**
1. Buscar uso de `.btn-primary`, `.btn-secondary`, `.card`, `.input`
2. Si no se usan, eliminar del CSS
3. Si se usan, documentar y asegurar uso consistente

**Validación:**
- [ ] CSS limpio o documentado

---

### Tarea 4.2: Identificar componentes duplicados
**Archivos:** Todos los componentes  
**Tiempo estimado:** 2-3 horas

**Estrategia:**
- Revisar componentes similares
- Identificar patrones comunes
- Documentar oportunidades de refactorización

**Validación:**
- [ ] Lista de componentes duplicados creada

---

## 📊 Métricas de Éxito

Al finalizar todas las fases, deberíamos tener:

- ✅ 0 archivos con clases `dark:`
- ✅ 0 archivos con `text-white` en fondos claros
- ✅ 0 archivos con `bg-gray-800/900` (excepto sidebar)
- ✅ 100% de inputs con `focus:ring-red-500/20`
- ✅ 100% de botones con estilos consistentes
- ✅ 100% de cards con `rounded-xl`
- ✅ 100% de severidades usando colores de guía

---

## 🚀 Orden de Ejecución Recomendado

### Día 1 (Mañana)
1. ✅ Tarea 1.1: FormField.tsx (30 min)
2. ✅ Tarea 1.2: Eliminar dark: (1-2 horas)
3. ✅ Tarea 1.3: text-white críticos (2 horas)

### Día 1 (Tarde) - Día 2
4. ✅ Tarea 1.3: text-white resto de archivos (3-4 horas)
5. ✅ Validación Fase 1

### Día 3
6. ✅ Tarea 2.1: border-radius (2-3 horas)
7. ✅ Tarea 2.2: bg-gray-800/900 (1-2 horas)

### Día 4
8. ✅ Tarea 2.3: Estandarizar botones (3-4 horas)
9. ✅ Tarea 2.4: Colores severidad (2 horas)

### Día 5
10. ✅ Tarea 3.1: Espaciado (2-3 horas)
11. ✅ Tarea 3.2: Tipografía (2-3 horas)
12. ✅ Tarea 3.3-3.5: Focus, disabled, contraste (3 horas)

### Día 6-7 (Opcional)
13. ✅ Tarea 4.1: Limpiar CSS (1 hora)
14. ✅ Tarea 4.2: Identificar duplicados (2-3 horas)

---

## 🔍 Comandos Útiles para Validación

```bash
# Buscar clases dark: residuales
grep -r "dark:" --include="*.tsx" | grep -v "backup\|\.bak" | wc -l

# Buscar text-white en fondos claros
grep -r "text-white" --include="*.tsx" | grep -v "bg-red\|bg-blue\|bg-gray-900\|bg-slate-900\|backup" | wc -l

# Buscar bg-gray-800/900
grep -r "bg-gray-800\|bg-gray-900" --include="*.tsx" | grep -v "backup\|\.bak\|sidebar\|slate" | wc -l

# Buscar focus rings incorrectos
grep -r "focus:ring-blue\|focus:border-blue" --include="*.tsx" | wc -l

# Buscar rounded-lg en cards
grep -r "bg-white.*rounded-lg\|bg-gray-50.*rounded-lg" --include="*.tsx" | grep -v "button\|btn" | wc -l
```

---

## 📝 Notas de Implementación

### Antes de comenzar:
1. Crear branch: `git checkout -b feature/frontend-improvements`
2. Hacer backup: Los archivos `.backup` ya existen
3. Revisar documento de mejoras: `DOCUMENTO_MEJORAS_FRONTEND.md`

### Durante la implementación:
1. Hacer commits frecuentes por tarea
2. Validar visualmente después de cada fase
3. Ejecutar linter: `npm run lint`
4. Probar funcionalidad afectada

### Después de cada fase:
1. Ejecutar comandos de validación
2. Revisar visualmente en navegador
3. Commit con mensaje descriptivo
4. Actualizar este documento con progreso

---

## ✅ Checklist de Progreso

### Fase 1: Correcciones Críticas
- [ ] Tarea 1.1: FormField.tsx
- [ ] Tarea 1.2: Eliminar dark:
- [ ] Tarea 1.3: text-white críticos
- [ ] Tarea 1.3: text-white resto
- [ ] Validación Fase 1

### Fase 2: Consistencia Visual
- [ ] Tarea 2.1: border-radius
- [ ] Tarea 2.2: bg-gray-800/900
- [ ] Tarea 2.3: Estandarizar botones
- [ ] Tarea 2.4: Colores severidad
- [ ] Validación Fase 2

### Fase 3: Refinamiento
- [ ] Tarea 3.1: Espaciado
- [ ] Tarea 3.2: Tipografía
- [ ] Tarea 3.3: Focus
- [ ] Tarea 3.4: Disabled
- [ ] Tarea 3.5: Contraste
- [ ] Validación Fase 3

### Fase 4: Limpieza (Opcional)
- [ ] Tarea 4.1: Limpiar CSS
- [ ] Tarea 4.2: Identificar duplicados

---

**Última actualización:** $(date)  
**Estado:** Listo para comenzar


