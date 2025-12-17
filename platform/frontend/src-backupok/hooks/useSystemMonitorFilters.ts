/**
 * useSystemMonitorFilters Hook
 * =============================
 * 
 * Hook para manejar filtros de la consola de logs.
 * 
 * Funcionalidades:
 * - Filtros por fuente (backend, celery, nikto, etc.)
 * - Filtros por nivel (DEBUG, INFO, WARNING, ERROR)
 * - Búsqueda en tiempo real
 * - Filtrado por tab activo
 */

import { useState, useMemo, useCallback } from 'react'
import { RealTimeLog, SourceFilters, LevelFilters, MonitorTab } from '../types/systemMonitor'

const DEFAULT_SOURCE_FILTERS: SourceFilters = {
  backend: true,
  celery: true,
  scanning: true,  // Agregado para logs de enumeración
  nikto: true,
  nmap: true,
  nuclei: true,
  sqlmap: true,
  zap: true,
  testssl: true,
  whatweb: true,
  dalfox: true
}

const DEFAULT_LEVEL_FILTERS: LevelFilters = {
  DEBUG: true,
  INFO: true,
  WARNING: true,
  ERROR: true
}

export const useSystemMonitorFilters = (logs: RealTimeLog[]) => {
  const [activeTab, setActiveTab] = useState<MonitorTab>('unified')
  const [sourceFilters, setSourceFilters] = useState<SourceFilters>(DEFAULT_SOURCE_FILTERS)
  const [levelFilters, setLevelFilters] = useState<LevelFilters>(DEFAULT_LEVEL_FILTERS)
  const [searchQuery, setSearchQuery] = useState('')

  // Toggle de filtro de fuente
  const toggleSourceFilter = useCallback((source: keyof SourceFilters) => {
    setSourceFilters(prev => ({
      ...prev,
      [source]: !prev[source]
    }))
  }, [])

  // Toggle de filtro de nivel
  const toggleLevelFilter = useCallback((level: keyof LevelFilters) => {
    setLevelFilters(prev => ({
      ...prev,
      [level]: !prev[level]
    }))
  }, [])

  // Resetear todos los filtros
  const resetFilters = useCallback(() => {
    setSourceFilters(DEFAULT_SOURCE_FILTERS)
    setLevelFilters(DEFAULT_LEVEL_FILTERS)
    setSearchQuery('')
  }, [])

  // Filtrar logs según tab activo, fuentes, niveles y búsqueda
  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      // Filtro por tab
      if (activeTab === 'backend' && log.source !== 'BACKEND') return false
      if (activeTab === 'celery' && log.source !== 'CELERY') return false
      if (activeTab === 'tools' && !['SCANNING', 'NIKTO', 'NMAP', 'NUCLEI', 'SQLMAP', 'ZAP', 'TESTSSL', 'WHATWEB', 'DALFOX'].includes(log.source)) return false

      // Filtro por fuente
      const sourceKey = log.source.toLowerCase() as keyof SourceFilters
      if (sourceFilters[sourceKey] === false) return false

      // Filtro por nivel
      if (levelFilters[log.level] === false) return false

      // Filtro por búsqueda
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        const matchesMessage = log.message.toLowerCase().includes(query)
        const matchesSource = log.source.toLowerCase().includes(query)
        const matchesRaw = log.raw?.toLowerCase().includes(query)
        if (!matchesMessage && !matchesSource && !matchesRaw) return false
      }

      return true
    })
  }, [logs, activeTab, sourceFilters, levelFilters, searchQuery])

  return {
    activeTab,
    setActiveTab,
    sourceFilters,
    levelFilters,
    searchQuery,
    setSearchQuery,
    toggleSourceFilter,
    toggleLevelFilter,
    resetFilters,
    filteredLogs
  }
}


