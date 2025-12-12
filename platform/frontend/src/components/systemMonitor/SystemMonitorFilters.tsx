/**
 * SystemMonitorFilters Component
 * ===============================
 * 
 * Barra de filtros con:
 * - Checkboxes de fuentes (Backend, Celery, Nikto, etc.)
 * - Checkboxes de niveles (DEBUG, INFO, WARNING, ERROR)
 * - Búsqueda en tiempo real
 * - Botones de acción (Pausar, Limpiar, Exportar)
 */

import React from 'react'
import { Search, Pause, Play, Trash2, Download } from 'lucide-react'
import { SourceFilters, LevelFilters } from '../../types/systemMonitor'

interface SystemMonitorFiltersProps {
  sourceFilters: SourceFilters
  levelFilters: LevelFilters
  searchQuery: string
  isPaused: boolean
  onToggleSource: (source: keyof SourceFilters) => void
  onToggleLevel: (level: keyof LevelFilters) => void
  onSearchChange: (query: string) => void
  onTogglePause: () => void
  onClear: () => void
  onExport: () => void
}

const SOURCES: Array<{ key: keyof SourceFilters; label: string }> = [
  { key: 'backend', label: 'Backend' },
  { key: 'celery', label: 'Celery' },
  { key: 'nikto', label: 'Nikto' },
  { key: 'nmap', label: 'Nmap' },
  { key: 'nuclei', label: 'Nuclei' },
  { key: 'sqlmap', label: 'SQLMap' },
  { key: 'zap', label: 'ZAP' },
  { key: 'testssl', label: 'TestSSL' },
  { key: 'whatweb', label: 'WhatWeb' },
  { key: 'dalfox', label: 'Dalfox' }
]

const LEVELS: Array<{ key: keyof LevelFilters; label: string }> = [
  { key: 'DEBUG', label: 'DEBUG' },
  { key: 'INFO', label: 'INFO' },
  { key: 'WARNING', label: 'WARNING' },
  { key: 'ERROR', label: 'ERROR' }
]

export const SystemMonitorFilters: React.FC<SystemMonitorFiltersProps> = ({
  sourceFilters,
  levelFilters,
  searchQuery,
  isPaused,
  onToggleSource,
  onToggleLevel,
  onSearchChange,
  onTogglePause,
  onClear,
  onExport
}) => {
  return (
    <div className="p-3 border-b border-green-500 bg-gray-800 space-y-3 overflow-x-auto">
      {/* Filtros de fuente */}
      <div className="flex items-center space-x-4 min-w-0">
        <span className="text-xs text-gray-400 font-medium flex-shrink-0">Fuentes:</span>
        <div className="flex flex-wrap items-center gap-2 min-w-0 flex-1">
          {SOURCES.map(source => (
            <label
              key={source.key}
              className="flex items-center space-x-1 cursor-pointer flex-shrink-0"
            >
              <input
                type="checkbox"
                checked={sourceFilters[source.key]}
                onChange={() => onToggleSource(source.key)}
                className="w-3 h-3 text-cyan-500 bg-gray-700 border-gray-600 rounded focus:ring-cyan-500"
              />
              <span className="text-xs text-gray-300 whitespace-nowrap">{source.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Filtros de nivel y búsqueda */}
      <div className="flex items-center justify-between gap-4 min-w-0">
        <div className="flex items-center space-x-4 min-w-0 flex-shrink">
          <span className="text-xs text-gray-400 font-medium flex-shrink-0">Niveles:</span>
          <div className="flex items-center gap-2 flex-wrap">
            {LEVELS.map(level => (
              <label
                key={level.key}
                className="flex items-center space-x-1 cursor-pointer flex-shrink-0"
              >
                <input
                  type="checkbox"
                  checked={levelFilters[level.key]}
                  onChange={() => onToggleLevel(level.key)}
                  className="w-3 h-3 text-cyan-500 bg-gray-700 border-gray-600 rounded focus:ring-cyan-500"
                />
                <span className="text-xs text-gray-300 whitespace-nowrap">{level.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Búsqueda y acciones */}
        <div className="flex items-center space-x-2 flex-shrink-0">
          <div className="relative">
            <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Buscar..."
              className="pl-8 pr-3 py-1 text-xs bg-gray-700 border border-green-500 rounded text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 w-32"
            />
          </div>

          <button
            onClick={onTogglePause}
            className="p-1.5 text-gray-400 hover:text-cyan-400 transition-colors flex-shrink-0"
            title={isPaused ? "Reanudar" : "Pausar"}
          >
            {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
          </button>

          <button
            onClick={onClear}
            className="p-1.5 text-gray-400 hover:text-red-400 transition-colors flex-shrink-0"
            title="Limpiar logs"
          >
            <Trash2 className="w-4 h-4" />
          </button>

          <button
            onClick={onExport}
            className="p-1.5 text-gray-400 hover:text-cyan-400 transition-colors flex-shrink-0"
            title="Exportar logs"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}


