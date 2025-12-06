import React, { useState } from 'react'
import { CheckSquare, Loader2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { containerAPI } from '../../lib/api/container'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../pages/VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../CommandPreviewModal'

interface KubeBenchSectionProps {
  workspaceId: number
}

export const KubeBenchSection: React.FC<KubeBenchSectionProps> = ({ workspaceId }) => {
  const { startTask, addLog, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview
  
  const [targets, setTargets] = useState<string[]>(['master', 'node'])

  const kubeBenchMutation = useMutation({
    mutationFn: () => {
      if (!workspaceId) {
        throw new Error('Workspace es requerido')
      }
      return containerAPI.runKubeBench(workspaceId, targets.length > 0 ? targets : undefined)
    },
    onMutate: () => {
      const taskId = startTask('Container Security', `Kube-bench: ${targets.join(', ')}`)
      addLog('info', 'container', `Iniciando Kube-bench para ${targets.join(', ')}`, taskId, `kube-bench ${targets.join(' ')}`)
      updateTaskProgress(taskId, 10, 'Iniciando Kube-bench...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`Kube-bench iniciado: ${data.scan_id}`)
      queryClient.invalidateQueries({ queryKey: ['container-scans'] })
      if (context?.taskId) {
        updateTaskProgress(context.taskId, 25, 'Scan enviado al backend')
        addLog('info', 'container', `Scan iniciado: ${data.scan_id}`, context.taskId)
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar Kube-bench: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const handleKubeBenchWithPreview = async () => {
    if (!workspaceId) {
      toast.error('Workspace es requerido')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewKubeBench({
        workspace_id: workspaceId,
        targets: targets.length > 0 ? targets : undefined
      })

      commandPreview.openPreview(preview, 'Kube-bench', async () => {
        await kubeBenchMutation.mutateAsync()
      })
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error.message || 'Error desconocido'}`)
    }
  }

  const toggleTarget = (target: string) => {
    setTargets(prev => 
      prev.includes(target) 
        ? prev.filter(t => t !== target)
        : [...prev, target]
    )
  }

  return (
    <div className="mt-4">
      <div className="bg-gray-900 border border-purple-500 rounded-lg p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-purple-400 flex items-center gap-2">
            <CheckSquare className="w-5 h-5" />
            Kube-bench - CIS Kubernetes Benchmark
          </h3>
          <p className="text-purple-600">
            Verifica la configuración de Kubernetes contra el benchmark CIS
          </p>
        </div>

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Componentes a verificar
            </label>
            <div className="flex flex-wrap gap-2">
              {['master', 'node', 'etcd', 'policies'].map(target => (
                <button
                  key={target}
                  onClick={() => toggleTarget(target)}
                  className={`px-3 py-1 rounded-md text-sm ${
                    targets.includes(target)
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {target.charAt(0).toUpperCase() + target.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        <button
          onClick={handleKubeBenchWithPreview}
          disabled={kubeBenchMutation.isPending || targets.length === 0}
          className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2"
        >
          {kubeBenchMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Iniciando scan...
            </>
          ) : (
            <>
              <CheckSquare className="w-4 h-4" />
              Ejecutar Kube-bench
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




