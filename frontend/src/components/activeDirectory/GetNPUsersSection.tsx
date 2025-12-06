import React, { useState } from 'react'
import { UserSearch, Loader2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { activeDirectoryAPI } from '../../lib/api/activeDirectory'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../pages/VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../CommandPreviewModal'

interface GetNPUsersSectionProps {
  workspaceId: number
}

export const GetNPUsersSection: React.FC<GetNPUsersSectionProps> = ({ workspaceId }) => {
  const { startTask, addLog, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview
  
  const [domain, setDomain] = useState('')
  const [dcIp, setDcIp] = useState('')
  const [authMethod, setAuthMethod] = useState<'username' | 'usersfile'>('username')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [usersfile, setUsersfile] = useState('')
  const [noPass, setNoPass] = useState(true)

  const getNPUsersMutation = useMutation({
    mutationFn: () => {
      if (!workspaceId || !domain) {
        throw new Error('Workspace y dominio son requeridos')
      }
      if (authMethod === 'username' && !username) {
        throw new Error('Username es requerido')
      }
      if (authMethod === 'usersfile' && !usersfile) {
        throw new Error('Archivo de usuarios es requerido')
      }
      
      return activeDirectoryAPI.startGetNPUsers(
        domain,
        workspaceId,
        authMethod === 'username' ? username : undefined,
        authMethod === 'username' ? password : undefined,
        dcIp || undefined,
        authMethod === 'usersfile' ? usersfile : undefined,
        noPass
      )
    },
    onMutate: () => {
      const taskId = startTask('Active Directory', `GetNPUsers: ${domain}`)
      addLog('info', 'active_directory', `Iniciando AS-REP Roasting en ${domain}`, taskId, `GetNPUsers.py ${domain}`)
      updateTaskProgress(taskId, 10, 'Iniciando GetNPUsers...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`GetNPUsers iniciado: ${data.scan_id}`)
      queryClient.invalidateQueries({ queryKey: ['ad-scans'] })
      if (context?.taskId) {
        updateTaskProgress(context.taskId, 25, 'Scan enviado al backend')
        addLog('info', 'active_directory', `Scan iniciado: ${data.scan_id}`, context.taskId)
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar GetNPUsers: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const handleGetNPUsersWithPreview = async () => {
    if (!workspaceId || !domain) {
      toast.error('Workspace y dominio son requeridos')
      return
    }
    if (authMethod === 'username' && !username) {
      toast.error('Username es requerido')
      return
    }
    if (authMethod === 'usersfile' && !usersfile) {
      toast.error('Archivo de usuarios es requerido')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewGetNPUsers({
        domain,
        workspace_id: workspaceId,
        username: authMethod === 'username' ? username : undefined,
        password: authMethod === 'username' ? password : undefined,
        dc_ip: dcIp || undefined,
        usersfile: authMethod === 'usersfile' ? usersfile : undefined,
        no_pass: noPass
      })

      commandPreview.openPreview(preview, 'GetNPUsers (AS-REP Roasting)', async () => {
        await getNPUsersMutation.mutateAsync()
      })
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error.message || 'Error desconocido'}`)
    }
  }

  return (
    <div className="mt-4">
      <div className="bg-gray-900 border border-red-500 rounded-lg p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
            <UserSearch className="w-5 h-5" />
            GetNPUsers - AS-REP Roasting
          </h3>
          <p className="text-red-600">
            Extrae hashes AS-REP de usuarios que no requieren pre-autenticación Kerberos
          </p>
        </div>

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Dominio *
            </label>
            <input
              type="text"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              DC IP (opcional)
            </label>
            <input
              type="text"
              value={dcIp}
              onChange={(e) => setDcIp(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="192.168.1.10"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Método de autenticación
            </label>
            <select
              value={authMethod}
              onChange={(e) => setAuthMethod(e.target.value as 'username' | 'usersfile')}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <option value="username">Username/Password</option>
              <option value="usersfile">Archivo de usuarios</option>
            </select>
          </div>

          {authMethod === 'username' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
                  placeholder="user"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Password (opcional)
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
                  placeholder="••••••••"
                />
              </div>
            </>
          )}

          {authMethod === 'usersfile' && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Archivo de usuarios
                <span className="text-xs text-gray-500 ml-2">Path al archivo con lista de usuarios</span>
              </label>
              <input
                type="text"
                value={usersfile}
                onChange={(e) => setUsersfile(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
                placeholder="/path/to/users.txt"
              />
            </div>
          )}

          <div className="flex items-center">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={noPass}
                onChange={(e) => setNoPass(e.target.checked)}
                className="w-4 h-4 text-red-600 bg-gray-800 border-gray-700 rounded focus:ring-red-500"
              />
              <span className="ml-2 text-sm text-gray-300">No requerir password (no-pass)</span>
            </label>
          </div>
        </div>

        <button
          onClick={handleGetNPUsersWithPreview}
          disabled={
            getNPUsersMutation.isPending || 
            !domain || 
            (authMethod === 'username' && !username) ||
            (authMethod === 'usersfile' && !usersfile)
          }
          className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2"
        >
          {getNPUsersMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Iniciando scan...
            </>
          ) : (
            <>
              <UserSearch className="w-4 h-4" />
              Ejecutar GetNPUsers
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




