import React, { useState } from 'react'
import { FileText, Loader2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { containerAPI } from '../../lib/api/container'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../pages/VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../CommandPreviewModal'

interface SyftSectionProps {
  workspaceId: number
}

export const SyftSection: React.FC<SyftSectionProps> = ({ workspaceId }) => {
  const { startTask, addLog, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview
  
  const [image, setImage] = useState('')
  const [outputFormat, setOutputFormat] = useState('spdx-json')

  const syftMutation = useMutation({
    mutationFn: () => {
      if (!image.trim() || !workspaceId) {
        throw new Error('Imagen y workspace son requeridos')
      }
      return containerAPI.generateSBOM(image, workspaceId, outputFormat)
    },
    onMutate: () => {
      const taskId = startTask('Container Security', `Syft SBOM: ${image}`)
      addLog('info', 'container', `Generando SBOM con Syft para ${image}`, taskId, `syft ${image}`)
      updateTaskProgress(taskId, 10, 'Generando SBOM...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`SBOM generado: ${data.scan_id}`)
      queryClient.invalidateQueries({ queryKey: ['container-scans'] })
      if (context?.taskId) {
        updateTaskProgress(context.taskId, 25, 'SBOM generado')
        addLog('info', 'container', `SBOM generado: ${data.scan_id}`, context.taskId)
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al generar SBOM: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const handleSyftWithPreview = async () => {
    if (!image.trim() || !workspaceId) {
      toast.error('Imagen y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewSyftSBOM({
        image: image.trim(),
        workspace_id: workspaceId,
        output_format: outputFormat
      })

      commandPreview.openPreview(preview, 'Syft SBOM', async () => {
        await syftMutation.mutateAsync()
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
            <FileText className="w-5 h-5" />
            Syft - SBOM Generator
          </h3>
          <p className="text-purple-600">
            Genera Software Bill of Materials (SBOM) para imágenes de contenedores
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
              Formato de salida
            </label>
            <select
              value={outputFormat}
              onChange={(e) => setOutputFormat(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="spdx-json">SPDX JSON</option>
              <option value="spdx-tag-value">SPDX Tag-Value</option>
              <option value="cyclonedx-json">CycloneDX JSON</option>
              <option value="cyclonedx-xml">CycloneDX XML</option>
              <option value="syft-json">Syft JSON</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleSyftWithPreview}
          disabled={syftMutation.isPending || !image.trim()}
          className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2"
        >
          {syftMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Generando SBOM...
            </>
          ) : (
            <>
              <FileText className="w-4 h-4" />
              Generar SBOM
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





