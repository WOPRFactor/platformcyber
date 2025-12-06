/**
 * RunningScansConsoleModal
 * ========================
 *
 * Consola flotante para monitorear y cancelar scans en ejecución.
 * Replica la experiencia visual de las otras consolas del sistema.
 */

import React, { useState, useEffect, useCallback } from 'react'
import { Activity, Maximize2, Minimize2, X } from 'lucide-react'
import RunningScansMonitor from './RunningScansMonitor'

interface RunningScansConsoleModalProps {
  isOpen: boolean
  onClose: () => void
}

const MIN_WIDTH = 820
const MIN_HEIGHT = 420

const RunningScansConsoleModal: React.FC<RunningScansConsoleModalProps> = ({ isOpen, onClose }) => {
  const [position, setPosition] = useState({ x: 160, y: 120 })
  const [size, setSize] = useState({ width: 960, height: 560 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const [isResizing, setIsResizing] = useState(false)
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0 })
  const [isMinimized, setIsMinimized] = useState(false)

  const handleHeaderMouseDown = (event: React.MouseEvent) => {
    setIsDragging(true)
    setDragOffset({
      x: event.clientX - position.x,
      y: event.clientY - position.y
    })
  }

  const handleResizeMouseDown = (event: React.MouseEvent) => {
    event.stopPropagation()
    setIsResizing(true)
    setResizeStart({
      x: event.clientX,
      y: event.clientY,
      width: size.width,
      height: size.height
    })
  }

  const handleMouseMove = useCallback((event: MouseEvent) => {
    if (isDragging) {
      const newX = event.clientX - dragOffset.x
      const newY = event.clientY - dragOffset.y
      const maxX = window.innerWidth - size.width
      const maxY = window.innerHeight - 80

      setPosition({
        x: Math.max(0, Math.min(newX, Math.max(0, maxX))),
        y: Math.max(40, Math.min(newY, Math.max(40, maxY)))
      })
    }

    if (isResizing) {
      const deltaX = event.clientX - resizeStart.x
      const deltaY = event.clientY - resizeStart.y

      setSize({
        width: Math.max(MIN_WIDTH, resizeStart.width + deltaX),
        height: Math.max(MIN_HEIGHT, resizeStart.height + deltaY)
      })
    }
  }, [isDragging, isResizing, dragOffset, resizeStart, size.width])

  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
    setIsResizing(false)
  }, [])

  useEffect(() => {
    if (!isOpen) return

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isOpen, handleMouseMove, handleMouseUp])

  useEffect(() => {
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }
    if (isOpen) {
      document.addEventListener('keydown', handleKey)
    }
    return () => document.removeEventListener('keydown', handleKey)
  }, [isOpen, onClose])

  if (!isOpen) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 pointer-events-none select-none">
      <div
        className="absolute pointer-events-auto bg-gray-900 border border-green-500 rounded-lg shadow-2xl flex flex-col"
        style={{
          left: position.x,
          top: position.y,
          width: size.width,
          height: isMinimized ? undefined : size.height,
          cursor: isDragging ? 'grabbing' : 'default'
        }}
      >
        {/* Header */}
        <div
          className="modal-header flex items-center justify-between px-4 py-2 border-b border-green-500 bg-gray-800 rounded-t-lg cursor-move"
          onMouseDown={handleHeaderMouseDown}
        >
          <div className="flex items-center gap-2 text-cyan-400">
            <Activity className="w-5 h-5" />
            <div>
              <p className="text-sm font-semibold leading-tight">
                Running Scans Console
              </p>
              <p className="text-[11px] text-gray-400 leading-tight">
                Control total de herramientas en ejecución
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={(event) => {
                event.stopPropagation()
                setIsMinimized(!isMinimized)
              }}
              className="p-1 text-gray-400 hover:text-cyan-300 transition-colors"
              title={isMinimized ? 'Restaurar' : 'Minimizar'}
            >
              {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
            </button>
            <button
              onClick={(event) => {
                event.stopPropagation()
                onClose()
              }}
              className="p-1 text-gray-400 hover:text-red-400 transition-colors"
              title="Cerrar consola"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            <div className="px-4 py-2 border-b border-green-500 bg-gray-800 text-xs text-gray-400 flex justify-between items-center">
              <span>
                ⚡ Supervisión en vivo de recon, scanning, vuln y post-exploitation
              </span>
              <span className="text-green-400">
                Arrastra para mover · ESC para cerrar
              </span>
            </div>

            <div className="flex-1 overflow-hidden p-4 bg-gray-900">
              <RunningScansMonitor />
            </div>
          </>
        )}

        <div
          className="absolute bottom-1 right-1 w-4 h-4 cursor-nwse-resize text-green-400 flex items-center justify-center"
          onMouseDown={handleResizeMouseDown}
          title="Redimensionar"
        >
          <div className="w-3 h-3 border-r border-b border-green-500" />
        </div>
      </div>
    </div>
  )
}

export default RunningScansConsoleModal

