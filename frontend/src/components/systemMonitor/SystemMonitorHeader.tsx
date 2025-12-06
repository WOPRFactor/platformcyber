/**
 * SystemMonitorHeader Component
 * =============================
 * 
 * Header del monitor de sistema con título, estadísticas y controles.
 * Mantiene el mismo estilo visual que MonitoringConsole.
 */

import React from 'react'
import { Activity, X, Minimize2, Maximize2, Trash2, Download } from 'lucide-react'
import { useWorkspaceLogsStats } from '../../hooks/useWorkspaceLogsStats'

interface SystemMonitorHeaderProps {
  activeTasksCount: number
  isMinimized: boolean
  onMinimize: () => void
  onClose: () => void
  onClearLogs: () => void
  onExportLogs: () => void
  totalLogsCount: number
}

export const SystemMonitorHeader: React.FC<SystemMonitorHeaderProps> = ({
  activeTasksCount,
  isMinimized,
  onMinimize,
  onClose,
  onClearLogs,
  onExportLogs,
  totalLogsCount
}) => {
  const { stats, isLoading: isLoadingStats } = useWorkspaceLogsStats()

  // Formatear número de logs
  const formatLogCount = (count: number) => {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K`
    }
    return count.toString()
  }

  return (
    <div className="modal-header flex items-center justify-between p-3 border-b border-green-500 bg-gray-800 rounded-t-lg select-none">
      <div className="flex items-center space-x-3 flex-1 min-w-0">
        <Activity className="w-5 h-5 text-cyan-400 flex-shrink-0" />
        <div className="flex items-center space-x-2 flex-1 min-w-0">
          <h3 className="text-sm font-medium text-cyan-400 whitespace-nowrap">Monitor de Sistema</h3>
          {activeTasksCount > 0 && (
            <span className="px-2 py-1 text-xs bg-blue-500 text-black rounded-full animate-pulse whitespace-nowrap">
              {activeTasksCount} activo{activeTasksCount !== 1 ? 's' : ''}
            </span>
          )}
          {/* Estadísticas de logs */}
          {stats && !isLoadingStats && (
            <span className="text-xs text-gray-400 whitespace-nowrap truncate">
              Logs: {formatLogCount(stats.totalLogs)} entradas ({stats.sizeMB.toFixed(1)}MB)
              {stats.daysSinceFirst > 0 && ` - Últimos ${stats.daysSinceFirst} días`}
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center space-x-1 flex-shrink-0">
        {/* Botón Exportar */}
        <button
          onClick={onExportLogs}
          className="p-1.5 text-gray-400 hover:text-green-400 transition-colors"
          title="Exportar logs"
        >
          <Download className="w-4 h-4" />
        </button>
        {/* Botón Limpiar */}
        <button
          onClick={onClearLogs}
          className="p-1.5 text-gray-400 hover:text-red-400 transition-colors"
          title="Limpiar logs"
        >
          <Trash2 className="w-4 h-4" />
        </button>
        {/* Botón Minimizar */}
        <button
          onClick={onMinimize}
          className="p-1.5 text-gray-400 hover:text-cyan-400 transition-colors"
          title={isMinimized ? "Maximizar" : "Minimizar"}
        >
          {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
        </button>
        {/* Botón Cerrar */}
        <button
          onClick={onClose}
          className="p-1.5 text-gray-400 hover:text-red-400 transition-colors"
          title="Cerrar"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

