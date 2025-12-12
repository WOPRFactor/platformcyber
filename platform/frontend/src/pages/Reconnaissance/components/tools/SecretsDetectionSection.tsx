import React, { useState } from 'react'
import { Key, Loader2 } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { reconnaissanceAPI } from '../../../../lib/api/reconnaissance'
import { commandPreviewAPI } from '../../../../lib/api/command-preview'
import { toast } from 'sonner'
import { useCommandPreview } from '../../../VulnerabilityAssessment/hooks/useCommandPreview'
import { useReconnaissanceScan } from '../../hooks/useReconnaissanceScan'

interface SecretsDetectionSectionProps {
  workspaceId: number
  commandPreview: ReturnType<typeof useCommandPreview>
}

export const SecretsDetectionSection: React.FC<SecretsDetectionSectionProps> = ({ workspaceId, commandPreview }) => {
  const { startReconScan } = useReconnaissanceScan()
  const { openPreview } = commandPreview
  const [repoUrl, setRepoUrl] = useState('')

  const secretsMutation = useMutation({
    mutationFn: (repoUrl: string, tool: string = 'gitleaks') => startReconScan(
      'Secrets Detection',
      () => reconnaissanceAPI.secrets(repoUrl, workspaceId, tool),
      `secrets ${repoUrl}`,
      repoUrl
    )
  })

  const handleSecretsWithPreview = async (repoUrl: string, tool: string = 'gitleaks') => {
    if (!repoUrl.trim() || !workspaceId) {
      toast.error('URL de repositorio y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewSecrets({
        repo_url: repoUrl,
        workspace_id: workspaceId,
        tool: tool
      })

      openPreview(preview, `Secrets Detection (${tool})`, async () => {
        await startReconScan(
          'Secrets Detection',
          () => reconnaissanceAPI.secrets(preview.parameters.repo_url, workspaceId, preview.parameters.tool),
          preview.command_string,
          preview.parameters.repo_url
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  return (
    <div className="mt-4">
      <div className="bg-gray-900 border border-green-500 rounded-lg p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-green-400 flex items-center gap-2">
            <Key className="w-5 h-5" />
            Secrets Detection
          </h3>
          <p className="text-green-600">
            Detecta secrets y credenciales en repositorios Git
          </p>
        </div>

        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <h4 className="text-md font-semibold text-pink-400 mb-2">Repositorio Git</h4>
            <p className="text-sm text-gray-400 mb-3">
              Ingresa la URL del repositorio a analizar
            </p>
            <input
              type="text"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/user/repo"
              className="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-gray-300 mb-3"
            />
            <div className="grid grid-cols-2 gap-2">
              {['gitleaks', 'trufflehog'].map((tool) => (
                <button
                  key={tool}
                  onClick={() => {
                    if (!repoUrl.trim()) {
                      toast.error('Por favor ingresa una URL de repositorio')
                      return
                    }
                    handleSecretsWithPreview(repoUrl, tool)
                  }}
                  disabled={secretsMutation.isPending}
                  className="bg-pink-600 hover:bg-pink-700 disabled:bg-pink-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2"
                >
                  {secretsMutation.isPending ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Key className="w-4 h-4" />
                  )}
                  {tool.charAt(0).toUpperCase() + tool.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

