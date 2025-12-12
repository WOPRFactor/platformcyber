/**
 * NmapSection Component
 * =====================
 * 
 * Componente completo para escaneos Nmap con todas sus sub-tabs.
 */

import React, { useState, useRef } from 'react'
import { Zap, Server, Shield, Target, Globe, Search, Loader2 } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { scanningAPI, ScanStartData } from '../../lib/api/scanning'
import { useWorkspace } from '../../contexts/WorkspaceContext'
import { useTarget } from '../../contexts/TargetContext'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useQueryClient } from '@tanstack/react-query'
import { commandPreviewAPI, CommandPreview } from '../../lib/api/command-preview'
import CommandPreviewModal from '../../components/CommandPreviewModal'

interface NmapSectionProps {
  activeTab: string
  setActiveTab: (tab: string) => void
  setActiveScanSession: (session: string | null) => void
  setScanProgress: (progress: any) => void
}

const NmapSection: React.FC<NmapSectionProps> = ({
  activeTab,
  setActiveTab,
  setActiveScanSession,
  setScanProgress
}) => {
  const { currentWorkspace } = useWorkspace()
  const { target } = useTarget()
  const { startTask, addLog, updateTask, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  
  // Estado para preview de comandos
  const [showPreview, setShowPreview] = useState(false)
  const [previewData, setPreviewData] = useState<CommandPreview | null>(null)
  const [previewToolName, setPreviewToolName] = useState('')
  const previewExecuteFnRef = useRef<(() => Promise<void>) | null>(null)

  const scanMutation = useMutation({
    mutationFn: (data: ScanStartData) => scanningAPI.startScan(data),
    onMutate: (data) => {
      const taskId = startTask('Scanning', `Escaneo ${data.scan_type} en ${data.target}`)
      addLog('info', 'scanning', `Iniciando escaneo ${data.scan_type} para ${data.target}`, taskId)
      updateTaskProgress(taskId, 10, 'Iniciando escaneo...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`Escaneo iniciado: ${data.message}`)
      queryClient.invalidateQueries({ queryKey: ['scan-sessions'] })
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
      if (context?.taskId && data.scan_id) {
        updateTaskProgress(context.taskId, 0, 'Escaneo enviado al backend')
        addLog('info', 'scanning', `Escaneo iniciado: scan_id ${data.scan_id}`, context.taskId)
        updateTask(context.taskId, { session_id: String(data.scan_id) })
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar escaneo: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  // Helper para Nmap con preview
  const handleNmapWithPreview = async (scanType: string) => {
    if (!target?.trim() || !currentWorkspace?.id) {
      toast.error('Target y workspace son requeridos')
      return
    }

    // Mapear tipos de escaneo del frontend a los del backend
    const scanTypeMap: Record<string, string> = {
      'quick': 'quick',
      'service': 'service',
      'vulnerability': 'vuln',
      'os': 'os',
      'network': 'discovery',
      'comprehensive': 'comprehensive'
    }

    const backendScanType = scanTypeMap[scanType] || scanType

    try {
      const preview = await commandPreviewAPI.previewNmapScan({
        target: target.trim(),
        workspace_id: currentWorkspace.id,
        scan_type: backendScanType
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
    if (!target?.trim() || !currentWorkspace?.id) {
      toast.error('Target y workspace son requeridos')
      return
    }
    const scanData: ScanStartData & { workspace_id: number; tool?: string } = {
      target: target.trim(),
      scan_type: scanType,
      workspace_id: currentWorkspace.id,
      tool: 'nmap',
      options: {
        stealth_mode: false,
        aggressive_mode: scanType === 'comprehensive',
        full_scan: scanType === 'comprehensive'
      }
    }
    scanMutation.mutate(scanData)
  }
  
  // Handler para ejecutar desde preview
  const handleExecuteFromPreview = async () => {
    if (previewExecuteFnRef.current) {
      setShowPreview(false)
      await previewExecuteFnRef.current()
    }
  }

  return (
    <>
      <div className="flex border-b border-gray-200 mb-4">
        <button
          onClick={() => setActiveTab('quick')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 ${
            activeTab === 'quick'
              ? 'border-gray-200 text-gray-900'
              : 'border-transparent text-gray-500 hover:text-gray-900'
          }`}
        >
          <Zap className="w-4 h-4" />
          Rápido
        </button>
        <button
          onClick={() => setActiveTab('service')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 ${
            activeTab === 'service'
              ? 'border-gray-200 text-gray-900'
              : 'border-transparent text-gray-500 hover:text-gray-900'
          }`}
        >
          <Server className="w-4 h-4" />
          Servicios
        </button>
        <button
          onClick={() => setActiveTab('vulnerability')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 ${
            activeTab === 'vulnerability'
              ? 'border-gray-200 text-gray-900'
              : 'border-transparent text-gray-500 hover:text-gray-900'
          }`}
        >
          <Shield className="w-4 h-4" />
          Vuln.
        </button>
        <button
          onClick={() => setActiveTab('os')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 ${
            activeTab === 'os'
              ? 'border-gray-200 text-gray-900'
              : 'border-transparent text-gray-500 hover:text-gray-900'
          }`}
        >
          <Target className="w-4 h-4" />
          OS
        </button>
        <button
          onClick={() => setActiveTab('network')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 ${
            activeTab === 'network'
              ? 'border-gray-200 text-gray-900'
              : 'border-transparent text-gray-500 hover:text-gray-900'
          }`}
        >
          <Globe className="w-4 h-4" />
          Red
        </button>
        <button
          onClick={() => setActiveTab('comprehensive')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 ${
            activeTab === 'comprehensive'
              ? 'border-gray-200 text-gray-900'
              : 'border-transparent text-gray-500 hover:text-gray-900'
          }`}
        >
          <Search className="w-4 h-4" />
          Completo
        </button>
      </div>

      {activeTab === 'quick' && (
        <div className="mt-4">
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Zap className="w-5 h-5" />
                Escaneo Rápido de Puertos
              </h3>
              <p className="text-gray-500">Escanea los 1000 puertos más comunes usando Nmap -F</p>
            </div>
            <button
              onClick={() => handleNmapWithPreview('quick')}
              disabled={scanMutation.isPending}
              className="w-full bg-red-600 hover:bg-red-700 disabled:bg-green-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center"
            >
              {scanMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Zap className="w-4 h-4 mr-2" />}
              Iniciar Escaneo Rápido
            </button>
          </div>
        </div>
      )}

      {activeTab === 'service' && (
        <div className="mt-4">
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Server className="w-5 h-5" />
                Escaneo de Servicios y Versiones
              </h3>
              <p className="text-gray-500">Detecta servicios corriendo, versiones y realiza detección OS básica</p>
            </div>
            <button
              onClick={() => handleNmapWithPreview('service')}
              disabled={scanMutation.isPending}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center"
            >
              {scanMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Server className="w-4 h-4 mr-2" />}
              Iniciar Escaneo de Servicios
            </button>
          </div>
        </div>
      )}

      {activeTab === 'vulnerability' && (
        <div className="mt-4">
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Escaneo de Vulnerabilidades
              </h3>
              <p className="text-gray-500">Ejecuta scripts NSE de vulnerabilidades usando --script vuln</p>
            </div>
            <button
              onClick={() => handleNmapWithPreview('vulnerability')}
              disabled={scanMutation.isPending}
              className="w-full bg-red-600 hover:bg-red-700 disabled:bg-red-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center"
            >
              {scanMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Shield className="w-4 h-4 mr-2" />}
              Iniciar Escaneo de Vulnerabilidades
            </button>
          </div>
        </div>
      )}

      {activeTab === 'os' && (
        <div className="mt-4">
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Target className="w-5 h-5" />
                Detección de Sistema Operativo
              </h3>
              <p className="text-gray-500">Intenta determinar el sistema operativo usando huellas TCP/IP</p>
            </div>
            <button
              onClick={() => handleNmapWithPreview('os')}
              disabled={scanMutation.isPending}
              className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center"
            >
              {scanMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Target className="w-4 h-4 mr-2" />}
              Iniciar Detección OS
            </button>
          </div>
        </div>
      )}

      {activeTab === 'network' && (
        <div className="mt-4">
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Globe className="w-5 h-5" />
                Descubrimiento de Red
              </h3>
              <p className="text-gray-500">Descubre hosts activos en la red usando ping sweeps</p>
            </div>
            <button
              onClick={() => handleNmapWithPreview('network')}
              disabled={scanMutation.isPending}
              className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center"
            >
              {scanMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Globe className="w-4 h-4 mr-2" />}
              Iniciar Descubrimiento de Red
            </button>
          </div>
        </div>
      )}

      {activeTab === 'comprehensive' && (
        <div className="mt-4">
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Search className="w-5 h-5" />
                Escaneo Completo
              </h3>
              <p className="text-gray-500">Ejecuta todos los tipos de escaneo en secuencia para un análisis completo</p>
            </div>
            <div className="border border-yellow-500 bg-yellow-50 p-4 rounded-xl mb-4">
              <p className="text-yellow-800">
                Este escaneo puede tomar varios minutos y genera alta carga en la red.
                Se ejecutarán: puertos, servicios, OS y vulnerabilidades.
              </p>
            </div>
            <button
              onClick={() => handleNmapWithPreview('comprehensive')}
              disabled={scanMutation.isPending}
              className="w-full bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 disabled:from-green-800 disabled:to-blue-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center"
            >
              {scanMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Search className="w-4 h-4 mr-2" />}
              Iniciar Escaneo Completo
            </button>
          </div>
        </div>
      )}
      
      <CommandPreviewModal
        isOpen={showPreview}
        onClose={() => setShowPreview(false)}
        onExecute={handleExecuteFromPreview}
        previewData={previewData}
        toolName={previewToolName}
        category="scanning"
      />
    </>
  )
}

export default NmapSection

