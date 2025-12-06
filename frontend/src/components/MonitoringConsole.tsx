import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useConsole } from '../contexts/ConsoleContext'
import { useAuth } from '../contexts/AuthContext'
import { useWorkspace } from '../contexts/WorkspaceContext'
import { useWindowManager } from '../contexts/WindowManagerContext'
import { api } from '../lib/api/shared/client'
import {
  X,
  Play,
  Pause,
  Square,
  Trash2,
  Download,
  Filter,
  Eye,
  EyeOff,
  Settings,
  Activity,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Maximize2,
  Minimize2,
  RotateCcw
} from 'lucide-react'

interface MonitoringConsoleProps {
  isOpen: boolean
  onClose: () => void
  className?: string
}

const MonitoringConsole: React.FC<MonitoringConsoleProps> = ({
  isOpen,
  onClose,
  className = ''
}) => {
  const { tasks, logs, completeTask, failTask, cancelTask, killTask, clearLogs, clearCompletedTasks, resetConsole, startTask, updateTask, updateTaskProgress } = useConsole()
  const { user } = useAuth()
  const { currentWorkspace } = useWorkspace()
  const { getZIndex, bringToFront } = useWindowManager()
  const [isMinimized, setIsMinimized] = useState(false)
  const [autoClose, setAutoClose] = useState(false)
  const [showCompleted, setShowCompleted] = useState(true)
  const [filterLevel, setFilterLevel] = useState<string>('all')
  const [selectedTask, setSelectedTask] = useState<string | null>(null)
  const windowId = 'monitoring-console'

  // Estados para drag & resize
  const [isDragging, setIsDragging] = useState(false)
  const [isResizing, setIsResizing] = useState(false)
  const [position, setPosition] = useState({ x: 200, y: 200 })
  const [size, setSize] = useState({ width: 1100, height: 650 })
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0 })

  const logsEndRef = useRef<HTMLDivElement>(null)
  const modalRef = useRef<HTMLDivElement>(null)

  // Consultar scans en ejecución del backend para sincronizar con tareas
  const { data: runningScansData } = useQuery({
    queryKey: ['running-scans-sync', currentWorkspace?.id],
    queryFn: async () => {
      try {
        const response = await api.get<{ scans: any[], total: number }>('system/running-scans')
        return response.data
      } catch (error) {
        console.error('[MonitoringConsole] Error fetching running scans:', error)
        return { scans: [], total: 0 }
      }
    },
    enabled: isOpen && !!currentWorkspace?.id,
    refetchInterval: 5000, // Actualizar cada 5 segundos
    staleTime: 0
  })

  // Sincronizar scans del backend con tareas del frontend
  useEffect(() => {
    if (!runningScansData?.scans || !currentWorkspace?.id) return

    const backendScans = runningScansData.scans.filter(scan => scan.workspace_id === currentWorkspace.id)

    backendScans.forEach(scan => {
      // Buscar si ya existe una tarea para este scan
      const existingTask = tasks.find(t => t.session_id === String(scan.id))

      if (!existingTask) {
        // Crear nueva tarea para este scan
        const toolName = scan.tool || scan.scan_type || 'Unknown'
        const taskName = `${toolName} - ${scan.target}`
        const module = scan.scan_type || 'unknown'
        
        const taskId = startTask(taskName, module, undefined, scan.target)
        // Guardar el scan_id como session_id para poder hacer seguimiento
        updateTask(taskId, { 
          session_id: String(scan.id),
          progress: scan.progress || 0
        })
        console.log(`🔄 Sincronizado scan del backend: Scan ID ${scan.id} -> Task ID ${taskId}`)
      } else {
        // Actualizar progreso de la tarea existente
        if (existingTask.progress !== scan.progress) {
          updateTaskProgress(existingTask.id, scan.progress || 0, `Progreso: ${scan.progress}%`)
        }
      }
    })
  }, [runningScansData, currentWorkspace?.id, tasks, startTask, updateTask, updateTaskProgress])

  // Auto-scroll a logs nuevos
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  // Auto-close cuando todas las tareas terminen
  useEffect(() => {
    if (autoClose && tasks.filter(t => t.status === 'running').length === 0 && isOpen) {
      setTimeout(() => onClose(), 3000) // Esperar 3 segundos antes de cerrar
    }
  }, [tasks, autoClose, isOpen, onClose])

  // Filtrar logs por nivel
  const filteredLogs = logs.filter(log => {
    if (filterLevel === 'all') return true
    return log.level === filterLevel
  })

  // Filtrar tareas por estado
  const activeTasks = tasks.filter(task => task.status === 'running')
  const completedTasks = tasks.filter(task => task.status !== 'running')

  // Debug: mostrar tareas activas y scans del backend
  console.log('🎯 MONITORING CONSOLE DEBUG:')
  console.log('  Total tasks (frontend):', tasks.length)
  console.log('  Active tasks (frontend):', activeTasks.length)
  if (activeTasks.length > 0) {
    activeTasks.forEach(task => {
      console.log(`    - ${task.name} (${task.id}): ${task.progress}% - status: ${task.status} - session_id: ${task.session_id}`)
    })
  }
  console.log('  Backend scans:', runningScansData?.total || 0)
  if (runningScansData?.scans && runningScansData.scans.length > 0) {
    const workspaceScans = runningScansData.scans.filter(s => s.workspace_id === currentWorkspace?.id)
    console.log('  Backend scans (workspace):', workspaceScans.length)
    workspaceScans.forEach(scan => {
      console.log(`    - Scan ID ${scan.id}: ${scan.tool || scan.scan_type} - ${scan.target} - ${scan.progress}%`)
    })
  }

  const getTaskIcon = (status: string) => {
    switch (status) {
      case 'running': return <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
      case 'completed': return <span className="w-2 h-2 bg-green-400 rounded-full" />
      case 'failed': return <span className="w-2 h-2 bg-red-400 rounded-full" />
      case 'cancelled': return <span className="w-2 h-2 bg-yellow-400 rounded-full" />
      default: return <span className="w-2 h-2 bg-gray-400 rounded-full" />
    }
  }

  const getTaskColor = (status: string) => {
    switch (status) {
      case 'running': return 'border-blue-500 bg-blue-500/10'
      case 'completed': return 'border-green-500 bg-green-500/10'
      case 'failed': return 'border-red-500 bg-red-500/10'
      case 'cancelled': return 'border-yellow-500 bg-yellow-500/10'
      default: return 'border-gray-500 bg-gray-500/10'
    }
  }

  const getLogColor = (level: string) => {
    switch (level) {
      case 'error': return 'text-red-400 border-red-500/30'
      case 'warning': return 'text-yellow-400 border-yellow-500/30'
      case 'success': return 'text-green-400 border-green-500/30'
      case 'command': return 'text-blue-400 border-blue-500/30'
      default: return 'text-gray-300 border-gray-500/30'
    }
  }

  // Función para iniciar el drag
  const handleMouseDown = (e: React.MouseEvent) => {
    // Traer la ventana al frente cuando se hace click
    bringToFront(windowId)

    if (e.target === e.currentTarget || (e.target as HTMLElement).closest('.modal-header')) {
      setIsDragging(true)
      setDragStart({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      })
    }
  }

  // Función para iniciar el resize
  const handleResizeMouseDown = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsResizing(true)
    setResizeStart({
      x: e.clientX,
      y: e.clientY,
      width: size.width,
      height: size.height
    })
  }

  // Función para manejar el movimiento del mouse
  const handleMouseMove = React.useCallback((e: MouseEvent) => {
    if (isDragging) {
      const newX = e.clientX - dragStart.x
      const newY = e.clientY - dragStart.y

      // Limites para mantener la modal dentro de la pantalla
      const maxX = window.innerWidth - size.width
      const maxY = window.innerHeight - size.height

      setPosition({
        x: Math.max(0, Math.min(newX, maxX)),
        y: Math.max(0, Math.min(newY, maxY))
      })
    }

    if (isResizing) {
      const newWidth = Math.max(900, resizeStart.width + (e.clientX - resizeStart.x))
      const newHeight = Math.max(500, resizeStart.height + (e.clientY - resizeStart.y))

      setSize({
        width: newWidth,
        height: newHeight
      })
    }
  }, [isDragging, isResizing, dragStart, resizeStart, size.width, size.height])

  // Función para terminar el drag/resize
  const handleMouseUp = React.useCallback(() => {
    setIsDragging(false)
    setIsResizing(false)
  }, [])

  // Efectos para agregar/remover event listeners
  React.useEffect(() => {
    if (isDragging || isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = isDragging ? 'grabbing' : 'nw-resize'
      document.body.style.userSelect = 'none'
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
  }, [isDragging, isResizing, handleMouseMove, handleMouseUp])

  const exportLogs = () => {
    const logData = filteredLogs.map(log => ({
      timestamp: log.timestamp.toISOString(),
      level: log.level,
      module: log.module,
      message: log.message,
      command: log.command,
      taskId: log.taskId
    }))

    const blob = new Blob([JSON.stringify(logData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `cybersecurity-logs-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (!isOpen) return null

  return (
    <div className={`fixed inset-0 z-50 bg-black bg-opacity-50 pointer-events-none ${className}`}>
      <div
        ref={modalRef}
        className="bg-gray-900 border border-green-500 rounded-lg shadow-2xl pointer-events-auto"
        style={{
          position: 'absolute',
          left: position.x,
          top: position.y,
          width: size.width,
          height: size.height,
          cursor: isDragging ? 'grabbing' : 'grab',
          zIndex: getZIndex(windowId)
        }}
        onMouseDown={handleMouseDown}
      >
        {/* Header - Draggable */}
        <div className="modal-header flex items-center justify-between p-3 border-b border-green-500 bg-gray-800 rounded-t-lg select-none">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            <h3 className="text-sm font-medium text-cyan-400">Monitor de Sistema</h3>
            {activeTasks.length > 0 && (
              <span className="px-2 py-1 text-xs bg-blue-500 text-black rounded-full animate-pulse">
                {activeTasks.length} activo{activeTasks.length !== 1 ? 's' : ''}
              </span>
            )}
          </div>

          <div className="flex items-center space-x-1">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-1 text-gray-400 hover:text-cyan-400 transition-colors"
              title={isMinimized ? "Maximizar" : "Minimizar"}
            >
              {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
            </button>
            <button
              onMouseDown={onClose}
              className="p-1 text-gray-400 hover:text-red-400 transition-colors"
              title="Cerrar"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <div className="flex h-[calc(100%-48px)]">

            {/* Panel lateral - Tareas activas */}
            <div className="w-64 border-r border-green-500 bg-gray-800 p-3">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-xs font-medium text-green-400 uppercase tracking-wide">Tareas Activas</h4>
                <div className="flex space-x-1">
                  <button
                    onClick={() => setShowCompleted(!showCompleted)}
                    className={`p-1 rounded text-xs ${showCompleted ? 'text-green-400' : 'text-gray-500'}`}
                    title={showCompleted ? "Ocultar completadas" : "Mostrar completadas"}
                  >
                    {showCompleted ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                  </button>
                </div>
              </div>

              <div className="space-y-2 max-h-40 overflow-y-auto">
                {activeTasks.map(task => (
                  <div
                    key={task.id}
                    className={`p-2 rounded border cursor-pointer transition-colors ${getTaskColor(task.status)}
                      ${selectedTask === task.id ? 'ring-2 ring-cyan-400' : ''}`}
                    onClick={() => setSelectedTask(selectedTask === task.id ? null : task.id)}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center space-x-2">
                        {getTaskIcon(task.status)}
                        <span className="text-xs font-medium truncate">{task.name}</span>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          killTask(task.id)
                        }}
                        className="p-1 text-red-400 hover:text-red-300 transition-colors"
                        title="Terminar proceso"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                    <div className="text-xs text-gray-400">{task.module}</div>
                    <div className="mt-2">
                      <div className="w-full bg-gray-700 rounded-full h-1">
                        <div
                          className="bg-cyan-500 h-1 rounded-full transition-all duration-300"
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                      <span className="text-xs text-cyan-400">{task.progress}%</span>
                    </div>
                  </div>
                ))}

                {showCompleted && completedTasks.slice(0, 3).map(task => (
                  <div
                    key={task.id}
                    className={`p-2 rounded border opacity-60 ${getTaskColor(task.status)}`}
                  >
                    <div className="flex items-center space-x-2 mb-1">
                      {getTaskIcon(task.status)}
                      <span className="text-xs font-medium truncate">{task.name}</span>
                    </div>
                    <div className="text-xs text-gray-500">{task.module}</div>
                  </div>
                ))}
              </div>

              {/* Controles */}
              <div className="mt-4 space-y-2">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="autoClose"
                    checked={autoClose}
                    onChange={(e) => setAutoClose(e.target.checked)}
                    className="w-3 h-3 text-cyan-500 bg-gray-700 border-gray-600 rounded focus:ring-cyan-500"
                  />
                  <label htmlFor="autoClose" className="text-xs text-gray-400">
                    Auto-cerrar al terminar
                  </label>
                </div>
              </div>
            </div>

            {/* Panel principal - Logs */}
            <div className="flex-1 flex flex-col">

              {/* Barra de herramientas */}
              <div className="flex items-center justify-between p-3 border-b border-green-500 bg-gray-800">
                <div className="flex items-center space-x-3">
                  <select
                    value={filterLevel}
                    onChange={(e) => setFilterLevel(e.target.value)}
                    className="px-2 py-1 text-xs bg-gray-700 border border-green-500 rounded text-green-400 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                  >
                    <option value="all">Todos los logs</option>
                    <option value="info">Info</option>
                    <option value="success">Éxito</option>
                    <option value="warning">Advertencias</option>
                    <option value="error">Errores</option>
                    <option value="command">Comandos</option>
                  </select>

                  <span className="text-xs text-gray-400">
                    {filteredLogs.length} logs
                  </span>
                </div>

                <div className="flex items-center space-x-1">
                  <button
                    onClick={exportLogs}
                    className="p-1 text-gray-400 hover:text-cyan-400 transition-colors"
                    title="Exportar logs"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  <button
                    onClick={clearLogs}
                    className="p-1 text-gray-400 hover:text-red-400 transition-colors"
                    title="Limpiar logs"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (window.confirm('¿Resetear completamente la consola? Se perderán todos los logs y tareas.')) {
                        resetConsole();
                      }
                    }}
                    className="p-1 text-gray-400 hover:text-orange-400 transition-colors"
                    title="Resetear consola completa"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Área de logs */}
              <div className="flex-1 overflow-hidden">
                <div className="h-full overflow-y-auto p-3 space-y-2">
                  {filteredLogs.length === 0 ? (
                    <div className="text-center py-20 text-gray-500">
                      <Activity className="w-16 h-16 mx-auto mb-4 opacity-50" />
                      <p className="text-lg mb-2">Monitor listo</p>
                      <p className="text-sm">Los logs de ejecución aparecerán aquí</p>
                    </div>
                  ) : (
                    filteredLogs.slice(-100).map((log) => (
                      <div
                        key={log.id}
                        className={`p-3 rounded border text-sm ${getLogColor(log.level)} bg-gray-800/50`}
                      >
                        <div className="flex items-start justify-between mb-1">
                          <div className="flex items-center space-x-2">
                            <span className="text-xs font-medium uppercase tracking-wide">
                              {log.level}
                            </span>
                            <span className="text-xs text-gray-500">
                              {log.timestamp.toLocaleTimeString('es-ES', {
                                hour12: false,
                                hour: '2-digit',
                                minute: '2-digit',
                                second: '2-digit'
                              })}
                            </span>
                            <span className="text-xs text-cyan-400">
                              {log.module}
                            </span>
                          </div>
                          {log.taskId && (
                            <span className="text-xs text-gray-500">
                              Task: {log.taskId.slice(-8)}
                            </span>
                          )}
                        </div>

                        {log.command && (
                          <div className="mb-2 font-mono text-blue-400 bg-gray-900/50 p-2 rounded">
                            $ {log.command}
                          </div>
                        )}

                        <div className="text-gray-300 break-words">
                          {log.message}
                        </div>
                      </div>
                    ))
                  )}
                  <div ref={logsEndRef} />
                </div>
              </div>

              {/* Barra de estado inferior */}
              <div className="p-2 border-t border-green-500 bg-gray-800 text-xs text-gray-400 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span>Usuario: <span className="text-green-400">{user?.username}</span></span>
                  <span>•</span>
                  <span>Estado: <span className="text-cyan-400">
                    {activeTasks.length > 0 ? `${activeTasks.length} ejecutándose` : 'En espera'}
                  </span></span>
                </div>
                <div className="flex items-center space-x-2">
                  <span>Versión: Factor X v2.0</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Resize Handle */}
        <div
          className="absolute bottom-0 right-0 w-4 h-4 cursor-nw-resize"
          onMouseDown={handleResizeMouseDown}
        >
          <div className="w-full h-full bg-green-500 rounded-tl opacity-50 hover:opacity-100 transition-opacity" />
        </div>
      </div>
    </div>
  )
}

export default MonitoringConsole
