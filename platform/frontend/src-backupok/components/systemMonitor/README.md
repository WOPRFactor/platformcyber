# System Monitor - Consola de Logs en Tiempo Real

## Descripción

Consola de logs en tiempo real para monitorear procesos de la aplicación. Muestra logs detallados de cualquier proceso ejecutándose vía WebSocket.

## Características

- ✅ Logs en tiempo real vía WebSocket
- ✅ Filtrado avanzado (fuentes, niveles, búsqueda)
- ✅ Tabs para categorizar logs (Unified, Backend, Celery, Tools)
- ✅ Auto-scroll inteligente (se desactiva al hacer scroll up manual)
- ✅ Drag & resize como MonitoringConsole
- ✅ Look & feel idéntico al MonitoringConsole actual
- ✅ Formato de logs: `[SOURCE] HH:MM:SS LEVEL mensaje`
- ✅ Colores por fuente (BACKEND: cyan, CELERY: green, NIKTO: yellow, etc.)

## Estructura de Componentes

Todos los archivos tienen menos de 300 líneas (regla principal):

```
systemMonitor/
├── SystemMonitor.tsx          # Componente principal (< 300 líneas)
├── SystemMonitorHeader.tsx    # Header con badge
├── SystemMonitorTabs.tsx      # Tabs (Unified, Backend, Celery, Tools)
├── SystemMonitorFilters.tsx   # Filtros (fuentes, niveles, búsqueda)
├── SystemMonitorLogViewer.tsx # Área de logs
├── SystemMonitorFooter.tsx    # Footer con estado
└── index.ts                   # Exportaciones
```

## Hooks

- `useSystemMonitorLogs.ts` - Manejo de logs y WebSocket
- `useSystemMonitorFilters.ts` - Lógica de filtrado

## Uso

```tsx
import { SystemMonitor } from '../components/systemMonitor'

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button onClick={() => setIsOpen(true)}>Abrir Monitor</button>
      <SystemMonitor
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </>
  )
}
```

## Eventos WebSocket

El componente escucha los siguientes eventos:

- `backend_log` - Logs del backend Flask
- `celery_log` - Logs de Celery workers
- `tool_log` - Logs de herramientas (nikto, nmap, nuclei, etc.)

## Formato de Logs

Cada log se muestra con el formato:
```
[SOURCE] HH:MM:SS LEVEL mensaje
```

Ejemplos:
```
[BACKEND] 10:05:06 INFO  Starting vulnerability scan
[CELERY]  10:05:06 INFO  Task received: nikto_scan
[NIKTO]   10:05:07 INFO  $ nikto -h pampafishsa.com
[NIKTO]   10:05:08 INFO  + Server: nginx/1.18.0
```

## Colores por Fuente

- BACKEND: cyan-400
- CELERY: green-400
- NIKTO: yellow-400
- NMAP: blue-400
- NUCLEI: purple-400
- SQLMAP: pink-400
- ERROR: red-400
- WARNING: orange-400

## Filtros

- **Fuentes**: Backend, Celery, Nikto, Nmap, Nuclei, SQLMap, ZAP, TestSSL, WhatWeb, Dalfox
- **Niveles**: DEBUG, INFO, WARNING, ERROR
- **Búsqueda**: Texto en tiempo real
- **Acciones**: Pausar, Limpiar, Exportar

## Backend

Los eventos WebSocket se emiten desde:
- `websockets/events.py` - Funciones `emit_backend_log`, `emit_celery_log`, `emit_tool_log`
- `services/vulnerability_service.py` - Integración en ejecución de herramientas
- `utils/logging_handlers.py` - Handlers personalizados para logging


