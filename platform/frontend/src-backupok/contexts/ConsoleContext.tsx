import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { useWorkspace } from './WorkspaceContext'

export type LogLevel = 'info' | 'success' | 'warning' | 'error' | 'command'

export interface ConsoleLog {
  id: string
  timestamp: Date
  level: LogLevel
  module: string
  message: string
  command?: string
  progress?: number
  duration?: number
  taskId?: string
  workspaceId?: number
}

export interface Task {
  id: string
  name: string
  module: string
  status: 'running' | 'completed' | 'failed' | 'cancelled'
  startTime: Date
  endTime?: Date
  progress: number
  logs: ConsoleLog[]
  command?: string
  target?: string
  session_id?: string
  workspaceId?: number
}

export interface TechnicalLog {
  id: string
  timestamp: Date
  level: LogLevel
  module: string
  operation: string
  message: string
  details: Record<string, any>
  taskId?: string
  workspaceId?: number
}

interface ConsoleContextType {
  // Estado
  tasks: Task[]
  logs: ConsoleLog[]
  technicalLogs: TechnicalLog[]
  isConsoleOpen: boolean
  consoleSize: 'minimized' | 'compact' | 'full'

  // Acciones
  toggleConsole: () => void
  toggleConsoleSmart: () => void
  setConsoleSize: (size: 'minimized' | 'compact' | 'full') => void

  // Funciones para reportar progreso
  startTask: (name: string, module: string, command?: string, target?: string) => string
  updateTask: (taskId: string, updates: Partial<Task>) => void
  updateTaskProgress: (taskId: string, progress: number, message?: string) => void
  completeTask: (taskId: string, message?: string) => void
  failTask: (taskId: string, error?: string) => void
  killTask: (taskId: string) => void

  // Logging mejorado
  addLog: (
    level: LogLevel,
    module: string,
    message: string,
    taskId?: string,
    command?: string,
    additionalData?: Record<string, any>
  ) => void

  // Logging avanzado para operaciones complejas
  addDetailedLog: (
    level: LogLevel,
    module: string,
    operation: string,
    message: string,
    taskId?: string,
    details?: {
      target?: string
      command?: string
      progress?: number
      duration?: number
      data?: Record<string, any>
    }
  ) => void

  // Logging técnico especializado
  addTechnicalLog: (
    level: LogLevel,
    module: string,
    operation: string,
    message: string,
    details: Record<string, any>,
    taskId?: string
  ) => void
  failTask: (taskId: string, error: string) => void
  cancelTask: (taskId: string) => void
  killTask: (taskId: string) => void

  // Logging
  addLog: (level: LogLevel, module: string, message: string, taskId?: string, command?: string) => void

  // Limpieza
  clearLogs: () => void
  clearCompletedTasks: () => void
  resetConsole: () => void
}

const ConsoleContext = createContext<ConsoleContextType | undefined>(undefined)

export const ConsoleProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { currentWorkspace } = useWorkspace()
  const [allTasks, setAllTasks] = useState<Task[]>([])
  const [allLogs, setAllLogs] = useState<ConsoleLog[]>([])
  const [allTechnicalLogs, setAllTechnicalLogs] = useState<TechnicalLog[]>([])
  const [isConsoleOpen, setIsConsoleOpen] = useState(false)
  const [consoleSize, setConsoleSize] = useState<'minimized' | 'compact' | 'full'>('compact')

  // Filtrar datos por workspace actual
  const tasks = allTasks.filter(task => task.workspaceId === currentWorkspace?.id)
  const logs = allLogs.filter(log => log.workspaceId === currentWorkspace?.id)
  const technicalLogs = allTechnicalLogs.filter(log => log.workspaceId === currentWorkspace?.id)

  // Limitar logs para performance
  const MAX_LOGS = 1000
  const MAX_TASKS = 50

  const addLog = useCallback((
    level: LogLevel,
    module: string,
    message: string,
    taskId?: string,
    command?: string,
    additionalData?: Record<string, any>
  ) => {
    const newLog: ConsoleLog = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
      level,
      module,
      message,
      command,
      taskId,
      workspaceId: currentWorkspace?.id
    }

    // Agregar datos adicionales al log si existen
    if (additionalData) {
      (newLog as any).additionalData = additionalData
    }

    setAllLogs(prev => {
      const updated = [newLog, ...prev]
      return updated.slice(0, MAX_LOGS) // Mantener solo los más recientes
    })

    // Log adicional a consola del navegador para debugging
    const timestamp = new Date().toLocaleTimeString()
    const logPrefix = `[${timestamp}] ${level.toUpperCase()} [${module}]`
    const logMessage = taskId ? `${logPrefix} [Task:${taskId}] ${message}` : `${logPrefix} ${message}`

    switch (level) {
      case 'error':
        console.error(logMessage, additionalData || '')
        break
      case 'warning':
        console.warn(logMessage, additionalData || '')
        break
      case 'success':
        console.log(`✅ ${logMessage}`, additionalData || '')
        break
      case 'command':
        console.log(`💻 ${logMessage}`, additionalData || '')
        break
      default:
        console.log(`ℹ️ ${logMessage}`, additionalData || '')
    }
  }, [currentWorkspace?.id])

  const updateTaskProgress = useCallback((
    taskId: string,
    progress: number,
    message?: string
  ) => {
    console.log(`📊 UPDATE TASK PROGRESS: taskId=${taskId}, progress=${progress}, message=${message || 'none'}`)

    setAllTasks(prev => prev.map(task => {
      if (task.id === taskId) {
        const updatedTask = {
          ...task,
          progress: Math.min(100, Math.max(0, progress))
        }

        console.log(`✅ TASK UPDATED: ${taskId} -> progress: ${updatedTask.progress}%`)

        if (message) {
          addLog('info', task.module, message, taskId)
        }

        return updatedTask
      }
      return task
    }))
  }, [addLog])

  const addDetailedLog = useCallback((
    level: LogLevel,
    module: string,
    operation: string,
    message: string,
    taskId?: string,
    details?: {
      target?: string
      command?: string
      progress?: number
      duration?: number
      data?: Record<string, any>
    }
  ) => {
    const timestamp = new Date()
    const logId = Date.now().toString() + Math.random().toString(36).substr(2, 9)

    // Crear log principal
    const mainLog: ConsoleLog = {
      id: logId,
      timestamp,
      level,
      module,
      message: `[${operation}] ${message}`,
      command: details?.command,
      progress: details?.progress,
      duration: details?.duration,
      taskId,
      workspaceId: currentWorkspace?.id
    }

    // Agregar datos adicionales
    if (details?.data) {
      (mainLog as any).additionalData = details.data
    }

    setAllLogs(prev => [mainLog, ...prev].slice(0, MAX_LOGS))

    // Logging detallado a consola del navegador
    const timeStr = timestamp.toLocaleTimeString()
    const prefix = `[${timeStr}] ${level.toUpperCase()} [${module}:${operation}]`
    const detailInfo = details ? {
      target: details.target,
      progress: details.progress,
      duration: details.duration,
      ...details.data
    } : undefined

    const consoleMessage = `${prefix} ${message}`
    const consoleDetails = detailInfo ? ` | Details: ${JSON.stringify(detailInfo, null, 2)}` : ''

    switch (level) {
      case 'error':
        console.error(consoleMessage + consoleDetails)
        break
      case 'warning':
        console.warn(consoleMessage + consoleDetails)
        break
      case 'success':
        console.log(`✅ ${consoleMessage}`, detailInfo || '')
        break
      case 'command':
        console.log(`💻 ${consoleMessage}`, detailInfo || '')
        break
      default:
        console.log(`ℹ️ ${consoleMessage}`, detailInfo || '')
    }

    // Si hay progreso, actualizar la tarea correspondiente
    if (details?.progress !== undefined && taskId) {
      updateTaskProgress(taskId, details.progress, message)
    }

    // Crear log técnico adicional
    const technicalLog: TechnicalLog = {
      id: logId + '_tech',
      timestamp,
      level,
      module,
      operation,
      message,
      details: {
        target: details?.target,
        command: details?.command,
        progress: details?.progress,
        duration: details?.duration,
        ...details?.data
      },
      taskId,
      workspaceId: currentWorkspace?.id
    }

    setAllTechnicalLogs(prev => {
      const updated = [technicalLog, ...prev]
      return updated.slice(0, MAX_LOGS) // Mantener solo los más recientes
    })
  }, [currentWorkspace?.id, updateTaskProgress])

  const addTechnicalLog = useCallback((
    level: LogLevel,
    module: string,
    operation: string,
    message: string,
    details: Record<string, any>,
    taskId?: string
  ) => {
    const timestamp = new Date()
    const logId = Date.now().toString() + Math.random().toString(36).substr(2, 9)

    const technicalLog: TechnicalLog = {
      id: logId,
      timestamp,
      level,
      module,
      operation,
      message,
      details,
      taskId,
      workspaceId: currentWorkspace?.id
    }

    setAllTechnicalLogs(prev => {
      const updated = [technicalLog, ...prev]
      return updated.slice(0, MAX_LOGS)
    })

    // Logging técnico detallado a consola
    const timeStr = timestamp.toLocaleTimeString()
    const prefix = `[${timeStr}] TECH-${level.toUpperCase()} [${module}:${operation}]`
    console.log(`${prefix} ${message}`, details)
  }, [currentWorkspace?.id])

  const startTask = useCallback((
    name: string,
    module: string,
    command?: string,
    target?: string
  ): string => {
    const taskId = Date.now().toString() + Math.random().toString(36).substr(2, 9)


    const newTask: Task = {
      id: taskId,
      name,
      module,
      status: 'running',
      startTime: new Date(),
      progress: 0,
      logs: [],
      command,
      target,
      workspaceId: currentWorkspace?.id
    }

    setAllTasks(prev => {
      const updated = [newTask, ...prev]
      return updated.slice(0, MAX_TASKS)
    })

    // ABRIR TERMINAL REAL cuando se ejecuta un comando del sistema
    if (command && typeof window !== 'undefined') {
      // Abrir nueva ventana con la terminal real
      const terminalWindow = window.open(
        `${window.location.origin}/terminal`,
        'CybersecurityTerminal',
        'width=800,height=600,scrollbars=yes,resizable=yes'
      )

      if (terminalWindow) {
        // Enfocar la nueva ventana
        terminalWindow.focus()

        // Notificar que se abrió la terminal
        console.log('🖥️ Terminal real abierta automáticamente para ejecutar comando')
      }
    } else {
      // Para tareas sin comando, abrir consola flotante
      setIsConsoleOpen(true)
    }

    // Log de inicio
    addLog('info', module, `Iniciando tarea: ${name}`, taskId, command)

    if (target) {
      addLog('info', module, `Target: ${target}`, taskId)
    }

    return taskId
  }, [addLog])

  const updateTask = useCallback((
    taskId: string,
    updates: Partial<Task>
  ) => {
    setAllTasks(prev => prev.map(task => {
      if (task.id === taskId) {
        return { ...task, ...updates }
      }
      return task
    }))
  }, [])

  const completeTask = useCallback((taskId: string, message?: string) => {
    setAllTasks(prev => prev.map(task => {
      if (task.id === taskId) {
        const completedTask = {
          ...task,
          status: 'completed' as const,
          progress: 100,
          endTime: new Date()
        }

        // Calcular duración
        const duration = completedTask.endTime.getTime() - task.startTime.getTime()

        // Log de completado
        addLog('success', task.module, `✅ ${message || `Tarea completada: ${task.name}`}`, taskId)
        addLog('info', task.module, `⏱️ Duración: ${Math.round(duration / 1000)}s`, taskId)

        return completedTask
      }
      return task
    }))
  }, [addLog])

  const failTask = useCallback((taskId: string, error: string) => {
    setAllTasks(prev => prev.map(task => {
      if (task.id === taskId) {
        const failedTask = {
          ...task,
          status: 'failed' as const,
          endTime: new Date()
        }

        // Log de error
        addLog('error', task.module, `Error: ${error}`, taskId)

        return failedTask
      }
      return task
    }))
  }, [addLog])

  const cancelTask = useCallback((taskId: string) => {
    setAllTasks(prev => prev.map(task => {
      if (task.id === taskId) {
        const cancelledTask = {
          ...task,
          status: 'cancelled' as const,
          endTime: new Date()
        }

        // Log de cancelación
        addLog('warning', task.module, `🚫 Tarea cancelada: ${task.name}`, taskId)

        return cancelledTask
      }
      return task
    }))
  }, [addLog])

  const killTask = useCallback((taskId: string) => {
    setAllTasks(prev => prev.map(task => {
      if (task.id === taskId) {
        const killedTask = {
          ...task,
          status: 'cancelled' as const,
          endTime: new Date()
        }

        // Log de eliminación forzada
        addLog('error', task.module, `💀 Proceso terminado: ${task.name}`, taskId)

        return killedTask
      }
      return task
    }))
  }, [addLog])

  const toggleConsole = useCallback(() => {
    setIsConsoleOpen(prev => !prev)
  }, [])

  const clearLogs = useCallback(() => {
    setLogs([])
  }, [])

  const clearCompletedTasks = useCallback(() => {
    setAllTasks(prev => prev.filter(task =>
      task.status === 'running' && task.workspaceId === currentWorkspace?.id
    ))
  }, [currentWorkspace?.id])

  const resetConsole = useCallback(() => {
    console.log(`🔄 RESET CONSOLE: Iniciando reset del workspace ${currentWorkspace?.name || 'actual'}`)
    console.log('🔄 RESET CONSOLE: Tasks actuales:', tasks.length)
    console.log('🔄 RESET CONSOLE: Logs actuales:', logs.length)

    // Solo limpiar datos del workspace actual
    setAllTasks(prev => prev.filter(task => task.workspaceId !== currentWorkspace?.id))
    setAllLogs(prev => prev.filter(log => log.workspaceId !== currentWorkspace?.id))

    setIsConsoleOpen(false)
    setConsoleSize('compact')
    console.log('🔄 RESET CONSOLE: Reset completado - Datos del workspace limpiados')
  }, [currentWorkspace?.id, tasks.length, logs.length])

  // Auto-manejo de visibilidad de consola
  const runningTasksCount = tasks.filter(t => t.status === 'running').length

  // Efecto para mostrar consola automáticamente cuando hay tareas activas
  React.useEffect(() => {
    if (runningTasksCount > 0 && !isConsoleOpen) {
      setIsConsoleOpen(true)
    }
  }, [runningTasksCount, isConsoleOpen])

  // Función para toggle con lógica inteligente
  const toggleConsoleSmart = useCallback(() => {
    if (runningTasksCount > 0) {
      // Si hay tareas activas, permitir cerrar la consola
      setIsConsoleOpen(prev => !prev)
    } else {
      // Si no hay tareas activas, siempre abrir
      setIsConsoleOpen(true)
    }
  }, [runningTasksCount])

  return (
    <ConsoleContext.Provider value={{
      tasks,
      logs,
      isConsoleOpen,
      consoleSize,
      toggleConsole,
      toggleConsoleSmart,
      setConsoleSize,
      startTask,
      updateTask,
      updateTaskProgress,
      completeTask,
      failTask,
      cancelTask,
      killTask,
      addLog,
      clearLogs,
      clearCompletedTasks,
      resetConsole
    }}>
      {children}
    </ConsoleContext.Provider>
  )
}

export const useConsole = () => {
  const context = useContext(ConsoleContext)
  if (context === undefined) {
    throw new Error('useConsole must be used within a ConsoleProvider')
  }
  return context
}