import React, { useState } from 'react'
import { Package, Loader2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { containerAPI } from '../../lib/api/container'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../pages/VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../CommandPreviewModal'

interface GrypeSectionProps {
  workspaceId: number
}

export const GrypeSection: React.FC<GrypeSectionProps> = ({ workspaceId }) => {
  const { startTask, addLog, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview
  
  const [image, setImage] = useState('')
  const [scope, setScope] = useState('all-layers')

  const grypeMutation = useMutation({
    mutationFn: () => {
      if (!image.trim() || !workspaceId) {
        throw new Error('Imagen y workspace son requeridos')
      }
      return containerAPI.scanImageGrype(image, workspaceId, scope)
    },
    onMutate: () => {
      const taskId = startTask('Container Security', `Grype scan: ${image}`)
      addLog('info', 'container', `Iniciando Grype scan para ${image}`, taskId, `grype ${image}`)
      updateTaskProgress(taskId, 10, 'Iniciando Grype scan...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`Grype scan iniciado: ${data.scan_id}`)
      queryClient.invalidateQueries({ queryKey: ['container-scans'] })
      if (context?.taskId) {
        updateTaskProgress(context.taskId, 25, 'Scan enviado al backend')
        addLog('info', 'container', `Scan iniciado: ${data.scan_id}`, context.taskId)
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar Grype scan: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const handleGrypeWithPreview = async () => {
    if (!image.trim() || !workspaceId) {
      toast.error('Imagen y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewGrypeScan({
        image: image.trim(),
        workspace_id: workspaceId,
        scope
      })

      commandPreview.openPreview(preview, 'Grype Scan', async () => {
        await grypeMutation.mutateAsync()
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
            <Package className="w-5 h-5" />
            Grype - Container Vulnerability Scanner
          </h3>
          <p className="text-purple-600">
            Escanea imágenes de contenedores en busca de vulnerabilidades conocidas
          </p>
        </div>

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Imagen Docker
              <span className="text-xs text-gray-500 ml-2">Ej: nginx:latest, ubuntu:20.04</span>
            </label>
            <input
              type="text"
              value={image}
              onChange={(e) => setImage(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="nginx:latest"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Scope
            </label>
            <select
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="all-layers">All Layers</option>
              <option value="squashed">Squashed</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleGrypeWithPreview}
          disabled={grypeMutation.isPending || !image.trim()}
          className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2"
        >
          {grypeMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Iniciando scan...
            </>
          ) : (
            <>
              <Package className="w-4 h-4" />
              Ejecutar Grype Scan
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

