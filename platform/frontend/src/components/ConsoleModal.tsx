import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Terminal, Send, X, Play, Square, RotateCcw, Trash2, Settings, Minimize2, Maximize2 } from 'lucide-react'
import { useWindowManager } from '../contexts/WindowManagerContext'
import { api } from '../lib/api/shared/client'

interface ConsoleMessage {
  type: 'welcome' | 'command_start' | 'stdout' | 'stderr' | 'command_end' | 'error'
  message?: string
  line?: string
  command?: string
  returncode?: number
  progress?: number
  timestamp: string
}

interface ConsoleModalProps {
  isOpen: boolean
  onClose: () => void
}

const ConsoleModal: React.FC<ConsoleModalProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<ConsoleMessage[]>([])
  const [command, setCommand] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const abortControllerRef = useRef<AbortController | null>(null)
  const { getZIndex, bringToFront } = useWindowManager()
  const windowId = 'console-modal'

  // Estados para drag & resize
  const [isDragging, setIsDragging] = useState(false)
  const [isResizing, setIsResizing] = useState(false)
  const [position, setPosition] = useState({ x: 50, y: 50 })
  const [size, setSize] = useState({ width: 1000, height: 600 })
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0 })

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const modalRef = useRef<HTMLDivElement>(null)

  // Auto-scroll a mensajes nuevos
  useEffect(() => {
    if (messagesEndRef.current && !isMinimized) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isMinimized])

  // Inicializar consola cuando se abre
  useEffect(() => {
    if (isOpen) {
      setIsConnected(true)
      addMessage({
        type: 'welcome',
        message: '🖥️ Cybersecurity Console Ready',
        timestamp: new Date().toISOString()
      })
    }
  }, [isOpen])

  // Reset cuando se cierra
  useEffect(() => {
    if (!isOpen) {
      setMessages([])
      setCommand('')
      setIsConnected(false)
      setIsRunning(false)
      setIsMinimized(false)
    }
  }, [isOpen])

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
      const newWidth = Math.max(800, resizeStart.width + (e.clientX - resizeStart.x))
      const newHeight = Math.max(400, resizeStart.height + (e.clientY - resizeStart.y))

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

  const addMessage = (message: ConsoleMessage) => {
    setMessages(prev => [...prev, message])
  }

  const cancelCommand = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setIsRunning(false)
    addMessage({
      type: 'error',
      message: '❌ Comando cancelado por el usuario',
      timestamp: new Date().toISOString()
    })
  }

  const sendCommand = async () => {
    if (!command.trim() || isRunning) {
      return
    }

    const commandToExecute = command.trim()
    setCommand('')
    setIsRunning(true)

    // Crear AbortController para poder cancelar
    abortControllerRef.current = new AbortController()

    // Mostrar comando que se va a ejecutar
    addMessage({
      type: 'command_start',
      command: commandToExecute,
      timestamp: new Date().toISOString()
    })

    try {
      const response = await api.post('/system/console/execute', {
        command: commandToExecute
      }, {
        signal: abortControllerRef.current.signal
      })

      const data = response.data

      if (data.success) {
        // Mostrar output línea por línea
        if (data.output) {
          const lines = data.output.split('\n').filter((line: string) => line.trim())
          lines.forEach((line: string) => {
            addMessage({
              type: 'stdout',
              line: line,
              timestamp: new Date().toISOString()
            })
          })
        }

        // Mostrar errores si hay
        if (data.error) {
          addMessage({
            type: 'stderr',
            message: data.error,
            timestamp: new Date().toISOString()
          })
        }

        // Mostrar fin de comando
        addMessage({
          type: 'command_end',
          returncode: data.returncode,
          timestamp: new Date().toISOString()
        })
      } else {
        addMessage({
          type: 'error',
          message: data.error || 'Error ejecutando comando',
          timestamp: new Date().toISOString()
        })
      }
    } catch (error: any) {
      // Si fue cancelado, no mostrar error
      if (error.name === 'CanceledError' || error.message === 'canceled') {
        return
      }
      const errorMessage = error.response?.data?.error || error.message || 'Error de conexión'
      addMessage({
        type: 'error',
        message: `❌ ${errorMessage}`,
        timestamp: new Date().toISOString()
      })
    } finally {
      setIsRunning(false)
      abortControllerRef.current = null
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendCommand()
    } else if (e.key === 'Escape') {
      onClose()
    }
  }

  const clearConsole = () => {
    setMessages([])
  }

  const reconnect = () => {
    setIsConnected(true)
    addMessage({
      type: 'welcome',
      message: '🖥️ Cybersecurity Console Reconnected',
      timestamp: new Date().toISOString()
    })
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('es-ES', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'welcome':
        return '🖥️'
      case 'command_start':
        return '▶️'
      case 'stdout':
        return '📄'
      case 'stderr':
        return '⚠️'
      case 'command_end':
        return '✅'
      case 'error':
        return '❌'
      default:
        return '💬'
    }
  }

  const getMessageColor = (type: string) => {
    switch (type) {
      case 'welcome':
        return 'text-cyan-400'
      case 'command_start':
        return 'text-blue-400'
      case 'stdout':
        return 'text-gray-900'
      case 'stderr':
        return 'text-yellow-400'
      case 'command_end':
        return 'text-gray-700'
      case 'error':
        return 'text-red-400'
      default:
        return 'text-gray-600'
    }
  }

  if (!isOpen) return null

  // Calcular contenido basado en el estado de minimización
  const renderContent = () => {
    if (isMinimized) {
      return (
        <div className="flex-1 flex items-center justify-center cursor-pointer" onClick={() => setIsMinimized(false)}>
          <div className="text-center">
            <Terminal className="w-6 h-6 text-cyan-400 mx-auto mb-1" />
            {isRunning && (
              <div className="text-xs text-blue-400">
                Ejecutando comando...
              </div>
            )}
            {messages.length > 0 && (
              <div className="text-xs text-gray-500">
                {messages.length} mensajes
              </div>
            )}
          </div>
        </div>
      )
    }

    return (
      <div className="flex flex-col" style={{ height: 'calc(100% - 48px)' }}>
        {/* Área de mensajes con scroll */}
        <div className="flex-1 overflow-y-auto p-4 space-y-1 bg-gray-50" style={{ minHeight: 0, overflowX: 'hidden' }}>
          {messages.length === 0 ? (
            <div className="text-center py-20 text-gray-500">
              <Terminal className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg mb-2">Consola lista</p>
              <p className="text-sm">Ingresa comandos para ejecutar...</p>
              <div className="mt-4 text-xs space-y-1">
                <p>💡 <strong>Comandos útiles:</strong></p>
                <p><code className="bg-white px-2 py-1 rounded">nmap -sV -p 80,443 example.com</code></p>
                <p><code className="bg-white px-2 py-1 rounded">whois example.com</code></p>
                <p><code className="bg-white px-2 py-1 rounded">dig example.com</code></p>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex items-start space-x-3 p-2 rounded ${
                  message.type === 'error' ? 'bg-red-900/20 border border-red-500/30' :
                  message.type === 'stderr' ? 'bg-yellow-900/20 border border-yellow-500/30' :
                  'hover:bg-white/50'
                }`}
              >
                <span className="text-gray-500 text-xs flex-shrink-0 w-12">
                  {formatTimestamp(message.timestamp)}
                </span>
                <span className="text-lg flex-shrink-0">
                  {getMessageIcon(message.type)}
                </span>
                <div className="flex-1 min-w-0">
                  {message.command && (
                    <div className="text-blue-400 font-medium mb-1">
                      $ {message.command}
                    </div>
                  )}
                  <div className={`break-all ${getMessageColor(message.type)}`}>
                    {message.message || message.line}
                  </div>
                  {message.returncode !== undefined && (
                    <div className="text-xs text-gray-500 mt-1">
                      Código de salida: {message.returncode}
                    </div>
                  )}
                  {message.progress !== undefined && message.progress < 100 && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-700 rounded-full h-1">
                        <div
                          className="bg-cyan-500 h-1 rounded-full transition-all duration-300"
                          style={{ width: `${message.progress}%` }}
                        />
                      </div>
                      <span className="text-xs text-cyan-400">{message.progress}%</span>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input de comandos - Siempre visible */}
        <div className="border-t border-gray-200 bg-white p-4 flex-shrink-0">
          <div className="flex items-center space-x-3">
            <span className="text-gray-900 font-bold">$</span>
            <input
              ref={inputRef}
              type="text"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ingresa un comando (ej: nmap -sV -p 80 example.com)"
              className="flex-1 bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 font-mono"
              disabled={!isConnected}
            />
            {isRunning ? (
              <button
                onClick={cancelCommand}
                className="flex items-center space-x-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded transition-colors font-medium"
              >
                <Square className="w-4 h-4" />
                <span>Cancelar</span>
              </button>
            ) : (
              <button
                onClick={sendCommand}
                disabled={!command.trim() || !isConnected}
                className="flex items-center space-x-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 disabled:bg-gray-600 text-black rounded transition-colors font-medium"
              >
                <Send className="w-4 h-4" />
                <span>Ejecutar</span>
              </button>
            )}
          </div>

          {/* Ayuda rápida */}
          <div className="mt-2 text-xs text-gray-500 flex items-center justify-between">
            <span>
              Presiona <kbd className="bg-gray-700 px-1 rounded">Enter</kbd> para ejecutar |
              <kbd className="bg-gray-700 px-1 rounded ml-1">Escape</kbd> para cerrar
            </span>
            <span>
              Estado: {isConnected ? '🟢 Conectado' : '🔴 Desconectado'}
            </span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 z-50 bg-black bg-opacity-50 pointer-events-none">
        {/* Modal */}
        <div
          ref={modalRef}
          className="bg-gray-50 border border-cyan-500 rounded-xl shadow-2xl overflow-hidden pointer-events-auto absolute flex flex-col"
          style={{
            left: position.x,
            top: position.y,
            width: size.width,
            height: size.height,
            cursor: isDragging ? 'grabbing' : 'grab',
            zIndex: getZIndex(windowId)
          }}
          onMouseDown={handleMouseDown}
        >
          {/* Header - Draggable - Siempre visible */}
          <div className="modal-header flex items-center justify-between p-3 bg-white border-b border-cyan-500 select-none flex-shrink-0 z-20">
          <div className="flex items-center space-x-3">
            <Terminal className="w-5 h-5 text-cyan-400" />
            <h2 className="text-lg font-semibold text-cyan-400">
              Cybersecurity Console
            </h2>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
              <span className="text-sm text-gray-600">
                {isConnected ? 'Conectado' : 'Desconectado'}
              </span>
              {isRunning && (
                <>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
                  <span className="text-sm text-blue-400">Ejecutando...</span>
                </>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-1">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-1 text-gray-500 hover:text-cyan-400 transition-colors"
              title={isMinimized ? "Maximizar" : "Minimizar"}
            >
              {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
            </button>
            <button
              onClick={reconnect}
              className="p-1 text-gray-500 hover:text-cyan-400 transition-colors"
              title="Reconectar"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            {!isMinimized && (
              <button
                onClick={clearConsole}
                className="p-1 text-gray-500 hover:text-red-400 transition-colors"
                title="Limpiar consola"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1 text-gray-500 hover:text-red-400 transition-colors flex-shrink-0 z-30"
              title="Cerrar"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Contenido - Flex container - Siempre visible */}
        <div className="flex flex-col flex-1 min-h-0 overflow-hidden" style={{ height: `calc(100% - 48px)` }}>
          {renderContent()}
        </div>

        {/* Resize Handle */}
        <div
          className="absolute bottom-0 right-0 w-4 h-4 cursor-nw-resize"
          onMouseDown={handleResizeMouseDown}
        >
          <div className="w-full h-full bg-cyan-500 rounded-tl opacity-50 hover:opacity-100 transition-opacity" />
        </div>
      </div>
    </div>
  </>
  )
}

export default ConsoleModal



