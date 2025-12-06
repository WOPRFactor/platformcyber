import React, { useState, useEffect, useRef } from 'react'
import { Activity } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { scanningAPI, ScanStartData } from '../lib/api/scanning'
import { commandPreviewAPI, CommandPreview } from '../lib/api/command-preview'
import { ScanSession } from '../types'
import { toast } from 'sonner'
import { useAuth } from '../contexts/AuthContext'
import { useWorkspace } from '../contexts/WorkspaceContext'
import { useTarget } from '../contexts/TargetContext'
import { useConsole } from '../contexts/ConsoleContext'
import CommandPreviewModal from '../components/CommandPreviewModal'
import EnumerationSection from '../components/scanning/EnumerationSection'
import NmapSection from '../components/scanning/NmapSection'
import RustScanSection from '../components/scanning/sections/RustScanSection'
import MasscanSection from '../components/scanning/sections/MasscanSection'
import NaabuSection from '../components/scanning/sections/NaabuSection'
import ScanningProgressHeader from '../components/scanning/ScanningProgressHeader'
import ScanningHistory from '../components/scanning/ScanningHistory'
import ScanningToolTabs from '../components/scanning/ScanningToolTabs'

const Scanning: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const { currentWorkspace } = useWorkspace()
  const { target, setTarget, clearTarget } = useTarget()
  const { startTask, addLog, updateTask, updateTaskProgress, completeTask, failTask, killTask, tasks } = useConsole()
  const [activeTool, setActiveTool] = useState('nmap') // Herramienta seleccionada
  const [activeTab, setActiveTab] = useState('quick') // Tipo de escaneo (solo para Nmap)
  const [activeScanSession, setActiveScanSession] = useState<string | null>(null)
  const [scanProgress, setScanProgress] = useState<{progress: number, status: string, message: string, target: string, scan_type: string} | null>(null)
  const queryClient = useQueryClient()
  
  // Estado para preview de comandos
  const [showPreview, setShowPreview] = useState(false)
  const [previewData, setPreviewData] = useState<CommandPreview | null>(null)
  const [previewToolName, setPreviewToolName] = useState('')
  const previewExecuteFnRef = useRef<(() => Promise<void>) | null>(null)

  // Auto-completar target desde workspace - SIEMPRE actualizar cuando cambia el workspace
  useEffect(() => {
    if (currentWorkspace?.target_domain) {
      // Siempre actualizar el target cuando cambia el workspace
      setTarget(currentWorkspace.target_domain)
      console.log(`🎯 Target actualizado desde workspace: ${currentWorkspace.target_domain}`)
    } else if (currentWorkspace && !currentWorkspace.target_domain) {
      // Si el workspace no tiene target, limpiar el campo
      setTarget('')
      console.log(`⚠️ Workspace sin target configurado`)
    }
  }, [currentWorkspace?.id, currentWorkspace?.target_domain, setTarget]) // Depender del ID y target_domain, no del target actual

  const { data: sessions, isLoading: sessionsLoading, error } = useQuery({
    queryKey: ['scan-sessions', currentWorkspace?.id],
    queryFn: async () => {
      console.log('🔍 Fetching sessions for workspace:', currentWorkspace?.id);
      if (!currentWorkspace?.id) {
        console.log('❌ No workspace selected');
        return [];
      }
      try {
        const result = await scanningAPI.getScanSessions(currentWorkspace.id);
        console.log('✅ Sessions fetched:', result);
        return result || [];  // Asegurar que siempre devuelve array
      } catch (err) {
        console.error('❌ Error fetching sessions:', err);
        return [];  // Devolver array vacío en caso de error
      }
    },
    enabled: isAuthenticated && !!currentWorkspace?.id,
    refetchInterval: 5000,
    retry: false  // No reintentar automáticamente
  })
  
  // Agregar esto después del query
  console.log('📊 Query state:', { sessions, isLoading: sessionsLoading, error, workspace: currentWorkspace?.id });

  // Query para monitorear progreso del escaneo activo
  const { data: activeScanData, isLoading: activeScanLoading, error: activeScanError } = useQuery({
    queryKey: ['scan-status', activeScanSession],
    queryFn: () => activeScanSession ? scanningAPI.getScanStatus(activeScanSession) : null,
    enabled: !!activeScanSession && isAuthenticated,
    refetchInterval: 2000, // Monitorear cada 2 segundos
  })

  // Efecto para procesar los datos del escaneo activo
  useEffect(() => {
    if (activeScanData && activeScanData.session) {
      const session = activeScanData.session
      setScanProgress({
        progress: session.progress || 0,
        status: session.status,
        message: `Escaneo ${session.scan_type || 'basic'} - ${session.progress || 0}% completado`,
        target: session.target,
        scan_type: session.scan_type || 'basic'
      })

      // Si el escaneo se completó o falló, detener monitoreo
      if (session.status === 'completed' || session.status === 'failed') {
        setActiveScanSession(null)
        queryClient.invalidateQueries({ queryKey: ['scan-sessions'] })

        if (session.status === 'completed') {
          toast.success(`Escaneo completado: ${session.ports_found || 0} puertos, ${session.services_detected || 0} servicios`)
        } else {
          toast.error('Escaneo falló')
        }
      }
    }
  }, [activeScanData, queryClient])

  // Manejar errores
  useEffect(() => {
    if (activeScanError) {
      setActiveScanSession(null)
      setScanProgress(null)
      toast.error('Error monitoreando progreso del escaneo')
    }
  }, [activeScanError])

  // Actualizar tarea de consola cuando cambia el progreso del escaneo activo
  useEffect(() => {
    if (!activeScanSession || !activeScanData?.session) return

    const session = activeScanData.session
    const activeTask = tasks.find(t => t.session_id === activeScanSession && t.status === 'running')
    if (!activeTask) return

    const realProgress = session.progress || 0
    const realStatus = session.status

    // Actualizar progreso de la tarea de consola
    if (realProgress !== activeTask.progress) {
      let displayMessage = 'Procesando...'
      if (realStatus === 'running') {
        displayMessage = realProgress < 40 ? 'Ejecutando escaneo Nmap...' :
                        realProgress < 70 ? 'Analizando puertos abiertos...' :
                        realProgress < 90 ? 'Detectando servicios...' : 'Finalizando análisis...'
      }
      updateTaskProgress(activeTask.id, realProgress, displayMessage)
    }

    // Si completó o falló, cerrar tarea
    if (realStatus === 'completed') {
      completeTask(activeTask.id, `Escaneo completado: ${session.ports_found || 0} puertos encontrados`)
    } else if (realStatus === 'failed') {
      // Intentar obtener el mensaje de error de diferentes fuentes
      const errorMessage = session.error || 
                          (activeScanData as any)?.error || 
                          (activeScanData as any)?.details ||
                          'Error desconocido. Revisa los logs del backend para más detalles.'
      failTask(activeTask.id, errorMessage)
    }
  }, [activeScanData, activeScanSession, tasks, updateTaskProgress, completeTask, failTask])

  // Mutación para iniciar escaneo
  const scanMutation = useMutation({
    mutationFn: (data: ScanStartData) => scanningAPI.startScan(data),
    onMutate: (data) => {
      // Iniciar tarea en consola
      const taskId = startTask('Scanning', `Escaneo ${data.scan_type} en ${data.target}`)

      // Log inicial
      addLog('info', 'scanning', `Iniciando escaneo ${data.scan_type} para ${data.target}`, taskId, `nmap ${data.scan_type === 'quick' ? '-sn' : data.scan_type === 'services' ? '-sV -O' : '-A -T4'} ${data.target}`)
      updateTaskProgress(taskId, 10, 'Iniciando escaneo...')

      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`Escaneo iniciado: ${data.message}`)
      queryClient.invalidateQueries({ queryKey: ['scan-sessions'] })

      // Iniciar monitoreo del progreso real usando scan_id
      if (data.scan_id) {
        setActiveScanSession(String(data.scan_id))
        setScanProgress({
          progress: 0,
          status: 'running',
          message: 'Iniciando escaneo...',
          target: variables.target,
          scan_type: variables.scan_type || 'basic'
        })
      }

      // Actualizar consola Y guardar scan_id en la tarea
      if (context?.taskId && data.scan_id) {
        updateTaskProgress(context.taskId, 0, 'Escaneo enviado al backend')
        addLog('info', 'scanning', `Escaneo iniciado: scan_id ${data.scan_id}`, context.taskId)
        // Guardar scan_id para el monitoreo del progreso
        updateTask(context.taskId, { session_id: String(data.scan_id) })
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar escaneo: ${error.message}`)

      // Marcar error en consola
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })


  // Helper para Nmap con preview
  const handleNmapWithPreview = async (scanType: string) => {
    if (!target.trim() || !currentWorkspace?.id) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewNmapScan({
        target: target,
        workspace_id: currentWorkspace.id,
        scan_type: scanType
      })

      setPreviewData(preview)
      setPreviewToolName(`Nmap ${scanType}`)
      previewExecuteFnRef.current = async () => {
        const scanData: ScanStartData & { workspace_id: number; tool?: string } = {
          target: preview.parameters.target,
          scan_type: preview.parameters.scan_type,
          workspace_id: currentWorkspace.id,
          tool: 'nmap',
          options: {
            stealth_mode: false,
            aggressive_mode: scanType === 'comprehensive',
            full_scan: scanType === 'comprehensive'
          }
        }
        scanMutation.mutate(scanData)
      };
      setShowPreview(true)
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
      // NO ejecutar el comando automáticamente - el usuario debe confirmar desde el preview
    }
  }

  const handleScan = (scanType: string) => {
    if (!target.trim()) {
      toast.error('Por favor ingrese un target válido')
      return
    }

    if (!currentWorkspace?.id) {
      toast.error('Por favor selecciona un workspace')
      return
    }

    // Preparar datos del escaneo
    const scanData: ScanStartData & { workspace_id: number; tool?: string } = {
      target: target.trim(),
      scan_type: scanType,
      workspace_id: currentWorkspace.id,
      tool: 'nmap', // Siempre Nmap para los tipos de escaneo actuales
      options: {
        stealth_mode: false,
        aggressive_mode: scanType === 'comprehensive',
        full_scan: scanType === 'comprehensive'
      }
    }

    scanMutation.mutate(scanData)
  }


  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Scanning</h1>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Activity className="w-4 h-4" />
          Sistema de escaneo avanzado activo
        </div>
      </div>

      {/* Barra de progreso del escaneo activo */}
      <ScanningProgressHeader scanProgress={scanProgress} />

      {/* Input del target */}
      <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
        <div className="mb-4">
          <h2 className="text-xl font-bold text-green-400">Target</h2>
          {currentWorkspace?.target_domain ? (
            <div className="space-y-2">
              <p className="text-green-600 flex items-center gap-2">
                <span className="text-green-400">🎯</span>
                Target del workspace: <span className="text-green-300 font-mono font-bold">{currentWorkspace.target_domain}</span>
              </p>
              {currentWorkspace.target_ip && (
                <p className="text-gray-400 text-sm">
                  IP: <span className="text-gray-300 font-mono">{currentWorkspace.target_ip}</span>
                </p>
              )}
              <p className="text-xs text-gray-500">
                Este target se auto-completa desde la configuración del workspace. Puedes modificarlo si necesitas escanear otro objetivo.
              </p>
            </div>
          ) : (
            <p className="text-yellow-600">
              ⚠️ Este workspace no tiene un target configurado. Ingresa manualmente el objetivo del escaneo.
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="ej: example.com, 192.168.1.1, 192.168.1.0/24"
            className="flex-1 bg-gray-900 border border-green-500 rounded px-3 py-2 text-green-400 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          {target && (
            <button
              onClick={clearTarget}
              className="btn-secondary px-3 ml-2"
              title="Limpiar target"
            >
              🗑️
            </button>
          )}
        </div>
      </div>

      {/* Herramientas de escaneo */}
      <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
        <div className="mb-4">
          <h2 className="text-xl font-bold text-green-400">Herramientas de Escaneo</h2>
          <p className="text-green-600">
            Seleccione la herramienta y tipo de escaneo a realizar
          </p>
        </div>

        <div className="w-full">
          <ScanningToolTabs
            activeTool={activeTool}
            setActiveTool={setActiveTool}
            setActiveTab={setActiveTab}
          />

          {/* Contenido para Nmap */}
          {activeTool === 'nmap' && (
            <NmapSection
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              setActiveScanSession={setActiveScanSession}
              setScanProgress={setScanProgress}
            />
          )}

          {/* Contenido para RustScan */}
          {activeTool === 'rustscan' && (
            <RustScanSection setActiveScanSession={setActiveScanSession} />
                  )}

          {/* Contenido para Masscan */}
          {activeTool === 'masscan' && (
            <MasscanSection setActiveScanSession={setActiveScanSession} />
          )}

          {/* Contenido para Naabu */}
          {activeTool === 'naabu' && (
            <NaabuSection setActiveScanSession={setActiveScanSession} />
          )}

          {/* Enumeración */}
          {activeTool === 'enumeration' && <EnumerationSection />}
        </div>
      </div>

      {/* Historial de sesiones */}
      <ScanningHistory
        sessions={sessions}
        sessionsLoading={sessionsLoading}
        tasks={tasks}
        killTask={killTask}
      />
    </div>
  )
}

export default Scanning