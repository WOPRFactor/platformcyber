import React, { useState } from 'react'
import { ShieldCheck, Loader2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { containerAPI } from '../../lib/api/container'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../pages/VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../CommandPreviewModal'

interface KubescapeSectionProps {
  workspaceId: number
}

export const KubescapeSection: React.FC<KubescapeSectionProps> = ({ workspaceId }) => {
  const { startTask, addLog, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview
  
  const [framework, setFramework] = useState('nsa')
  const [namespace, setNamespace] = useState('')

  const kubescapeMutation = useMutation({
    mutationFn: () => {
      if (!workspaceId) {
        throw new Error('Workspace es requerido')
      }
      return containerAPI.runKubescape(workspaceId, framework, namespace || undefined)
    },
    onMutate: () => {
      const taskId = startTask('Container Security', `Kubescape: ${framework}`)
      addLog('info', 'container', `Iniciando Kubescape con framework ${framework}`, taskId, `kubescape scan framework ${framework}`)
      updateTaskProgress(taskId, 10, 'Iniciando Kubescape...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`Kubescape iniciado: ${data.scan_id}`)
      queryClient.invalidateQueries({ queryKey: ['container-scans'] })
      if (context?.taskId) {
        updateTaskProgress(context.taskId, 25, 'Scan enviado al backend')
        addLog('info', 'container', `Scan iniciado: ${data.scan_id}`, context.taskId)
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar Kubescape: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const handleKubescapeWithPreview = async () => {
    if (!workspaceId) {
      toast.error('Workspace es requerido')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewKubescape({
        workspace_id: workspaceId,
        framework,
        namespace: namespace || undefined
      })

      commandPreview.openPreview(preview, 'Kubescape', async () => {
        await kubescapeMutation.mutateAsync()
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
            <ShieldCheck className="w-5 h-5" />
            Kubescape - Kubernetes Security Platform
          </h3>
          <p className="text-purple-600">
            Plataforma de seguridad para Kubernetes con múltiples frameworks
          </p>
        </div>

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Framework de seguridad
            </label>
            <select
              value={framework}
              onChange={(e) => setFramework(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="nsa">NSA/CISA Framework</option>
              <option value="mitre">MITRE ATT&CK</option>
              <option value="armo">ARMO Best Practices</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Namespace (opcional)
              <span className="text-xs text-gray-500 ml-2">Dejar vacío para todos los namespaces</span>
            </label>
            <input
              type="text"
              value={namespace}
              onChange={(e) => setNamespace(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="default"
            />
          </div>
        </div>

        <button
          onClick={handleKubescapeWithPreview}
          disabled={kubescapeMutation.isPending}
          className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2"
        >
          {kubescapeMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Iniciando scan...
            </>
          ) : (
            <>
              <ShieldCheck className="w-4 h-4" />
              Ejecutar Kubescape
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





