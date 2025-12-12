/**
 * SystemMonitor Component
 * =======================
 * 
 * Consola de logs en tiempo real para monitorear procesos de la aplicación.
 * 
 * Características:
 * - Logs en tiempo real vía WebSocket
 * - Filtrado avanzado (fuentes, niveles, búsqueda)
 * - Tabs para categorizar logs (Unified, Backend, Celery, Tools)
 * - Auto-scroll inteligente
 * - Drag & resize como MonitoringConsole
 * - Look & feel idéntico al MonitoringConsole actual
 * 
 * Estructura:
 * - Header: Título y badge de tareas activas
 * - Tabs: Unified | Backend | Celery | Tools
 * - Filters: Fuentes, niveles, búsqueda, acciones
 * - LogViewer: Área de logs con formato [SOURCE] HH:MM:SS LEVEL mensaje
 * - Footer: Usuario, estado, conexión WebSocket
 */

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { useWindowManager } from '../../contexts/WindowManagerContext'
import { useConsole } from '../../contexts/ConsoleContext'
import { useSystemMonitorLogs } from '../../hooks/useSystemMonitorLogs'
import { useSystemMonitorFilters } from '../../hooks/useSystemMonitorFilters'
import { SystemMonitorHeader } from './SystemMonitorHeader'
import { SystemMonitorTabs } from './SystemMonitorTabs'
import { SystemMonitorFilters } from './SystemMonitorFilters'
import { SystemMonitorLogViewer } from './SystemMonitorLogViewer'
import { SystemMonitorFooter } from './SystemMonitorFooter'
import { ClearLogsModal } from './ClearLogsModal'
import { useWorkspace } from '../../contexts/WorkspaceContext'
import { useMutation } from '@tanstack/react-query'
import { workspacesAPI } from '../../lib/api/workspaces/workspaces'

interface SystemMonitorProps {
  isOpen: boolean
  onClose: () => void
  className?: string
}

export const SystemMonitor: React.FC<SystemMonitorProps> = ({
  isOpen,
  onClose,
  className = ''
}) => {
  const { user } = useAuth()
  const { tasks } = useConsole()
  const { getZIndex, bringToFront } = useWindowManager()
  const windowId = 'system-monitor'

  // Estados de UI
  const [isMinimized, setIsMinimized] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)

  // Estados para drag & resize (igual que MonitoringConsole)
  const [isDragging, setIsDragging] = useState(false)
  const [isResizing, setIsResizing] = useState(false)
  const [position, setPosition] = useState({ x: 200, y: 200 })
  const [size, setSize] = useState({ width: 1200, height: 700 })
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0 })

  const modalRef = useRef<HTMLDivElement>(null)

  // Hooks de logs y filtros
  const { logs, isPaused, setIsPaused, clearLogs, isConnected } = useSystemMonitorLogs()
  const { currentWorkspace } = useWorkspace()
  const [showClearModal, setShowClearModal] = useState(false)
  const {
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
  } = useSystemMonitorFilters(logs)

  // Tareas activas
  const activeTasks = tasks.filter(task => task.status === 'running')

  // Función para iniciar el drag
  const handleMouseDown = (e: React.MouseEvent) => {
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
  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isDragging) {
      const newX = e.clientX - dragStart.x
      const newY = e.clientY - dragStart.y
      const maxX = window.innerWidth - size.width
      const maxY = window.innerHeight - size.height
      setPosition({
        x: Math.max(0, Math.min(newX, maxX)),
        y: Math.max(0, Math.min(newY, maxY))
      })
    }
    if (isResizing) {
      const newWidth = Math.max(800, Math.min(resizeStart.width + (e.clientX - resizeStart.x), window.innerWidth - 50))
      const newHeight = Math.max(400, Math.min(resizeStart.height + (e.clientY - resizeStart.y), window.innerHeight - 50))
      setSize({ width: newWidth, height: newHeight })
    }
  }, [isDragging, isResizing, dragStart, resizeStart, size.width, size.height])

  // Función para terminar el drag/resize
  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
    setIsResizing(false)
  }, [])

  // Efectos para agregar/remover event listeners
  useEffect(() => {
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

  // Exportar logs usando API
  const exportMutation = useMutation({
    mutationFn: async (format: 'json' | 'txt') => {
      if (!currentWorkspace?.id) return
      return await workspacesAPI.exportWorkspaceLogs(currentWorkspace.id, format)
    },
    onSuccess: (blob, format) => {
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const extension = format === 'json' ? 'json' : 'txt'
      a.download = `workspace_${currentWorkspace?.id}_logs_${new Date().toISOString().split('T')[0]}.${extension}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
  })

  const handleExport = () => {
    exportMutation.mutate('json')
  }

  const handleClearLogs = () => {
    setShowClearModal(true)
  }

  // Handler para cambio de scroll
  const handleScrollChange = (isAtBottom: boolean) => {
    setAutoScroll(isAtBottom)
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
        {/* Header */}
        <SystemMonitorHeader
          activeTasksCount={activeTasks.length}
          isMinimized={isMinimized}
          onMinimize={() => setIsMinimized(!isMinimized)}
          onClose={onClose}
          onClearLogs={handleClearLogs}
          onExportLogs={handleExport}
          totalLogsCount={filteredLogs.length}
        />

        {!isMinimized && (
          <div className="flex flex-col h-[calc(100%-48px)]">
            {/* Tabs */}
            <SystemMonitorTabs
              activeTab={activeTab}
              onTabChange={setActiveTab}
            />

            {/* Filters */}
            <SystemMonitorFilters
              sourceFilters={sourceFilters}
              levelFilters={levelFilters}
              searchQuery={searchQuery}
              isPaused={isPaused}
              onToggleSource={toggleSourceFilter}
              onToggleLevel={toggleLevelFilter}
              onSearchChange={setSearchQuery}
              onTogglePause={() => setIsPaused(!isPaused)}
              onClear={clearLogs}
              onExport={handleExport}
            />

            {/* Log Viewer */}
            <SystemMonitorLogViewer
              logs={filteredLogs}
              autoScroll={autoScroll}
              onScrollChange={handleScrollChange}
            />

            {/* Footer */}
            <SystemMonitorFooter
              username={user?.username}
              activeTasksCount={activeTasks.length}
              totalLogs={filteredLogs.length}
              isConnected={isConnected}
            />
          </div>
        )}

        {/* Resize Handle */}
        <div
          className="absolute bottom-0 right-0 w-6 h-6 cursor-nw-resize z-10"
          onMouseDown={handleResizeMouseDown}
        >
          <div className="w-full h-full bg-green-500 rounded-tl opacity-70 hover:opacity-100 transition-opacity border-t-2 border-r-2 border-green-400" />
        </div>
      </div>

      {/* Modal de limpiar logs */}
      <ClearLogsModal
        isOpen={showClearModal}
        onClose={() => setShowClearModal(false)}
        onClear={clearLogs}
      />
    </div>
  )
}

export default SystemMonitor

