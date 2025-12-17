import React, { useState } from 'react'
import { Search, Loader2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { cloudAPI } from '../../lib/api/cloud'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../pages/VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../CommandPreviewModal'

interface ScoutSuiteSectionProps {
  workspaceId: number
}

export const ScoutSuiteSection: React.FC<ScoutSuiteSectionProps> = ({ workspaceId }) => {
  const { startTask, addLog, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview
  
  const [provider, setProvider] = useState('aws')
  const [profile, setProfile] = useState('')
  const [regions, setRegions] = useState('')

  const scoutSuiteMutation = useMutation({
    mutationFn: () => {
      if (!workspaceId) {
        throw new Error('Workspace es requerido')
      }
      const regionsList = regions ? regions.split(',').map(r => r.trim()).filter(r => r) : undefined
      return cloudAPI.startScoutSuiteScan(provider, workspaceId, profile || undefined, regionsList)
    },
    onMutate: () => {
      const taskId = startTask('Cloud Pentesting', `ScoutSuite: ${provider}`)
      addLog('info', 'cloud', `Iniciando ScoutSuite para ${provider}`, taskId, `scout ${provider}`)
      updateTaskProgress(taskId, 10, 'Iniciando ScoutSuite...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`ScoutSuite iniciado: ${data.scan_id}`)
      queryClient.invalidateQueries({ queryKey: ['cloud-scans'] })
      if (context?.taskId) {
        updateTaskProgress(context.taskId, 25, 'Scan enviado al backend')
        addLog('info', 'cloud', `Scan iniciado: ${data.scan_id}`, context.taskId)
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar ScoutSuite: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const handleScoutSuiteWithPreview = async () => {
    if (!workspaceId) {
      toast.error('Workspace es requerido')
      return
    }

    try {
      const regionsList = regions ? regions.split(',').map(r => r.trim()).filter(r => r) : undefined
      const preview = await commandPreviewAPI.previewScoutSuiteScan({
        provider,
        workspace_id: workspaceId,
        profile: profile || undefined,
        regions: regionsList
      })

      commandPreview.openPreview(preview, 'ScoutSuite Scan', async () => {
        await scoutSuiteMutation.mutateAsync()
      })
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error.message || 'Error desconocido'}`)
    }
  }

  return (
    <div className="mt-4">
      <div className="bg-gray-100 border border-blue-500 rounded-xl p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-blue-400 flex items-center gap-2">
            <Search className="w-5 h-5" />
            ScoutSuite - Multi-cloud Security Audit
          </h3>
          <p className="text-blue-600">
            Auditoría de seguridad para múltiples proveedores cloud (AWS, Azure, GCP, etc.)
          </p>
        </div>

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Proveedor Cloud
            </label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
            >
              <option value="aws">AWS</option>
              <option value="azure">Azure</option>
              <option value="gcp">GCP</option>
              <option value="alibaba">Alibaba Cloud</option>
              <option value="oci">Oracle Cloud Infrastructure</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Profile (opcional)
              <span className="text-xs text-gray-500 ml-2">Perfil de credenciales</span>
            </label>
            <input
              type="text"
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
              placeholder="default"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Regiones (opcional)
              <span className="text-xs text-gray-500 ml-2">Separadas por comas: us-east-1,eu-west-1</span>
            </label>
            <input
              type="text"
              value={regions}
              onChange={(e) => setRegions(e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
              placeholder="us-east-1,eu-west-1"
            />
          </div>
        </div>

        <button
          onClick={handleScoutSuiteWithPreview}
          disabled={scoutSuiteMutation.isPending}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
        >
          {scoutSuiteMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Iniciando scan...
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              Ejecutar ScoutSuite
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








