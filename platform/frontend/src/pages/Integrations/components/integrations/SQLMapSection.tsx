import React, { useState } from 'react'
import { Database, Loader, Eye } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { SQLMapFindings } from '../shared/SQLMapFindings'
import { integrationsAPI } from '../../../../lib/api/integrations'
import { useWorkspace } from '../../../../contexts/WorkspaceContext'
import { useCommandPreview } from '../../../VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../../../../components/CommandPreviewModal'

interface SQLMapFinding {
  severity?: string
  type?: string
  description?: string
  technique?: string
}

export const SQLMapSection: React.FC = () => {
  const { currentWorkspace } = useWorkspace()
  const [sqlmapUrl, setSqlmapUrl] = useState('')
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview, openPreview } = commandPreview

  const sqlmapMutation = useMutation({
    mutationFn: () => {
      if (!currentWorkspace?.id) {
        throw new Error('Workspace no seleccionado')
      }
      return integrationsAPI.advancedSQLMapScan(sqlmapUrl, currentWorkspace.id)
    },
    onSuccess: () => {
      toast.success('Escaneo SQLMap ejecutado correctamente')
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`)
    }
  })

  const handleSQLMapWithPreview = async () => {
    if (!currentWorkspace?.id) {
      toast.error('Workspace no seleccionado')
      return
    }
    if (!sqlmapUrl.trim()) {
      toast.error('URL es requerida')
      return
    }

    try {
      const preview = await integrationsAPI.previewSQLMapScan(sqlmapUrl, currentWorkspace.id)
      openPreview(preview, 'SQLMap', async () => {
        await sqlmapMutation.mutateAsync()
      })
    } catch (error: any) {
      toast.error(`Error obteniendo preview: ${error.message}`)
    }
  }

  return (
    <div className="bg-gray-100 border border-red-500 rounded-xl p-6">
      <h3 className="text-lg font-bold text-red-400 mb-4 flex items-center gap-2">
        <Database className="w-5 h-5" />
        Escaneo SQLMap Avanzado
      </h3>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-900 mb-2">URL Objetivo</label>
        <input
          type="url"
          value={sqlmapUrl}
          onChange={(e) => setSqlmapUrl(e.target.value)}
          placeholder="https://example.com/page?id=1"
          className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500"
        />
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleSQLMapWithPreview}
          disabled={sqlmapMutation.isPending || !sqlmapUrl.trim()}
          className="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {sqlmapMutation.isPending ? (
            <Loader className="w-4 h-4 animate-spin mr-2" />
          ) : (
            <Database className="w-4 h-4 mr-2" />
          )}
          Ejecutar SQLMap
        </button>
        <button
          onClick={handleSQLMapWithPreview}
          disabled={!sqlmapUrl.trim()}
          className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-xl flex items-center gap-2 disabled:opacity-50"
        >
          <Eye className="w-4 h-4" />
          Preview
        </button>
      </div>

      {sqlmapMutation.data && (
        <div className="mt-6">
          <div className="bg-gray-100 border border-gray-300 rounded-xl p-6 mb-4">
            <h4 className="font-semibold mb-4 text-gray-900">Resumen de SQLMap</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className={`text-2xl font-bold ${sqlmapMutation.data?.vulnerable ? 'text-red-600' : 'text-gray-500'}`}>
                  {sqlmapMutation.data?.vulnerable ? 'VULNERABLE' : 'SEGURO'}
                </div>
                <div className="text-sm text-gray-600">Estado</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{sqlmapMutation.data?.findings?.length || 0}</div>
                <div className="text-sm text-gray-600">Hallazgos</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {sqlmapMutation.data?.findings?.filter((f: SQLMapFinding) => f.severity === 'high').length || 0}
                </div>
                <div className="text-sm text-gray-600">Inyecciones</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {sqlmapMutation.data?.findings?.filter((f: SQLMapFinding) => f.type === 'sql_injection_technique').length || 0}
                </div>
                <div className="text-sm text-gray-600">Técnicas</div>
              </div>
            </div>
          </div>

          {sqlmapMutation.data?.findings && sqlmapMutation.data.findings.length > 0 && (
            <div>
              <h4 className="font-semibold mb-2 text-red-400">Vulnerabilidades Detectadas</h4>
              <SQLMapFindings findings={sqlmapMutation.data.findings} />
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

