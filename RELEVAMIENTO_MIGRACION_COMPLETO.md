# Relevamiento Completo - Migración Frontend

## Resumen Ejecutivo

**Fecha:** $(date)
**Total archivos con tema antiguo encontrados:** 12 archivos
**Estado:** Relevamiento completo de `src/` sin usar `src-new/` como referencia

---

## Archivos que Requieren Migración

### 1. components/charts/StatCard.tsx
**Patrones encontrados:**
- `text-green-400` (líneas 63, 131, 135)
- `text-gray-400` (posiblemente en contexto de fondo oscuro)

**Acción requerida:**
- Revisar esquemas de color `green` - pueden ser válidos para estados, pero verificar contexto
- Cambiar `text-gray-400` a `text-gray-500` o `text-gray-700` según guía

---

### 2. components/DatePicker.tsx
**Patrones encontrados:**
- `bg-green-900 text-gray-700` (línea 170)

**Acción requerida:**
- Cambiar fondo verde oscuro a fondo claro según guía de estilos
- Ajustar colores de texto para tema light

---

### 3. components/GlobalSearch.tsx
**Patrones encontrados:**
- `dark:bg-green-900 dark:text-gray-700` (línea 199)
- `bg-green-100` (válido, pero verificar contexto)

**Acción requerida:**
- Eliminar clases `dark:` del tema antiguo
- Migrar a tema light según guía

---

### 4. components/Layout.tsx
**Patrones encontrados:**
- `border-green-700` (línea 347)

**Acción requerida:**
- Cambiar `border-green-700` a `border-gray-200` o `border-red-500` para estados activos

---

### 5. components/ProcessGraphConsole/components/ProcessGraphTabs.tsx
**Patrones encontrados:**
- `border-green-700` (línea 32)

**Acción requerida:**
- Cambiar `border-green-700` a `border-gray-200` con `border-red-500` para tab activo

---

### 6. components/scanning/NmapSection.tsx
**Patrones encontrados:**
- `disabled:bg-green-800` (línea 240)
- `bg-gradient-to-r from-green-600 to-blue-600` (línea 356)
- `hover:from-green-700 hover:to-blue-700` (línea 356)
- `disabled:from-green-800 disabled:to-blue-800` (línea 356)

**Acción requerida:**
- Cambiar gradientes verdes oscuros a colores del nuevo tema (rojo/azul según guía)
- Cambiar estados disabled a colores apropiados del nuevo tema

---

### 7. pages/IA/components/ChatbotTab.tsx
**Patrones encontrados:**
- `bg-green-900/50` (línea 58)
- `text-green-200` (línea 59)

**Acción requerida:**
- Cambiar fondo verde oscuro a fondo claro (`bg-white` o `bg-gray-50`)
- Cambiar `text-green-200` a `text-gray-700` o `text-gray-900`

---

### 8. pages/IA/components/LegacyTab.tsx
**Patrones encontrados:**
- `bg-green-900/20` (línea 65)

**Acción requerida:**
- Cambiar fondo verde oscuro semitransparente a fondo claro según guía

---

### 9. pages/Reconnaissance/components/tools/CompleteReconSection.tsx
**Patrones encontrados:**
- `disabled:bg-green-800` (línea 64)

**Acción requerida:**
- Cambiar estado disabled de verde oscuro a color apropiado del nuevo tema

---

### 10. pages/Reporting/components/ExecutiveReportModal.tsx
**Patrones encontrados:**
- `bg-green-900/20` (línea 92)
- `bg-green-900 text-green-200` (línea 213)
- `bg-green-900 text-gray-700` (línea 399)

**Acción requerida:**
- Migrar todos los fondos verdes oscuros a fondos claros
- Cambiar textos verdes claros a textos oscuros según guía

---

### 11. pages/Reporting/components/ExecutiveSummary.tsx
**Patrones encontrados:**
- `bg-green-900 text-green-200` (línea 62)

**Acción requerida:**
- Cambiar fondo verde oscuro a fondo claro
- Cambiar texto verde claro a texto oscuro

---

### 12. pages/Reporting/components/ReportsHistory.tsx
**Patrones encontrados:**
- `bg-green-900 text-gray-700` (líneas 196, 204)

**Acción requerida:**
- Cambiar fondos verdes oscuros a fondos claros
- Ajustar colores de texto según guía

---

## Patrones del Tema Antiguo Detectados

### Fondos Oscuros
- `bg-gray-800`, `bg-gray-900` - ❌ Eliminar
- `bg-green-800`, `bg-green-900` - ❌ Eliminar
- `bg-green-900/20`, `bg-green-900/50` - ❌ Eliminar

### Bordes Verdes Oscuros (Cyberpunk)
- `border-green-600`, `border-green-700`, `border-green-800`, `border-green-900` - ❌ Eliminar

### Textos Verdes Claros (Sobre Fondo Oscuro)
- `text-green-200`, `text-green-300`, `text-green-400` - ❌ Eliminar (excepto en contextos específicos de estados)

### Gradientes Oscuros
- `from-green-600`, `to-green-700`, `from-green-800`, `to-green-800` - ❌ Eliminar
- `from-gray-800`, `to-gray-900` - ❌ Eliminar

### Estados Disabled con Verde Oscuro
- `disabled:bg-green-800` - ❌ Cambiar a color apropiado del nuevo tema

---

## Clases Válidas del Nuevo Tema (NO Cambiar)

Estas clases son válidas y NO deben cambiarse:
- `bg-green-50`, `bg-green-100` - Fondos claros para estados de éxito ✅
- `text-green-700`, `text-green-800` - Texto oscuro sobre fondo claro ✅
- `border-green-200` - Bordes claros ✅

---

## Plan de Migración

### Prioridad Alta (Componentes Core)
1. `components/Layout.tsx` - Layout principal
2. `components/charts/StatCard.tsx` - Componente de estadísticas
3. `components/DatePicker.tsx` - Selector de fechas
4. `components/GlobalSearch.tsx` - Búsqueda global

### Prioridad Media (Componentes de Funcionalidad)
5. `components/ProcessGraphConsole/components/ProcessGraphTabs.tsx` - Tabs
6. `components/scanning/NmapSection.tsx` - Sección de Nmap

### Prioridad Baja (Páginas Específicas)
7. `pages/IA/components/ChatbotTab.tsx` - Chatbot
8. `pages/IA/components/LegacyTab.tsx` - Tab legacy
9. `pages/Reconnaissance/components/tools/CompleteReconSection.tsx` - Reconnaissance
10. `pages/Reporting/components/ExecutiveReportModal.tsx` - Modal de reportes
11. `pages/Reporting/components/ExecutiveSummary.tsx` - Resumen ejecutivo
12. `pages/Reporting/components/ReportsHistory.tsx` - Historial de reportes

---

## Notas

- Este relevamiento se hizo directamente sobre `src/` sin usar `src-new/` como referencia
- `src-new/` era solo un ejemplo/punto de partida y ya no se usa
- Todos los archivos listados necesitan migración manual según `guiadeestilos.md`
- Total: **12 archivos** requieren migración

