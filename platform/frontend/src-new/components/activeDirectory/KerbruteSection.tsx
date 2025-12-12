import React, { useState } from 'react'
import { Key, Loader2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { activeDirectoryAPI } from '../../lib/api/activeDirectory'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../pages/VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../CommandPreviewModal'

interface KerbruteSectionProps {
  workspaceId: number
}

export const KerbruteSection: React.FC<KerbruteSectionProps> = ({ workspaceId }) => {
  const { startTask, addLog, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview
  
  const [action, setAction] = useState<'userenum' | 'passwordspray'>('userenum')
  const [domain, setDomain] = useState('')
  const [dcIp, setDcIp] = useState('')
  const [userlist, setUserlist] = useState('')
  const [password, setPassword] = useState('')

  const kerbruteMutation = useMutation({
    mutationFn: () => {
      if (!workspaceId || !domain || !dcIp || !userlist) {
        throw new Error('Todos los campos son requeridos')
      }
      if (action === 'passwordspray' && !password) {
        throw new Error('Password es requerido para password spraying')
      }
      
      if (action === 'userenum') {
        return activeDirectoryAPI.startKerbruteUserEnum(domain, dcIp, userlist, workspaceId)
      } else {
        return activeDirectoryAPI.startKerbrutePasswordSpray(domain, dcIp, userlist, password, workspaceId)
      }
    },
    onMutate: () => {
      const taskId = startTask('Active Directory', `Kerbrute: ${action}`)
      addLog('info', 'active_directory', `Iniciando Kerbrute ${action} en ${domain}`, taskId, `kerbrute ${action} -d ${domain}`)
      updateTaskProgress(taskId, 10, 'Iniciando Kerbrute...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`Kerbrute iniciado: ${data.scan_id}`)
      queryClient.invalidateQueries({ queryKey: ['ad-scans'] })
      if (context?.taskId) {
        updateTaskProgress(context.taskId, 25, 'Scan enviado al backend')
        addLog('info', 'active_directory', `Scan iniciado: ${data.scan_id}`, context.taskId)
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar Kerbrute: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const handleKerbruteWithPreview = async () => {
    if (!workspaceId || !domain || !dcIp || !userlist) {
      toast.error('Todos los campos son requeridos')
      return
    }
    if (action === 'passwordspray' && !password) {
      toast.error('Password es requerido para password spraying')
      return
    }

    try {
      let preview
      if (action === 'userenum') {
        preview = await commandPreviewAPI.previewKerbruteUserEnum({
          domain,
          dc_ip: dcIp,
          userlist,
          workspace_id: workspaceId
        })
      } else {
        preview = await commandPreviewAPI.previewKerbrutePasswordSpray({
          domain,
          dc_ip: dcIp,
          userlist,
          password,
          workspace_id: workspaceId
        })
      }

      commandPreview.openPreview(preview, `Kerbrute ${action}`, async () => {
        await kerbruteMutation.mutateAsync()
      })
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error.message || 'Error desconocido'}`)
    }
  }

  return (
    <div className="mt-4">
      <div className="bg-gray-50 border border-red-500 rounded-xl p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
            <Key className="w-5 h-5" />
            Kerbrute - User Enumeration & Password Spraying
          </h3>
          <p className="text-red-600">
            Enumera usuarios válidos y realiza password spraying en Active Directory
          </p>
        </div>

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Acción
            </label>
            <select
              value={action}
              onChange={(e) => setAction(e.target.value as 'userenum' | 'passwordspray')}
              className="w-full bg-white border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <option value="userenum">User Enumeration</option>
              <option value="passwordspray">Password Spraying</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Dominio
            </label>
            <input
              type="text"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="w-full bg-white border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              DC IP
            </label>
            <input
              type="text"
              value={dcIp}
              onChange={(e) => setDcIp(e.target.value)}
              className="w-full bg-white border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="192.168.1.10"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Lista de usuarios
              <span className="text-xs text-gray-500 ml-2">Path al archivo de usuarios</span>
            </label>
            <input
              type="text"
              value={userlist}
              onChange={(e) => setUserlist(e.target.value)}
              className="w-full bg-white border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="/path/to/users.txt"
            />
          </div>

          {action === 'passwordspray' && (
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-white border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
                placeholder="Password123!"
              />
            </div>
          )}
        </div>

        <button
          onClick={handleKerbruteWithPreview}
          disabled={kerbruteMutation.isPending || !domain || !dcIp || !userlist || (action === 'passwordspray' && !password)}
          className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
        >
          {kerbruteMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Iniciando scan...
            </>
          ) : (
            <>
              <Key className="w-4 h-4" />
              Ejecutar Kerbrute
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








