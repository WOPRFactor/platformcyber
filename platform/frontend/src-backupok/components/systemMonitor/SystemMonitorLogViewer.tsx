/**
 * SystemMonitorLogViewer Component
 * ================================
 * 
 * Área de visualización de logs con formato:
 * [SOURCE] HH:MM:SS LEVEL mensaje
 * 
 * Funcionalidades:
 * - Auto-scroll inteligente (se desactiva al hacer scroll up manual)
 * - Colores por fuente
 * - Formato monospace
 */

import React, { useEffect, useRef, useState } from 'react'
import { RealTimeLog, LogSource } from '../../types/systemMonitor'

interface SystemMonitorLogViewerProps {
  logs: RealTimeLog[]
  autoScroll: boolean
  onScrollChange: (isAtBottom: boolean) => void
}

// Colores por fuente (manteniendo paleta actual)
const getSourceColor = (source: LogSource): string => {
  switch (source) {
    case 'BACKEND': return 'text-cyan-400'
    case 'CELERY': return 'text-gray-900'
    case 'NIKTO': return 'text-yellow-400'
    case 'NMAP': return 'text-blue-400'
    case 'NUCLEI': return 'text-purple-400'
    case 'SQLMAP': return 'text-pink-400'
    case 'ZAP': return 'text-orange-400'
    case 'TESTSSL': return 'text-teal-400'
    case 'WHATWEB': return 'text-indigo-400'
    case 'DALFOX': return 'text-rose-400'
    default: return 'text-gray-600'
  }
}

// Colores por nivel
const getLevelColor = (level: string): string => {
  switch (level) {
    case 'ERROR': return 'text-red-400'
    case 'WARNING': return 'text-orange-400'
    case 'INFO': return 'text-gray-600'
    case 'DEBUG': return 'text-gray-500'
    default: return 'text-gray-600'
  }
}

export const SystemMonitorLogViewer: React.FC<SystemMonitorLogViewerProps> = ({
  logs,
  autoScroll,
  onScrollChange
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const logsEndRef = useRef<HTMLDivElement>(null)
  const [isUserScrolling, setIsUserScrolling] = useState(false)

  // Auto-scroll cuando hay nuevos logs y está activado
  useEffect(() => {
    if (autoScroll && !isUserScrolling && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, autoScroll, isUserScrolling])

  // Detectar scroll manual
  const handleScroll = () => {
    if (!containerRef.current) return

    const container = containerRef.current
    const isAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 50

    setIsUserScrolling(!isAtBottom)
    onScrollChange(isAtBottom)
  }

  // Formatear timestamp
  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('es-ES', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto p-3 bg-gray-50 font-mono text-sm"
      style={{ fontFamily: 'monospace' }}
    >
      {logs.length === 0 ? (
        <div className="text-center py-20 text-gray-500">
          <p className="text-lg mb-2">Consola lista</p>
          <p className="text-sm">Los logs aparecerán aquí en tiempo real</p>
        </div>
      ) : (
        <div className="space-y-1">
          {logs.map(log => {
            // Separador de sesión
            if (log.id === 'session-separator') {
              return (
                <div
                  key={log.id}
                  className="flex items-center justify-center py-3 my-2 border-t border-b border-gray-200/50"
                >
                  <span className="text-gray-900 font-bold text-sm px-4 bg-gray-50">
                    {log.message}
                  </span>
                </div>
              )
            }

            return (
              <div
                key={log.id}
                className={`flex items-start space-x-2 text-xs hover:bg-white/30 px-2 py-1 rounded ${
                  log.id.startsWith('historical-') ? 'opacity-75' : ''
                }`}
              >
                {/* [SOURCE] */}
                <span className={`font-bold ${getSourceColor(log.source)}`}>
                  [{log.source}]
                </span>

                {/* HH:MM:SS */}
                <span className="text-gray-500">
                  {formatTime(log.timestamp)}
                </span>

                {/* LEVEL */}
                <span className={`font-medium ${getLevelColor(log.level)}`}>
                  {log.level}
                </span>

                {/* Mensaje */}
                <span className="text-gray-600 flex-1 break-words">
                  {log.raw ? log.raw : log.message}
                </span>
              </div>
            )
          })}
        </div>
      )}
      <div ref={logsEndRef} />
    </div>
  )
}

