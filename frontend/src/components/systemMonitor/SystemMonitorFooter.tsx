/**
 * SystemMonitorFooter Component
 * =============================
 * 
 * Footer con información de usuario y estado.
 * Mantiene el mismo estilo que MonitoringConsole.
 */

import React from 'react'

interface SystemMonitorFooterProps {
  username?: string
  activeTasksCount: number
  totalLogs: number
  isConnected: boolean
}

export const SystemMonitorFooter: React.FC<SystemMonitorFooterProps> = ({
  username,
  activeTasksCount,
  totalLogs,
  isConnected
}) => {
  return (
    <div className="p-2 border-t border-green-500 bg-gray-800 text-xs text-gray-400 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <span>
          Usuario: <span className="text-green-400">{username || 'N/A'}</span>
        </span>
        <span>•</span>
        <span>
          Estado: <span className="text-cyan-400">
            {activeTasksCount > 0 ? `${activeTasksCount} ejecutándose` : 'En espera'}
          </span>
        </span>
        <span>•</span>
        <span>
          Logs: <span className="text-cyan-400">{totalLogs}</span>
        </span>
        <span>•</span>
        <span>
          WebSocket: <span className={isConnected ? 'text-green-400' : 'text-red-400'}>
            {isConnected ? 'Conectado' : 'Desconectado'}
          </span>
        </span>
      </div>
      <div className="flex items-center space-x-2">
        <span>Versión: Factor X v2.0</span>
      </div>
    </div>
  )
}


