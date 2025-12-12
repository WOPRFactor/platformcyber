/**
 * useSystemMonitorLogs Hook
 * ==========================
 * 
 * Hook para manejar logs históricos y en tiempo real vía WebSocket.
 * 
 * Funcionalidades:
 * - Carga logs históricos al abrir consola o cambiar workspace
 * - Conecta a WebSocket y escucha eventos de logs en tiempo real
 * - Muestra separador "─── NUEVA SESIÓN ───" entre histórico y tiempo real
 * - Mantiene últimos 1000 logs en memoria
 * - Maneja reconexión automática
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useWebSocket } from '../contexts/WebSocketContext'
import { useWorkspace } from '../contexts/WorkspaceContext'
import { RealTimeLog, LogSource, LogLevel } from '../types/systemMonitor'
import { workspacesAPI, WorkspaceLog } from '../lib/api/workspaces/workspaces'

const MAX_LOGS = 1000
const HISTORICAL_LOGS_LIMIT = 500 // Límite de logs históricos a cargar

interface WebSocketLogEvent {
  source: string
  level: string
  message: string
  timestamp: number
  command?: string
  taskId?: string
  workspaceId?: number
}

export const useSystemMonitorLogs = () => {
  const { socket, isConnected, joinWorkspace, leaveWorkspace } = useWebSocket()
  const { currentWorkspace } = useWorkspace()
  const [logs, setLogs] = useState<RealTimeLog[]>([])
  const [isPaused, setIsPaused] = useState(false)
  const [hasLoadedHistorical, setHasLoadedHistorical] = useState(false)
  const logIdCounter = useRef(0)
  const sessionStartTime = useRef<Date | null>(null)

  // Cargar logs históricos cuando cambia el workspace
  const { data: historicalLogs, isLoading: isLoadingHistorical } = useQuery({
    queryKey: ['workspace-logs', currentWorkspace?.id],
    queryFn: async () => {
      if (!currentWorkspace?.id) return []
      const response = await workspacesAPI.getWorkspaceLogs(currentWorkspace.id, {
        limit: HISTORICAL_LOGS_LIMIT,
        per_page: HISTORICAL_LOGS_LIMIT,
        page: 1
      })
      return response.logs
    },
    enabled: !!currentWorkspace?.id,
    staleTime: 5 * 60 * 1000, // 5 minutos
    refetchOnWindowFocus: false
  })

  // Convertir logs históricos a formato RealTimeLog
  const convertHistoricalLog = useCallback((log: WorkspaceLog): RealTimeLog => {
    return {
      id: `historical-${log.id}`,
      source: log.source as LogSource,
      level: log.level as LogLevel,
      message: log.message,
      timestamp: new Date(log.timestamp),
      taskId: log.task_id,
      workspaceId: log.workspace_id,
      metadata: log.metadata,
      command: log.metadata?.command
    }
  }, [])

  // Cargar logs históricos cuando están disponibles
  useEffect(() => {
    if (historicalLogs && historicalLogs.length > 0 && !hasLoadedHistorical && currentWorkspace) {
      const convertedLogs = historicalLogs.map(convertHistoricalLog).reverse() // Más antiguos primero
      
      // Agregar separador de sesión
      const sessionSeparator: RealTimeLog = {
        id: 'session-separator',
        source: 'BACKEND',
        level: 'INFO',
        message: '─── NUEVA SESIÓN ───',
        timestamp: new Date(),
        workspaceId: currentWorkspace.id
      }

      setLogs([...convertedLogs, sessionSeparator])
      setHasLoadedHistorical(true)
      sessionStartTime.current = new Date()
    } else if (!currentWorkspace || !historicalLogs) {
      // Reset cuando cambia el workspace
      setLogs([])
      setHasLoadedHistorical(false)
      sessionStartTime.current = null
    }
  }, [historicalLogs, hasLoadedHistorical, currentWorkspace, convertHistoricalLog])

  // Generar ID único para cada log
  const generateLogId = useCallback(() => {
    return `log-${Date.now()}-${++logIdCounter.current}`
  }, [])

  // Agregar log manteniendo máximo de 1000
  const addLog = useCallback((log: RealTimeLog) => {
    if (isPaused) return

    setLogs(prev => {
      const newLogs = [...prev, log]
      // Mantener solo los últimos MAX_LOGS
      return newLogs.slice(-MAX_LOGS)
    })
  }, [isPaused])

  // Handler para backend_log
  const handleBackendLog = useCallback((event: WebSocketLogEvent) => {
    const log: RealTimeLog = {
      id: generateLogId(),
      source: 'BACKEND',
      level: (event.level || 'INFO') as LogLevel,
      message: event.message || '',
      timestamp: new Date(event.timestamp * 1000),
      taskId: event.taskId,
      workspaceId: event.workspaceId
    }
    addLog(log)
  }, [generateLogId, addLog])

  // Handler para celery_log
  const handleCeleryLog = useCallback((event: WebSocketLogEvent) => {
    const log: RealTimeLog = {
      id: generateLogId(),
      source: 'CELERY',
      level: (event.level || 'INFO') as LogLevel,
      message: event.message || '',
      timestamp: new Date(event.timestamp * 1000),
      taskId: event.taskId,
      workspaceId: event.workspaceId
    }
    addLog(log)
  }, [generateLogId, addLog])

  // Handler para tool_log
  const handleToolLog = useCallback((event: WebSocketLogEvent) => {
    const log: RealTimeLog = {
      id: generateLogId(),
      source: (event.source || 'TOOL') as LogSource,
      level: (event.level || 'INFO') as LogLevel,
      message: event.message || '',
      timestamp: new Date(event.timestamp * 1000),
      raw: event.command, // Comando completo para mostrar
      taskId: event.taskId,
      workspaceId: event.workspaceId
    }
    addLog(log)
  }, [generateLogId, addLog])

  // Conectar a WebSocket cuando esté disponible
  useEffect(() => {
    if (!socket || !isConnected || !currentWorkspace) return

    const workspaceId = currentWorkspace.id
    joinWorkspace(workspaceId)

    // Registrar listeners
    socket.on('backend_log', handleBackendLog)
    socket.on('celery_log', handleCeleryLog)
    socket.on('tool_log', handleToolLog)

    return () => {
      socket.off('backend_log', handleBackendLog)
      socket.off('celery_log', handleCeleryLog)
      socket.off('tool_log', handleToolLog)
      leaveWorkspace(workspaceId)
    }
  }, [socket, isConnected, currentWorkspace, joinWorkspace, leaveWorkspace, handleBackendLog, handleCeleryLog, handleToolLog])

  // Reset cuando cambia el workspace
  useEffect(() => {
    setHasLoadedHistorical(false)
    setLogs([])
    sessionStartTime.current = null
  }, [currentWorkspace?.id])

  // Limpiar logs
  const clearLogs = useCallback(() => {
    setLogs([])
  }, [])

  return {
    logs,
    isPaused,
    setIsPaused,
    clearLogs,
    isConnected,
    isLoadingHistorical,
    hasLoadedHistorical
  }
}

