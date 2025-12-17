import React, { useState } from 'react'
import { Shield, Loader2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { cloudAPI } from '../../lib/api/cloud'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../pages/VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../CommandPreviewModal'

interface ProwlerSectionProps {
  workspaceId: number
}

export const ProwlerSection: React.FC<ProwlerSectionProps> = ({ workspaceId }) => {
  const { startTask, addLog, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview
  
  const [provider, setProvider] = useState('aws')
  const [profile, setProfile] = useState('')
  const [severity, setSeverity] = useState<string[]>(['critical', 'high'])
  const [compliance, setCompliance] = useState('')

  const prowlerMutation = useMutation({
    mutationFn: () => {
      if (!workspaceId) {
        throw new Error('Workspace es requerido')
      }
      return cloudAPI.startProwlerScan(
        provider, 
        workspaceId, 
        profile || undefined, 
        severity.length > 0 ? severity : undefined,
        compliance || undefined
      )
    },
    onMutate: () => {
      const taskId = startTask('Cloud Pentesting', `Prowler: ${provider}`)
      addLog('info', 'cloud', `Iniciando Prowler para ${provider}`, taskId, `prowler ${provider}`)
      updateTaskProgress(taskId, 10, 'Iniciando Prowler...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`Prowler iniciado: ${data.scan_id}`)
      queryClient.invalidateQueries({ queryKey: ['cloud-scans'] })
      if (context?.taskId) {
        updateTaskProgress(context.taskId, 25, 'Scan enviado al backend')
        addLog('info', 'cloud', `Scan iniciado: ${data.scan_id}`, context.taskId)
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar Prowler: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const handleProwlerWithPreview = async () => {
    if (!workspaceId) {
      toast.error('Workspace es requerido')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewProwlerScan({
        provider,
        workspace_id: workspaceId,
        profile: profile || undefined,
        severity: severity.length > 0 ? severity : undefined,
        compliance: compliance || undefined
      })

      commandPreview.openPreview(preview, 'Prowler Scan', async () => {
        await prowlerMutation.mutateAsync()
      })
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error.message || 'Error desconocido'}`)
    }
  }

  const toggleSeverity = (sev: string) => {
    setSeverity(prev => 
      prev.includes(sev) 
        ? prev.filter(s => s !== sev)
        : [...prev, sev]
    )
  }

  return (
    <div className="mt-4">
      <div className="bg-gray-100 border border-blue-500 rounded-xl p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-blue-400 flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Prowler - Cloud Security Scanner
          </h3>
          <p className="text-blue-600">
            Escáner de seguridad para AWS, Azure y GCP
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
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="aws">AWS</option>
              <option value="azure">Azure</option>
              <option value="gcp">GCP</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Profile (opcional)
            </label>
            <input
              type="text"
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="default"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Severidades
            </label>
            <div className="flex flex-wrap gap-2">
              {['critical', 'high', 'medium', 'low'].map(sev => (
                <button
                  key={sev}
                  onClick={() => toggleSeverity(sev)}
                  className={`px-3 py-1 rounded-md text-sm ${
                    severity.includes(sev)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-600 hover:bg-gray-600'
                  }`}
                >
                  {sev.charAt(0).toUpperCase() + sev.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Framework de Compliance (opcional)
              <span className="text-xs text-gray-500 ml-2">Ej: cis, hipaa, gdpr</span>
            </label>
            <input
              type="text"
              value={compliance}
              onChange={(e) => setCompliance(e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="cis"
            />
          </div>
        </div>

        <button
          onClick={handleProwlerWithPreview}
          disabled={prowlerMutation.isPending}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
        >
          {prowlerMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Iniciando scan...
            </>
          ) : (
            <>
              <Shield className="w-4 h-4" />
              Ejecutar Prowler
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








