import React, { useState } from 'react'
import { Route, Loader2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { cloudAPI } from '../../lib/api/cloud'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../pages/VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../CommandPreviewModal'

interface ROADtoolsSectionProps {
  workspaceId: number
}

export const ROADtoolsSection: React.FC<ROADtoolsSectionProps> = ({ workspaceId }) => {
  const { startTask, addLog, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview
  
  const [authMethod, setAuthMethod] = useState<'username' | 'token' | 'device'>('username')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [accessToken, setAccessToken] = useState('')
  const [tenantId, setTenantId] = useState('')

  const roadtoolsMutation = useMutation({
    mutationFn: () => {
      if (!workspaceId) {
        throw new Error('Workspace es requerido')
      }
      if (authMethod === 'username' && (!username || !password)) {
        throw new Error('Username y password son requeridos')
      }
      if (authMethod === 'token' && !accessToken) {
        throw new Error('Access token es requerido')
      }
      
      return cloudAPI.startROADtoolsGather(
        workspaceId,
        authMethod === 'username' ? username : undefined,
        authMethod === 'username' ? password : undefined,
        authMethod === 'token' ? accessToken : undefined,
        tenantId || undefined
      )
    },
    onMutate: () => {
      const taskId = startTask('Cloud Pentesting', 'ROADtools: gather')
      addLog('info', 'cloud', 'Iniciando ROADtools gather', taskId, 'roadrecon gather')
      updateTaskProgress(taskId, 10, 'Iniciando ROADtools...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`ROADtools iniciado: ${data.scan_id}`)
      queryClient.invalidateQueries({ queryKey: ['cloud-scans'] })
      if (context?.taskId) {
        updateTaskProgress(context.taskId, 25, 'Gather enviado al backend')
        addLog('info', 'cloud', `Gather iniciado: ${data.scan_id}`, context.taskId)
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar ROADtools: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const handleROADtoolsWithPreview = async () => {
    if (!workspaceId) {
      toast.error('Workspace es requerido')
      return
    }
    if (authMethod === 'username' && (!username || !password)) {
      toast.error('Username y password son requeridos')
      return
    }
    if (authMethod === 'token' && !accessToken) {
      toast.error('Access token es requerido')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewROADtoolsGather({
        workspace_id: workspaceId,
        username: authMethod === 'username' ? username : undefined,
        password: authMethod === 'username' ? password : undefined,
        access_token: authMethod === 'token' ? accessToken : undefined,
        tenant_id: tenantId || undefined
      })

      commandPreview.openPreview(preview, 'ROADtools Gather', async () => {
        await roadtoolsMutation.mutateAsync()
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
            <Route className="w-5 h-5" />
            ROADtools - Azure AD Analysis
          </h3>
          <p className="text-blue-600">
            Recopila y analiza datos de Azure Active Directory
          </p>
        </div>

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Método de autenticación
            </label>
            <select
              value={authMethod}
              onChange={(e) => setAuthMethod(e.target.value as 'username' | 'token' | 'device')}
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="username">Username/Password</option>
              <option value="token">Access Token</option>
              <option value="device">Device Code</option>
            </select>
          </div>

          {authMethod === 'username' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="user@domain.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="••••••••"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  Tenant ID (opcional)
                </label>
                <input
                  type="text"
                  value={tenantId}
                  onChange={(e) => setTenantId(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                />
              </div>
            </>
          )}

          {authMethod === 'token' && (
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                Access Token
              </label>
              <textarea
                value={accessToken}
                onChange={(e) => setAccessToken(e.target.value)}
                className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                placeholder="eyJ0eXAiOiJKV1QiLCJhbGc..."
              />
            </div>
          )}

          {authMethod === 'device' && (
            <div className="bg-blue-900 border border-blue-700 rounded-xl p-4">
              <p className="text-blue-300 text-sm">
                Se usará autenticación por device code. Se mostrará un código en la consola que deberás ingresar en el navegador.
              </p>
            </div>
          )}
        </div>

        <button
          onClick={handleROADtoolsWithPreview}
          disabled={
            roadtoolsMutation.isPending || 
            (authMethod === 'username' && (!username || !password)) ||
            (authMethod === 'token' && !accessToken)
          }
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
        >
          {roadtoolsMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Iniciando gather...
            </>
          ) : (
            <>
              <Route className="w-4 h-4" />
              Ejecutar ROADtools
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








