import React, { useState, useRef, useEffect } from 'react'
import {
  Terminal,
  Minimize2,
  Maximize2,
  X,
  Play,
  Square,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
  Command,
  Trash2,
  ChevronUp,
  ChevronDown,
  Settings
} from 'lucide-react'
import { useConsole } from '../contexts/ConsoleContext'
import { cn } from '../lib/utils'

interface FloatingConsoleProps {
  className?: string
}

const FloatingConsole: React.FC<FloatingConsoleProps> = ({ className }) => {
  const {
    tasks,
    logs,
    isConsoleOpen,
    consoleSize,
    toggleConsole,
    toggleConsoleSmart,
    setConsoleSize,
    completeTask,
    failTask,
    cancelTask,
    clearLogs,
    clearCompletedTasks
  } = useConsole()

  const [position, setPosition] = useState({ x: 20, y: 20 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const consoleRef = useRef<HTMLDivElement>(null)
  const logsEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll a los logs más recientes
  useEffect(() => {
    if (logsEndRef.current && consoleSize === 'full') {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, consoleSize])

  // Manejo del drag
  const handleMouseDown = (e: React.MouseEvent) => {
    if (consoleSize !== 'full') {
      setIsDragging(true)
      setDragStart({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      })
    }
  }

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging) {
        setPosition({
          x: e.clientX - dragStart.x,
          y: e.clientY - dragStart.y
        })
      }
    }

    const handleMouseUp = () => {
      setIsDragging(false)
    }

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging, dragStart])

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'error':
        return <XCircle className="w-4 h-4 text-red-400" />
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />
      case 'command':
        return <Command className="w-4 h-4 text-blue-400" />
      case 'info':
      default:
        return <Info className="w-4 h-4 text-cyan-400" />
    }
  }

  const getTaskStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-400" />
      case 'cancelled':
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />
      default:
        return <div className="w-2 h-2 bg-gray-400 rounded-full" />
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('es-ES', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getConsoleSize = () => {
    switch (consoleSize) {
      case 'minimized':
        return { width: '300px', height: '40px' }
      case 'compact':
        return { width: '500px', height: '200px' }
      case 'full':
        return { width: '800px', height: '500px' }
    }
  }

  const runningTasks = tasks.filter(t => t.status === 'running')
  const hasActivity = runningTasks.length > 0 || logs.length > 0

  if (!isConsoleOpen) {
    return (
      <button
        onClick={toggleConsoleSmart}
        className={cn(
          "fixed bottom-4 right-4 z-50 p-3 rounded-full shadow-lg transition-all duration-200",
          hasActivity
            ? "bg-cyan-500 hover:bg-cyan-600 text-black animate-pulse"
            : "bg-gray-800 hover:bg-gray-700 text-cyan-400"
        )}
        title={hasActivity ? "Ver progreso de tareas" : "Abrir consola de tareas"}
      >
        <Terminal className="w-6 h-6" />
        {runningTasks.length > 0 && (
          <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center animate-bounce">
            {runningTasks.length}
          </span>
        )}
      </button>
    )
  }

  const size = getConsoleSize()

  return (
    <div
      ref={consoleRef}
      className={cn(
        "fixed z-50 bg-gray-900 border border-cyan-500 rounded-lg shadow-2xl overflow-hidden",
        "backdrop-blur-sm bg-opacity-95",
        isDragging && "cursor-move"
      )}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        width: size.width,
        height: size.height,
        boxShadow: '0 0 30px rgba(34, 211, 238, 0.3)'
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between p-3 bg-gray-800 border-b border-cyan-500 cursor-move"
        onMouseDown={handleMouseDown}
      >
        <div className="flex items-center space-x-2">
          <Terminal className="w-5 h-5 text-cyan-400" />
          <span className="text-sm font-medium text-cyan-400">
            Console
          </span>
          {runningTasks.length > 0 && (
            <span className="text-xs bg-cyan-500 text-black px-2 py-0.5 rounded-full">
              {runningTasks.length} running
            </span>
          )}
        </div>

        <div className="flex items-center space-x-1">
          {/* Controles de tamaño */}
          {consoleSize !== 'minimized' && (
            <button
              onClick={() => setConsoleSize(consoleSize === 'compact' ? 'full' : 'compact')}
              className="p-1 text-gray-400 hover:text-cyan-400 transition-colors"
              title={consoleSize === 'compact' ? 'Maximizar' : 'Compactar'}
            >
              {consoleSize === 'compact' ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
            </button>
          )}

          {consoleSize === 'full' && (
            <button
              onClick={() => setConsoleSize('compact')}
              className="p-1 text-gray-400 hover:text-cyan-400 transition-colors"
              title="Compactar"
            >
              <ChevronDown className="w-4 h-4" />
            </button>
          )}

          <button
            onClick={toggleConsole}
            className="p-1 text-gray-400 hover:text-red-400 transition-colors"
            title="Cerrar consola"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Contenido */}
      <div className="flex flex-col h-full">
        {/* Tareas activas */}
        {consoleSize !== 'minimized' && runningTasks.length > 0 && (
          <div className="p-3 border-b border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-cyan-400">Tareas Activas</h4>
              <button
                onClick={clearCompletedTasks}
                className="text-xs text-gray-400 hover:text-red-400"
                title="Limpiar completadas"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
            <div className="space-y-2">
              {runningTasks.map((task) => (
                <div key={task.id} className="flex items-center justify-between bg-gray-800 p-2 rounded">
                  <div className="flex items-center space-x-2 flex-1 min-w-0">
                    {getTaskStatusIcon(task.status)}
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-white truncate">{task.name}</p>
                      <p className="text-xs text-gray-400">{task.module}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-gray-700 rounded-full h-1">
                      <div
                        className="bg-cyan-500 h-1 rounded-full transition-all duration-300"
                        style={{ width: `${task.progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-cyan-400 w-8">{task.progress}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Logs */}
        {consoleSize !== 'minimized' && (
          <div className="flex-1 overflow-hidden">
            <div className="flex items-center justify-between p-3 border-b border-gray-700">
              <h4 className="text-sm font-medium text-cyan-400">Logs</h4>
              <div className="flex items-center space-x-1">
                <button
                  onClick={clearLogs}
                  className="text-xs text-gray-400 hover:text-red-400"
                  title="Limpiar logs"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            </div>

            <div className="h-full overflow-y-auto p-3 space-y-1 font-mono text-xs">
              {logs.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <Terminal className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No hay actividad reciente</p>
                </div>
              ) : (
                logs.slice(0, consoleSize === 'compact' ? 20 : 100).map((log) => (
                  <div key={log.id} className="flex items-start space-x-2 group">
                    <span className="text-gray-500 flex-shrink-0 w-12">
                      {formatTime(log.timestamp)}
                    </span>
                    <div className="flex items-center space-x-1 flex-shrink-0">
                      {getLogIcon(log.level)}
                    </div>
                    <span className="text-gray-400 flex-shrink-0 w-12">
                      [{log.module}]
                    </span>
                    <span className={cn(
                      "flex-1 break-all",
                      log.level === 'error' && "text-red-400",
                      log.level === 'success' && "text-green-400",
                      log.level === 'warning' && "text-yellow-400",
                      log.level === 'command' && "text-blue-400",
                      log.level === 'info' && "text-cyan-400"
                    )}>
                      {log.command && (
                        <span className="text-blue-300 font-medium">$ {log.command}</span>
                      )}
                      {log.command ? ' ' : ''}{log.message}
                    </span>
                  </div>
                ))
              )}
              <div ref={logsEndRef} />
            </div>
          </div>
        )}
      </div>

      {/* Minimized view */}
      {consoleSize === 'minimized' && (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <Terminal className="w-6 h-6 text-cyan-400 mx-auto mb-1" />
            {runningTasks.length > 0 && (
              <div className="text-xs text-cyan-400">
                {runningTasks.length} tarea{runningTasks.length !== 1 ? 's' : ''} activa{runningTasks.length !== 1 ? 's' : ''}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default FloatingConsole