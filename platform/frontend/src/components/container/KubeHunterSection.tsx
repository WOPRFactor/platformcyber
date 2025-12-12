import React, { useState } from 'react'
import { Target, Loader2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { containerAPI } from '../../lib/api/container'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../pages/VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../CommandPreviewModal'

interface KubeHunterSectionProps {
  workspaceId: number
}

export const KubeHunterSection: React.FC<KubeHunterSectionProps> = ({ workspaceId }) => {
  const { startTask, addLog, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview
  
  const [mode, setMode] = useState('remote')
  const [remoteHost, setRemoteHost] = useState('')

  const kubeHunterMutation = useMutation({
    mutationFn: () => {
      if (!workspaceId) {
        throw new Error('Workspace es requerido')
      }
      if (mode === 'remote' && !remoteHost.trim()) {
        throw new Error('Host remoto es requerido para modo remote')
      }
      return containerAPI.runKubeHunter(workspaceId, mode, remoteHost || undefined)
    },
    onMutate: () => {
      const taskId = startTask('Container Security', `Kube-hunter: ${mode}`)
      addLog('info', 'container', `Iniciando Kube-hunter en modo ${mode}`, taskId, `kube-hunter --${mode}`)
      updateTaskProgress(taskId, 10, 'Iniciando Kube-hunter...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`Kube-hunter iniciado: ${data.scan_id}`)
      queryClient.invalidateQueries({ queryKey: ['container-scans'] })
      if (context?.taskId) {
        updateTaskProgress(context.taskId, 25, 'Scan enviado al backend')
        addLog('info', 'container', `Scan iniciado: ${data.scan_id}`, context.taskId)
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar Kube-hunter: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const handleKubeHunterWithPreview = async () => {
    if (!workspaceId) {
      toast.error('Workspace es requerido')
      return
    }
    if (mode === 'remote' && !remoteHost.trim()) {
      toast.error('Host remoto es requerido para modo remote')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewKubeHunter({
        workspace_id: workspaceId,
        mode,
        remote_host: remoteHost || undefined
      })

      commandPreview.openPreview(preview, 'Kube-hunter', async () => {
        await kubeHunterMutation.mutateAsync()
      })
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error.message || 'Error desconocido'}`)
    }
  }

  return (
    <div className="mt-4">
      <div className="bg-gray-900 border border-purple-500 rounded-lg p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-purple-400 flex items-center gap-2">
            <Target className="w-5 h-5" />
            Kube-hunter - Kubernetes Penetration Testing
          </h3>
          <p className="text-purple-600">
            Herramienta de pentesting para clusters Kubernetes
          </p>
        </div>

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Modo de ejecución
            </label>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="remote">Remote (escanear cluster remoto)</option>
              <option value="pod">Pod (ejecutar desde dentro del cluster)</option>
            </select>
          </div>

          {mode === 'remote' && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Host remoto
                <span className="text-xs text-gray-500 ml-2">IP o hostname del cluster</span>
              </label>
              <input
                type="text"
                value={remoteHost}
                onChange={(e) => setRemoteHost(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="192.168.1.100"
              />
            </div>
          )}
        </div>

        <button
          onClick={handleKubeHunterWithPreview}
          disabled={kubeHunterMutation.isPending || (mode === 'remote' && !remoteHost.trim())}
          className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2"
        >
          {kubeHunterMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Iniciando scan...
            </>
          ) : (
            <>
              <Target className="w-4 h-4" />
              Ejecutar Kube-hunter
            </>
          )}
        </button>
      </div>

      <CommandPreviewModal
        isOpen={showPreview}
        onClose={closePreview}
        previewData={previewData}
        category="Cloud Pentesting"
        toolName={previewToolName}
        onExecute={async (parameters: Record<string, any>) => { await executePreview() }}
          // Los parámetros ya están en el estado del componente, solo ejecutar
      />
    </div>
  )
}





