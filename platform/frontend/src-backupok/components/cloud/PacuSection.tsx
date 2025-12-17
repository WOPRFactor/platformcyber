import React, { useState } from 'react'
import { Cloud, Loader2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { cloudAPI } from '../../lib/api/cloud'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../pages/VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../CommandPreviewModal'

interface PacuSectionProps {
  workspaceId: number
}

export const PacuSection: React.FC<PacuSectionProps> = ({ workspaceId }) => {
  const { startTask, addLog, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview
  
  const [moduleName, setModuleName] = useState('iam__enum_permissions')
  const [awsProfile, setAwsProfile] = useState('')

  const pacuMutation = useMutation({
    mutationFn: () => {
      if (!workspaceId) {
        throw new Error('Workspace es requerido')
      }
      return cloudAPI.startPacuModule(moduleName, workspaceId, awsProfile || undefined)
    },
    onMutate: () => {
      const taskId = startTask('Cloud Pentesting', `Pacu: ${moduleName}`)
      addLog('info', 'cloud', `Iniciando Pacu módulo ${moduleName}`, taskId, `pacu --exec "run ${moduleName}"`)
      updateTaskProgress(taskId, 10, 'Iniciando Pacu...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`Pacu iniciado: ${data.scan_id}`)
      queryClient.invalidateQueries({ queryKey: ['cloud-scans'] })
      if (context?.taskId) {
        updateTaskProgress(context.taskId, 25, 'Módulo enviado al backend')
        addLog('info', 'cloud', `Scan iniciado: ${data.scan_id}`, context.taskId)
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar Pacu: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const handlePacuWithPreview = async () => {
    if (!workspaceId) {
      toast.error('Workspace es requerido')
      return
    }
    if (!moduleName.trim()) {
      toast.error('Nombre del módulo es requerido')
      return
    }

    try {
      console.log('🔍 [PacuSection] Solicitando preview:', {
        module_name: moduleName,
        workspace_id: workspaceId,
        aws_profile: awsProfile
      })
      
      const preview = await commandPreviewAPI.previewPacuModule({
        module_name: moduleName,
        workspace_id: workspaceId,
        aws_profile: awsProfile || undefined
      })

      console.log('✅ [PacuSection] Preview recibido:', preview)
      
      commandPreview.openPreview(preview, 'Pacu Module', async () => {
        await pacuMutation.mutateAsync()
      })
    } catch (error: any) {
      console.error('❌ [PacuSection] Error al obtener preview:', error)
      toast.error(`Error al obtener preview: ${error.message || 'Error desconocido'}`)
    }
  }

  return (
    <div className="mt-4">
      <div className="bg-gray-50 border border-blue-500 rounded-xl p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-blue-400 flex items-center gap-2">
            <Cloud className="w-5 h-5" />
            Pacu - AWS Pentesting Framework
          </h3>
          <p className="text-blue-600">
            Framework de pentesting para AWS con múltiples módulos de ataque
          </p>
        </div>

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Módulo Pacu
              <span className="text-xs text-gray-500 ml-2">Ej: iam__enum_permissions, s3__enum</span>
            </label>
            <input
              type="text"
              value={moduleName}
              onChange={(e) => setModuleName(e.target.value)}
              className="w-full bg-white border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="iam__enum_permissions"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              AWS Profile (opcional)
              <span className="text-xs text-gray-500 ml-2">Perfil de credenciales AWS</span>
            </label>
            <input
              type="text"
              value={awsProfile}
              onChange={(e) => setAwsProfile(e.target.value)}
              className="w-full bg-white border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="default"
            />
          </div>
        </div>

        <button
          onClick={handlePacuWithPreview}
          disabled={pacuMutation.isPending || !moduleName.trim()}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
        >
          {pacuMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Iniciando módulo...
            </>
          ) : (
            <>
              <Cloud className="w-4 h-4" />
              Ejecutar Módulo Pacu
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
        onExecute={async (parameters: Record<string, any>) => {
          // Los parámetros ya están en el estado del componente, solo ejecutar
          await executePreview()
        }}
      />
    </div>
  )
}


