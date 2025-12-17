import React, { useState } from 'react'
import { Network, Loader2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { activeDirectoryAPI } from '../../lib/api/activeDirectory'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../pages/VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../CommandPreviewModal'

interface CrackMapExecSectionProps {
  workspaceId: number
}

export const CrackMapExecSection: React.FC<CrackMapExecSectionProps> = ({ workspaceId }) => {
  const { startTask, addLog, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview
  
  const [action, setAction] = useState<'enum_users' | 'enum_groups'>('enum_users')
  const [dcIp, setDcIp] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [domain, setDomain] = useState('')

  const cmeMutation = useMutation({
    mutationFn: async () => {
      if (!workspaceId || !dcIp || !username || !password || !domain) {
        throw new Error('Todos los campos son requeridos')
      }
      
      if (action === 'enum_users') {
        return await activeDirectoryAPI.startCMEEnumUsers(dcIp, username, password, domain, workspaceId)
      } else {
        return await activeDirectoryAPI.startCMEEnumGroups(dcIp, username, password, domain, workspaceId)
      }
    },
    onMutate: () => {
      const taskId = startTask('Active Directory', `CrackMapExec: ${action} en ${domain}`)
      addLog('info', 'active_directory', `Iniciando CrackMapExec ${action} en ${domain}`, taskId, `crackmapexec ldap ${dcIp} -u ${username}`)
      updateTaskProgress(taskId, 10, 'Iniciando CrackMapExec...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`CrackMapExec iniciado: ${data.scan_id}`)
      queryClient.invalidateQueries({ queryKey: ['ad-scans'] })
      if (context?.taskId) {
        updateTaskProgress(context.taskId, 25, 'Scan enviado al backend')
        addLog('info', 'active_directory', `Scan iniciado: ${data.scan_id}`, context.taskId)
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar CrackMapExec: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const handleCMEWithPreview = async () => {
    if (!workspaceId || !dcIp || !username || !password || !domain) {
      toast.error('Todos los campos son requeridos')
      return
    }

    try {
      const preview = action === 'enum_users'
        ? await commandPreviewAPI.previewCMEEnumUsers({
            dc_ip: dcIp,
            username,
            password,
            domain,
            workspace_id: workspaceId
          })
        : await commandPreviewAPI.previewCMEEnumGroups({
            dc_ip: dcIp,
            username,
            password,
            domain,
            workspace_id: workspaceId
          })

      commandPreview.openPreview(preview, `CrackMapExec ${action}`, async () => {
        await cmeMutation.mutateAsync()
      })
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error.message || 'Error desconocido'}`)
    }
  }

  return (
    <div className="mt-4">
      <div className="bg-gray-100 border border-red-500 rounded-xl p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
            <Network className="w-5 h-5" />
            CrackMapExec - AD Enumeration
          </h3>
          <p className="text-red-600">
            Enumera usuarios y grupos de Active Directory
          </p>
        </div>

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Acción
            </label>
            <select
              value={action}
              onChange={(e) => setAction(e.target.value as 'enum_users' | 'enum_groups')}
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <option value="enum_users">Enum Users</option>
              <option value="enum_groups">Enum Groups</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              DC IP *
            </label>
            <input
              type="text"
              value={dcIp}
              onChange={(e) => setDcIp(e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="192.168.1.10"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Dominio *
            </label>
            <input
              type="text"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Username *
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="user"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Password *
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="••••••••"
            />
          </div>
        </div>

        <button
          onClick={handleCMEWithPreview}
          disabled={cmeMutation.isPending || !dcIp || !username || !password || !domain}
          className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
        >
          {cmeMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Iniciando scan...
            </>
          ) : (
            <>
              <Network className="w-4 h-4" />
              Ejecutar CrackMapExec
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


