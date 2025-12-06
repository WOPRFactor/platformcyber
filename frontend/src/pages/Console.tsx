import React, { useState, useEffect, useRef } from 'react'
import { Terminal, Send, X, Play, Square, RotateCcw, Trash2, Settings } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

interface ConsoleMessage {
  type: 'welcome' | 'command_start' | 'stdout' | 'stderr' | 'command_end' | 'error'
  message?: string
  line?: string
  command?: string
  returncode?: number
  progress?: number
  timestamp: string
}

// Nueva consola real como terminal de Linux
const RealTerminal: React.FC = () => {
  const { user } = useAuth()
  const [output, setOutput] = useState<string[]>([])
  const [currentCommand, setCurrentCommand] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const terminalRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    terminalRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [output])

  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = `ws://localhost:5001/ws/console`
      wsRef.current = new WebSocket(wsUrl)

      wsRef.current.onopen = () => {
        setIsConnected(true)
        addOutput(`[INFO] Conectado a Cybersecurity Terminal`)
        addOutput(`[INFO] Usuario: ${user?.username || 'anonymous'} | Rol: ${user?.role || 'user'}`)
        addOutput(`[INFO] Terminal lista para comandos...`)
        addOutput('')
      }

      wsRef.current.onmessage = (event) => {
        try {
          const data: ConsoleMessage = JSON.parse(event.data)

          if (data.type === 'welcome') {
            addOutput(`[SYSTEM] ${data.message}`)
          } else if (data.type === 'command_start') {
            setIsRunning(true)
            addOutput(`$ ${data.command}`)
          } else if (data.type === 'stdout' && data.line) {
            addOutput(data.line)
          } else if (data.type === 'stderr' && data.message) {
            addOutput(`[ERROR] ${data.message}`)
          } else if (data.type === 'command_end') {
            setIsRunning(false)
            if (data.returncode !== undefined) {
              addOutput(`[EXIT] Código: ${data.returncode}`)
            }
            addOutput('')
          } else if (data.type === 'error') {
            addOutput(`[ERROR] ${data.message}`)
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      wsRef.current.onclose = () => {
        setIsConnected(false)
        setIsRunning(false)
        addOutput(`[ERROR] Conexión perdida con el servidor`)
      }

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsConnected(false)
        setIsRunning(false)
        addOutput(`[ERROR] Error de conexión WebSocket`)
      }
    }

    connectWebSocket()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [user])

  const addOutput = (line: string) => {
    setOutput(prev => [...prev, line])
  }

  const sendCommand = () => {
    if (!currentCommand.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return
    }

    const commandData = {
      command: currentCommand.trim(),
      user: user?.username || 'anonymous',
      timestamp: new Date().toISOString()
    }

    wsRef.current.send(JSON.stringify(commandData))
    setCurrentCommand('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      sendCommand()
    }
  }

  return (
    <div className="min-h-screen bg-black text-green-400 font-mono p-4">
      {/* Terminal Header */}
      <div className="border-b border-green-500 pb-2 mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-red-500">●</span>
          <span className="text-yellow-500">●</span>
          <span className="text-green-500">●</span>
          <span className="ml-4 text-green-400">Cybersecurity Terminal</span>
          <span className={`ml-auto ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
            {isConnected ? '●' : '○'}
          </span>
        </div>
      </div>

      {/* Terminal Output */}
      <div className="flex-1 mb-4 max-h-[calc(100vh-120px)] overflow-y-auto">
        {output.map((line, index) => (
          <div key={index} className="mb-1">
            {line}
          </div>
        ))}
        {isRunning && (
          <div className="text-yellow-400">
            <span className="animate-pulse">█</span>
          </div>
        )}
        <div ref={terminalRef} />
      </div>

      {/* Command Input */}
      <div className="flex items-center space-x-2">
        <span className="text-green-400">$</span>
        <input
          type="text"
          value={currentCommand}
          onChange={(e) => setCurrentCommand(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ingresa comando..."
          className="flex-1 bg-transparent border-none outline-none text-green-400 placeholder-green-600"
          disabled={!isConnected}
          autoFocus
        />
      </div>
    </div>
  )
}

const Console: React.FC = () => {
  const { user } = useAuth()
  const [messages, setMessages] = useState<ConsoleMessage[]>([])
  const [command, setCommand] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll a mensajes nuevos
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Conectar WebSocket
  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = `ws://localhost:5001/ws/console`
      wsRef.current = new WebSocket(wsUrl)

      wsRef.current.onopen = () => {
        setIsConnected(true)
        addMessage({
          type: 'welcome',
          message: '🔗 Conectado a Cybersecurity Console',
          timestamp: new Date().toISOString()
        })
      }

      wsRef.current.onmessage = (event) => {
        try {
          const data: ConsoleMessage = JSON.parse(event.data)
          addMessage(data)

          // Actualizar estado según el tipo de mensaje
          if (data.type === 'command_start') {
            setIsRunning(true)
          } else if (data.type === 'command_end') {
            setIsRunning(false)
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      wsRef.current.onclose = () => {
        setIsConnected(false)
        setIsRunning(false)
        addMessage({
          type: 'error',
          message: '❌ Conexión perdida con el servidor',
          timestamp: new Date().toISOString()
        })
      }

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsConnected(false)
        setIsRunning(false)
      }
    }

    connectWebSocket()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  const addMessage = (message: ConsoleMessage) => {
    setMessages(prev => [...prev, message])
  }

  const sendCommand = () => {
    if (!command.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return
    }

    const commandData = {
      command: command.trim(),
      user: user?.username || 'anonymous',
      timestamp: new Date().toISOString()
    }

    wsRef.current.send(JSON.stringify(commandData))
    setCommand('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendCommand()
    }
  }

  const clearConsole = () => {
    setMessages([])
  }

  const reconnect = () => {
    if (wsRef.current) {
      wsRef.current.close()
    }
    // La reconexión se hará automáticamente por el useEffect
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
        return 'text-green-400'
      case 'stderr':
        return 'text-yellow-400'
      case 'command_end':
        return 'text-green-300'
      case 'error':
        return 'text-red-400'
      default:
        return 'text-gray-300'
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-green-400 font-mono flex flex-col">
      {/* Header */}
      <header className="bg-gray-800 border-b border-green-500 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Terminal className="w-6 h-6 text-cyan-400" />
            <h1 className="text-xl font-bold text-cyan-400">
              Cybersecurity Console
            </h1>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
              <span className="text-sm text-gray-300">
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

          <div className="flex items-center space-x-2">
            <button
              onClick={reconnect}
              className="p-2 text-gray-400 hover:text-cyan-400 transition-colors"
              title="Reconectar"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              onClick={clearConsole}
              className="p-2 text-gray-400 hover:text-red-400 transition-colors"
              title="Limpiar consola"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Barra de información */}
        <div className="mt-2 text-xs text-gray-400 flex items-center justify-between">
          <span>
            Usuario: <span className="text-green-400">{user?.username}</span> |
            Rol: <span className="text-cyan-400">{user?.role}</span>
          </span>
          <span>
            {messages.length} mensajes | {isConnected ? 'WebSocket activo' : 'WebSocket inactivo'}
          </span>
        </div>
      </header>

      {/* Área de mensajes */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto p-4 space-y-1 bg-gray-900">
          {messages.length === 0 ? (
            <div className="text-center py-20 text-gray-500">
              <Terminal className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg mb-2">Consola lista</p>
              <p className="text-sm">Ingresa comandos para ejecutar...</p>
              <div className="mt-4 text-xs space-y-1">
                <p>💡 <strong>Comandos útiles:</strong></p>
                <p><code className="bg-gray-800 px-2 py-1 rounded">nmap -sV -p 80,443 example.com</code></p>
                <p><code className="bg-gray-800 px-2 py-1 rounded">whois example.com</code></p>
                <p><code className="bg-gray-800 px-2 py-1 rounded">dig example.com</code></p>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex items-start space-x-3 p-2 rounded ${
                  message.type === 'error' ? 'bg-red-900/20 border border-red-500/30' :
                  message.type === 'stderr' ? 'bg-yellow-900/20 border border-yellow-500/30' :
                  'hover:bg-gray-800/50'
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
      </div>

      {/* Input de comandos */}
      <div className="border-t border-green-500 bg-gray-800 p-4">
        <div className="flex items-center space-x-3">
          <span className="text-green-400 font-bold">$</span>
          <input
            ref={inputRef}
            type="text"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ingresa un comando (ej: nmap -sV -p 80 example.com)"
            className="flex-1 bg-gray-900 border border-green-500 rounded px-3 py-2 text-green-400 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 font-mono"
            disabled={!isConnected}
          />
          <button
            onClick={sendCommand}
            disabled={!command.trim() || !isConnected || isRunning}
            className="flex items-center space-x-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 disabled:bg-gray-600 text-black rounded transition-colors font-medium"
          >
            {isRunning ? (
              <>
                <Square className="w-4 h-4" />
                <span>Ejecutando...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Ejecutar</span>
              </>
            )}
          </button>
        </div>

        {/* Ayuda rápida */}
        <div className="mt-2 text-xs text-gray-500 flex items-center justify-between">
          <span>
            Presiona <kbd className="bg-gray-700 px-1 rounded">Enter</kbd> para ejecutar |
            Comandos seguros solo
          </span>
          <span>
            Estado: {isConnected ? '🟢 Conectado' : '🔴 Desconectado'}
          </span>
        </div>
      </div>
    </div>
  )
}

export default Console



