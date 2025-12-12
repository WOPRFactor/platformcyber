import React, { useState, useEffect, useRef } from 'react'
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

const RealTerminal: React.FC = () => {
  const { user } = useAuth()
  const [output, setOutput] = useState<string[]>([])
  const [currentCommand, setCurrentCommand] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const terminalRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    terminalRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [output])

  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = `ws://localhost:5003/ws/console`
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

  // Auto-focus en el input cuando se carga
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  return (
    <div className="min-h-screen bg-black text-gray-900 font-mono p-4">
      {/* Terminal Header */}
      <div className="border-b border-gray-200 pb-2 mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-red-500">●</span>
          <span className="text-yellow-500">●</span>
          <span className="text-gray-800">●</span>
          <span className="ml-4 text-gray-900">Cybersecurity Terminal</span>
          <span className={`ml-auto ${isConnected ? 'text-gray-900' : 'text-red-400'}`}>
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
        <span className="text-gray-900">$</span>
        <input
          ref={inputRef}
          type="text"
          value={currentCommand}
          onChange={(e) => setCurrentCommand(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ingresa comando..."
          className="flex-1 bg-transparent border-none outline-none text-gray-900 placeholder-green-600"
          disabled={!isConnected}
          autoFocus
        />
      </div>
    </div>
  )
}

export default RealTerminal
