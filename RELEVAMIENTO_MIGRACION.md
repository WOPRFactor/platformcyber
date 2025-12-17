# Relevamiento Completo - Migración Frontend

## Resumen Ejecutivo

- **Total archivos en src/**: 315 archivos (.tsx/.ts)
- **Total archivos en src-new/**: 316 archivos (.tsx/.ts)
- **Archivos con tema antiguo detectados**: 14 archivos
- **Archivos que NO están en src-new**: 0 archivos

## Archivos con Tema Antiguo que Necesitan Migración

### 1. Archivos con `border-green-700` (Tema Cyberpunk - Necesita Migración)

Estos archivos tienen bordes verdes oscuros del tema antiguo:

1. **components/Layout.tsx**
   - Línea 347: `border-t border-green-700`
   - **Acción**: Cambiar a `border-t border-gray-200` o `border-red-500` para activo

2. **components/ProcessGraphConsole/components/ProcessGraphTabs.tsx**
   - Línea 32: `border-b border-green-700`
   - **Acción**: Cambiar a `border-b border-gray-200` con `border-red-500` para activo

### 2. Archivos con `text-green-200` (Texto Verde Claro - Tema Oscuro)

1. **pages/IA/components/ChatbotTab.tsx**
   - Línea 59: `text-green-200`
   - **Acción**: Cambiar a `text-gray-700` o `text-gray-900`

### 3. Archivos con `bg-green-900 text-green-200` (Fondo Verde Oscuro - Tema Antiguo)

1. **pages/Reporting/components/ExecutiveReportModal.tsx**
   - Línea 213: `bg-green-900 text-green-200`
   - **Acción**: Cambiar a fondo claro con texto oscuro según guía de estilos

2. **pages/Reporting/components/ExecutiveSummary.tsx**
   - Línea 62: `bg-green-900 text-green-200`
   - **Acción**: Cambiar a fondo claro con texto oscuro según guía de estilos

### 4. Archivos con `text-green-400/text-green-500` en StatCard (Verificar Contexto)

1. **components/charts/StatCard.tsx**
   - Líneas 63-65: `text-green-400`, `text-green-500`, `border-green-500/30`
   - **Estado**: Ya migrado manualmente el fondo, pero los esquemas de color pueden necesitar ajuste
   - **Acción**: Verificar si estos colores son para estados específicos o parte del tema

### 5. Archivos con Clases Válidas (NO Necesitan Cambio)

Estos archivos tienen clases que son válidas en el nuevo tema (estados de éxito):

- `pages/Integrations/components/integrations/BurpSection.tsx` - `bg-green-50 border-green-200` ✅
- `pages/Integrations/components/shared/DirectoriesList.tsx` - `bg-green-100 text-green-800` ✅
- `pages/Integrations/components/shared/IntegrationHistory.tsx` - `bg-green-100 text-green-800` ✅
- `pages/PentestSelector/components/DashboardSection.tsx` - `bg-green-100 text-green-800` ✅
- `pages/PentestSelector/components/ProjectsSection.tsx` - `bg-green-100 text-green-800` ✅
- `pages/Reporting/components/ComplianceReport.tsx` - `bg-green-100 text-green-800` ✅
- `pages/WhiteboxTesting/components/SessionsHistory.tsx` - `bg-green-100 text-green-800` ✅
- `components/scanning/ScanningHistory.tsx` - `bg-green-100 text-green-800` ✅

## Archivos que Requieren Migración Manual

### Prioridad Alta (Tema Antiguo Claro)

1. **components/Layout.tsx** - `border-green-700`
2. **components/ProcessGraphConsole/components/ProcessGraphTabs.tsx** - `border-green-700`
3. **pages/IA/components/ChatbotTab.tsx** - `text-green-200`
4. **pages/Reporting/components/ExecutiveReportModal.tsx** - `bg-green-900 text-green-200`
5. **pages/Reporting/components/ExecutiveSummary.tsx** - `bg-green-900 text-green-200`

### Prioridad Media (Verificar Contexto)

1. **components/charts/StatCard.tsx** - Verificar esquemas de color `text-green-400/500`

## Patrones del Tema Antiguo a Buscar

### Clases que Indican Tema Antiguo (Cyberpunk)

- `bg-gray-800`, `bg-gray-900` - Fondos oscuros ❌
- `border-green-700`, `border-green-600` - Bordes verdes oscuros ❌
- `text-green-200`, `text-green-300` - Texto verde claro ❌
- `bg-green-900`, `bg-green-800` - Fondos verdes oscuros ❌
- `from-gray-800`, `to-gray-900` - Gradientes oscuros ❌
- `text-gray-400` en contexto de fondo oscuro ❌

### Clases Válidas del Nuevo Tema (NO Cambiar)

- `bg-green-50`, `bg-green-100` - Fondos claros para estados ✅
- `text-green-700`, `text-green-800` - Texto oscuro sobre fondo claro ✅
- `border-green-200` - Bordes claros ✅

## Plan de Acción

### Fase 1: Migración de Bordes Verdes Oscuros
- [ ] `components/Layout.tsx` - Cambiar `border-green-700` a `border-gray-200` o `border-red-500`
- [ ] `components/ProcessGraphConsole/components/ProcessGraphTabs.tsx` - Cambiar `border-green-700` a tema nuevo

### Fase 2: Migración de Textos Verdes Claros
- [ ] `pages/IA/components/ChatbotTab.tsx` - Cambiar `text-green-200` a `text-gray-700`

### Fase 3: Migración de Fondos Verdes Oscuros
- [ ] `pages/Reporting/components/ExecutiveReportModal.tsx` - Migrar a fondo claro
- [ ] `pages/Reporting/components/ExecutiveSummary.tsx` - Migrar a fondo claro

### Fase 4: Revisión de StatCard
- [ ] Verificar si los esquemas de color `green` en StatCard son apropiados o necesitan ajuste

## Notas

- `src-new/` contiene aproximadamente el mismo número de archivos que `src/` (316 vs 315)
- No hay archivos en `src/` que no estén en `src-new/`
- La mayoría de archivos ya fueron migrados al copiar desde `src-new/`
- Quedan 5 archivos con tema antiguo claro que requieren migración manual

