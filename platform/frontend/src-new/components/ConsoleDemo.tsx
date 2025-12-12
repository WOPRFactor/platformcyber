import React from 'react'
import { Play, Terminal, Zap } from 'lucide-react'
import { useConsole } from '../contexts/ConsoleContext'
import { useTaskProgress } from '../hooks/useTaskProgress'

interface ConsoleDemoProps {
  className?: string
}

const ConsoleDemo: React.FC<ConsoleDemoProps> = ({ className }) => {
  const { addLog, startTask, updateTaskProgress, completeTask, failTask } = useConsole()
  const { executeTask, executeCommand, logInfo, logSuccess, logError } = useTaskProgress()

  // Función que simula EXACTAMENTE lo que pasa cuando ejecutas un proceso real
  const simulateRealProcess = async () => {
    try {
      // 🚀 ESTO ABRE AUTOMÁTICAMENTE LA CONSOLA CUANDO SE EJECUTA
      await executeCommand(
        `nmap -sV -p 1-1000 example.com`,
        {
          module: 'scanning',
          target: 'example.com'
        },
        async (updateProgress) => {
          // Simular los logs que verías en un escaneo real
          updateProgress(5, 'Resolviendo hostname...')
          await new Promise(resolve => setTimeout(resolve, 500))

          updateProgress(15, 'Iniciando escaneo SYN...')
          await new Promise(resolve => setTimeout(resolve, 800))

          updateProgress(30, 'Puerto 22/tcp abierto - SSH detectado')
          await new Promise(resolve => setTimeout(resolve, 600))

          updateProgress(45, 'Puerto 80/tcp abierto - HTTP detectado')
          await new Promise(resolve => setTimeout(resolve, 700))

          updateProgress(60, 'Puerto 443/tcp abierto - HTTPS detectado')
          await new Promise(resolve => setTimeout(resolve, 800))

          updateProgress(75, 'Analizando versiones de servicios...')
          await new Promise(resolve => setTimeout(resolve, 900))

          updateProgress(85, 'Detectando sistema operativo...')
          await new Promise(resolve => setTimeout(resolve, 600))

          updateProgress(95, 'Generando reporte...')
          await new Promise(resolve => setTimeout(resolve, 500))

          updateProgress(100, 'Escaneo completado - 3 puertos abiertos encontrados')
        }
      )
    } catch (error) {
      console.error('Error en proceso simulado:', error)
    }
  }

  // Mantener la función anterior por compatibilidad
  const simulateScanTask = simulateRealProcess

  // Función para simular análisis de vulnerabilidades
  const simulateVulnAnalysis = async () => {
    try {
      await executeCommand(
        'nikto -h example.com',
        { module: 'vulnerability', target: 'example.com' },
        async (updateProgress) => {
          updateProgress(15, 'Iniciando análisis web...')
          await new Promise(resolve => setTimeout(resolve, 800))

          updateProgress(30, 'Escaneando directorios comunes...')
          await new Promise(resolve => setTimeout(resolve, 1200))

          updateProgress(50, 'Verificando configuraciones inseguras...')
          await new Promise(resolve => setTimeout(resolve, 1000))

          updateProgress(70, 'Analizando headers HTTP...')
          await new Promise(resolve => setTimeout(resolve, 800))

          updateProgress(85, 'Buscando archivos expuestos...')
          await new Promise(resolve => setTimeout(resolve, 1000))

          updateProgress(100, 'Análisis completado - 3 vulnerabilidades encontradas')
        }
      )
    } catch (error) {
      console.error('Error en análisis de vulnerabilidades:', error)
    }
  }

  // Función para simular múltiples tareas simultáneas
  const simulateMultipleTasks = async () => {
    const tasks = [
      simulateScanTask(),
      simulateVulnAnalysis(),
      // Simular una tarea que falla
      (async () => {
        try {
          await executeTask(
            'Análisis de malware',
            { module: 'malware', target: 'suspicious.exe' },
            async (updateProgress) => {
              updateProgress(20, 'Descargando archivo...')
              await new Promise(resolve => setTimeout(resolve, 1000))

              updateProgress(50, 'Analizando comportamiento...')
              await new Promise(resolve => setTimeout(resolve, 1200))

              updateProgress(80, 'Verificando firmas...')
              await new Promise(resolve => setTimeout(resolve, 1000))

              // Simular error
              throw new Error('Archivo corrupto - no se puede analizar')
            }
          )
        } catch (error) {
          // Error ya manejado por executeTask
        }
      })()
    ]

    await Promise.all(tasks)
  }

  // Función para agregar logs de ejemplo
  const addSampleLogs = () => {
    const sampleLogs = [
      { type: 'info', module: 'system', message: 'Sistema inicializado correctamente' },
      { type: 'success', module: 'auth', message: 'Usuario admin autenticado' },
      { type: 'warning', module: 'network', message: 'Latencia alta detectada en conexión' },
      { type: 'error', module: 'database', message: 'Error de conexión a base de datos' },
      { type: 'command', module: 'recon', message: 'Ejecutando: whois example.com', command: 'whois example.com' },
      { type: 'info', module: 'scanning', message: 'Puerto 80 abierto - HTTP detectado' },
      { type: 'success', module: 'reporting', message: 'Reporte generado exitosamente' }
    ]

    sampleLogs.forEach((log, index) => {
      setTimeout(() => {
        addLog(log.type as any, log.module, log.message, undefined, log.command)
      }, index * 500)
    })
  }

  return (
    <div className={`p-4 bg-white rounded-xl border border-cyan-500 ${className}`}>
      <h3 className="text-lg font-semibold text-cyan-400 mb-4 flex items-center">
        <Terminal className="w-5 h-5 mr-2" />
        🔔 Consola Automática - Demo
      </h3>

      <div className="mb-4 p-3 bg-cyan-500/10 border border-cyan-500/30 rounded">
        <p className="text-sm text-cyan-300">
          💡 <strong>¡Prueba real!</strong> Ve al módulo Reconnaissance, ingresa un target como "google.com"
          y ejecuta WHOIS, DNS o Subdominios. La consola se abrirá automáticamente mostrando el progreso.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Simulación de Procesos Reales */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-600 flex items-center">
            <Zap className="w-4 h-4 mr-2 text-yellow-400" />
            Simular Procesos Reales
          </h4>
          <button
            onClick={simulateScanTask}
            className="w-full flex items-center justify-center px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors"
          >
            <Play className="w-4 h-4 mr-2" />
            🚀 Escaneo Nmap Real
          </button>
          <button
            onClick={simulateVulnAnalysis}
            className="w-full flex items-center justify-center px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-colors"
          >
            <Zap className="w-4 h-4 mr-2" />
            Análisis de Vuln.
          </button>
          <button
            onClick={simulateMultipleTasks}
            className="w-full flex items-center justify-center px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm transition-colors"
          >
            <Terminal className="w-4 h-4 mr-2" />
            Múltiples Tareas
          </button>
        </div>

        {/* Logs de Ejemplo */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-600">Logs de Ejemplo</h4>
          <button
            onClick={addSampleLogs}
            className="w-full flex items-center justify-center px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-colors"
          >
            <Terminal className="w-4 h-4 mr-2" />
            Agregar Logs
          </button>
          <div className="text-xs text-gray-500 mt-2">
            <p>• Click en el botón del terminal (abajo derecha)</p>
            <p>• Prueba diferentes tamaños (minimizar/compacto/completo)</p>
            <p>• Observa el progreso en tiempo real</p>
          </div>
        </div>
      </div>

      <div className="mt-4 p-3 bg-gray-50 rounded text-xs text-gray-500">
        <p className="font-medium text-cyan-400 mb-2">🎯 Cómo Funciona la Apertura Automática:</p>
        <div className="space-y-2">
          <div className="flex items-start space-x-2">
            <span className="text-cyan-400 font-mono">1.</span>
            <span>Ejecutas cualquier proceso (WHOIS, DNS, escaneo, etc.)</span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="text-cyan-400 font-mono">2.</span>
            <span>La consola se abre automáticamente mostrando progreso</span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="text-cyan-400 font-mono">3.</span>
            <span>Logs en tiempo real de comandos ejecutados</span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="text-cyan-400 font-mono">4.</span>
            <span>Barras de progreso animadas</span>
          </div>
          <div className="flex items-start space-x-2">
            <span className="text-cyan-400 font-mono">5.</span>
            <span>Notificaciones cuando termina</span>
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="font-medium text-yellow-400 mb-1">💡 Consejos:</p>
          <ul className="space-y-1">
            <li>• <strong>Arrastra</strong> la consola para moverla</li>
            <li>• <strong>Minimiza/Maximiza</strong> para cambiar tamaño</li>
            <li>• <strong>Escape</strong> para cerrar rápidamente</li>
            <li>• Los logs se mantienen hasta que los limpies</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default ConsoleDemo
