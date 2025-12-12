import React, { useState } from 'react'
import { FolderOpen, Loader, Eye } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { DirectoriesList } from '../shared/DirectoriesList'
import { integrationsAPI } from '../../../../lib/api/integrations'
import { useWorkspace } from '../../../../contexts/WorkspaceContext'
import { useCommandPreview } from '../../../VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../../../../components/CommandPreviewModal'

interface DirectoryResult {
  url?: string
  status_code?: string
  size?: string
}

export const GobusterSection: React.FC = () => {
  const { currentWorkspace } = useWorkspace()
  const [gobusterUrl, setGobusterUrl] = useState('')
  const [gobusterWordlist, setGobusterWordlist] = useState('common')
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview, openPreview } = commandPreview

  const directoryBustingMutation = useMutation({
    mutationFn: () => {
      if (!currentWorkspace?.id) {
        throw new Error('Workspace no seleccionado')
      }
      return integrationsAPI.directoryBusting(gobusterUrl, gobusterWordlist, currentWorkspace.id)
    },
    onSuccess: () => {
      toast.success('Directory busting ejecutado correctamente')
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`)
    }
  })

  const handleGobusterWithPreview = async () => {
    if (!currentWorkspace?.id) {
      toast.error('Workspace no seleccionado')
      return
    }
    if (!gobusterUrl.trim()) {
      toast.error('URL es requerida')
      return
    }

    try {
      const preview = await integrationsAPI.previewGobusterDirectory(gobusterUrl, gobusterWordlist, currentWorkspace.id)
      openPreview(preview, 'Gobuster', async () => {
        await directoryBustingMutation.mutateAsync()
      })
    } catch (error: any) {
      toast.error(`Error obteniendo preview: ${error.message}`)
    }
  }

  return (
    <div className="bg-gray-900 border border-red-500 rounded-lg p-6">
      <h3 className="text-lg font-bold text-red-400 mb-4 flex items-center gap-2">
        <FolderOpen className="w-5 h-5" />
        Directory Busting
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-green-400 mb-2">URL Base</label>
          <input
            type="url"
            value={gobusterUrl}
            onChange={(e) => setGobusterUrl(e.target.value)}
            placeholder="https://example.com"
            className="w-full bg-gray-900 border border-green-500 rounded px-3 py-2 text-green-400 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-green-400 mb-2">Wordlist</label>
          <select
            value={gobusterWordlist}
            onChange={(e) => setGobusterWordlist(e.target.value)}
            className="w-full bg-gray-900 border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="common">Common (874 palabras)</option>
            <option value="big">Big (204.689 palabras)</option>
            <option value="small">Small (34 palabras)</option>
          </select>
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleGobusterWithPreview}
          disabled={directoryBustingMutation.isPending || !gobusterUrl.trim()}
          className="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {directoryBustingMutation.isPending ? (
            <Loader className="w-4 h-4 animate-spin mr-2" />
          ) : (
            <FolderOpen className="w-4 h-4 mr-2" />
          )}
          Ejecutar Directory Busting
        </button>
        <button
          onClick={handleGobusterWithPreview}
          disabled={!gobusterUrl.trim()}
          className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 disabled:opacity-50"
        >
          <Eye className="w-4 h-4" />
          Preview
        </button>
      </div>

      {directoryBustingMutation.data && (
        <div className="mt-6">
          <div className="bg-gray-800 border border-green-500 rounded-lg p-6 mb-4">
            <h4 className="font-semibold mb-4 text-green-400">Resumen de Directory Busting</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{directoryBustingMutation.data?.directories_found || 0}</div>
                <div className="text-sm text-gray-600">Directorios</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {directoryBustingMutation.data?.directories?.filter((d: DirectoryResult) => d.status_code?.startsWith('2')).length || 0}
                </div>
                <div className="text-sm text-gray-600">200 OK</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {directoryBustingMutation.data?.directories?.filter((d: DirectoryResult) => d.status_code?.startsWith('3')).length || 0}
                </div>
                <div className="text-sm text-gray-600">Redirects</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {directoryBustingMutation.data?.directories?.filter((d: DirectoryResult) => d.status_code?.startsWith('4')).length || 0}
                </div>
                <div className="text-sm text-gray-600">Forbidden</div>
              </div>
            </div>
            <div className="mt-4">
              <p className="text-sm text-gray-600">
                Wordlist usada: <span className="font-semibold">{directoryBustingMutation.data?.wordlist}</span>
              </p>
            </div>
          </div>

          {directoryBustingMutation.data?.directories && directoryBustingMutation.data.directories.length > 0 && (
            <div>
              <h4 className="font-semibold mb-2 text-red-400">Directorios Encontrados</h4>
              <DirectoriesList directories={directoryBustingMutation.data.directories} />
            </div>
          )}
        </div>
      )}

      <CommandPreviewModal
        isOpen={showPreview}
        onClose={closePreview}
        previewData={previewData}
        category="Integraciones Avanzadas"
        toolName={previewToolName}
        onExecute={async () => {
          await executePreview()
        }}
      />
    </div>
  )
}

