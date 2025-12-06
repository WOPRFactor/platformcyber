import React, { useState } from 'react'
import { Building2, Loader2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { cloudAPI } from '../../lib/api/cloud'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../pages/VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../CommandPreviewModal'

interface AzureHoundSectionProps {
  workspaceId: number
}

export const AzureHoundSection: React.FC<AzureHoundSectionProps> = ({ workspaceId }) => {
  const { startTask, addLog, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview
  
  const [tenantId, setTenantId] = useState('')
  const [authMethod, setAuthMethod] = useState<'username' | 'token'>('username')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [accessToken, setAccessToken] = useState('')

  const azureHoundMutation = useMutation({
    mutationFn: () => {
      if (!workspaceId || !tenantId) {
        throw new Error('Workspace y Tenant ID son requeridos')
      }
      if (authMethod === 'username' && (!username || !password)) {
        throw new Error('Username y password son requeridos')
      }
      if (authMethod === 'token' && !accessToken) {
        throw new Error('Access token es requerido')
      }
      
      return cloudAPI.startAzureHoundCollection(
        tenantId,
        workspaceId,
        authMethod === 'username' ? username : undefined,
        authMethod === 'username' ? password : undefined,
        authMethod === 'token' ? accessToken : undefined
      )
    },
    onMutate: () => {
      const taskId = startTask('Cloud Pentesting', `AzureHound: ${tenantId}`)
      addLog('info', 'cloud', `Iniciando AzureHound para tenant ${tenantId}`, taskId, `azurehound -t ${tenantId}`)
      updateTaskProgress(taskId, 10, 'Iniciando AzureHound...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`AzureHound iniciado: ${data.scan_id}`)
      queryClient.invalidateQueries({ queryKey: ['cloud-scans'] })
      if (context?.taskId) {
        updateTaskProgress(context.taskId, 25, 'Scan enviado al backend')
        addLog('info', 'cloud', `Scan iniciado: ${data.scan_id}`, context.taskId)
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar AzureHound: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const handleAzureHoundWithPreview = async () => {
    if (!workspaceId || !tenantId) {
      toast.error('Workspace y Tenant ID son requeridos')
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
      const preview = await commandPreviewAPI.previewAzureHoundCollection({
        tenant_id: tenantId,
        workspace_id: workspaceId,
        username: authMethod === 'username' ? username : undefined,
        password: authMethod === 'username' ? password : undefined,
        access_token: authMethod === 'token' ? accessToken : undefined
      })

      commandPreview.openPreview(preview, 'AzureHound Collection', async () => {
        await azureHoundMutation.mutateAsync()
      })
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error.message || 'Error desconocido'}`)
    }
  }

  return (
    <div className="mt-4">
      <div className="bg-gray-900 border border-blue-500 rounded-lg p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-blue-400 flex items-center gap-2">
            <Building2 className="w-5 h-5" />
            AzureHound - Azure AD Enumeration
          </h3>
          <p className="text-blue-600">
            Enumera y analiza la estructura de Azure Active Directory
          </p>
        </div>

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Tenant ID *
            </label>
            <input
              type="text"
              value={tenantId}
              onChange={(e) => setTenantId(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Método de autenticación
            </label>
            <select
              value={authMethod}
              onChange={(e) => setAuthMethod(e.target.value as 'username' | 'token')}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="username">Username/Password</option>
              <option value="token">Access Token</option>
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
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="user@domain.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="••••••••"
                />
              </div>
            </>
          )}

          {authMethod === 'token' && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Access Token
              </label>
              <textarea
                value={accessToken}
                onChange={(e) => setAccessToken(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                placeholder="eyJ0eXAiOiJKV1QiLCJhbGc..."
              />
            </div>
          )}
        </div>

        <button
          onClick={handleAzureHoundWithPreview}
          disabled={
            azureHoundMutation.isPending || 
            !tenantId || 
            (authMethod === 'username' && (!username || !password)) ||
            (authMethod === 'token' && !accessToken)
          }
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2"
        >
          {azureHoundMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Iniciando collection...
            </>
          ) : (
            <>
              <Building2 className="w-4 h-4" />
              Ejecutar AzureHound
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




