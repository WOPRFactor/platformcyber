import React, { useState } from 'react'
import { Database, Loader2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { activeDirectoryAPI } from '../../lib/api/activeDirectory'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useConsole } from '../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../pages/VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../CommandPreviewModal'

interface LDAPDomainDumpSectionProps {
  workspaceId: number
}

export const LDAPDomainDumpSection: React.FC<LDAPDomainDumpSectionProps> = ({ workspaceId }) => {
  const { startTask, addLog, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview
  
  const [dcIp, setDcIp] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [domain, setDomain] = useState('')

  const ldapDumpMutation = useMutation({
    mutationFn: () => {
      if (!workspaceId || !dcIp || !username || !password || !domain) {
        throw new Error('Todos los campos son requeridos')
      }
      return activeDirectoryAPI.startLDAPDomainDump(dcIp, username, password, domain, workspaceId)
    },
    onMutate: () => {
      const taskId = startTask('Active Directory', `LDAP Domain Dump: ${domain}`)
      addLog('info', 'active_directory', `Iniciando LDAP Domain Dump en ${domain}`, taskId, `ldapdomaindump -u ${domain}\\${username}`)
      updateTaskProgress(taskId, 10, 'Iniciando LDAP Domain Dump...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      toast.success(`LDAP Domain Dump iniciado: ${data.scan_id}`)
      queryClient.invalidateQueries({ queryKey: ['ad-scans'] })
      if (context?.taskId) {
        updateTaskProgress(context.taskId, 25, 'Dump enviado al backend')
        addLog('info', 'active_directory', `Dump iniciado: ${data.scan_id}`, context.taskId)
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error al iniciar LDAP Domain Dump: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const handleLDAPDumpWithPreview = async () => {
    if (!workspaceId || !dcIp || !username || !password || !domain) {
      toast.error('Todos los campos son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewLDAPDomainDump({
        dc_ip: dcIp,
        username,
        password,
        domain,
        workspace_id: workspaceId
      })

      commandPreview.openPreview(preview, 'LDAP Domain Dump', async () => {
        await ldapDumpMutation.mutateAsync()
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
            <Database className="w-5 h-5" />
            LDAP Domain Dump
          </h3>
          <p className="text-red-600">
            Extrae toda la información del dominio Active Directory vía LDAP
          </p>
        </div>

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              DC IP *
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
              Username *
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
              Password *
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="••••••••"
            />
          </div>
        </div>

        <button
          onClick={handleLDAPDumpWithPreview}
          disabled={ldapDumpMutation.isPending || !dcIp || !username || !password || !domain}
          className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2"
        >
          {ldapDumpMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Iniciando dump...
            </>
          ) : (
            <>
              <Database className="w-4 h-4" />
              Ejecutar LDAP Domain Dump
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




