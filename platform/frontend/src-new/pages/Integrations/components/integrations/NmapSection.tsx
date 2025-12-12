import React, { useState } from 'react'
import { Activity, Loader, Eye } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { NmapFindings } from '../shared/NmapFindings'
import { integrationsAPI } from '../../../../lib/api/integrations'
import { useWorkspace } from '../../../../contexts/WorkspaceContext'
import { useCommandPreview } from '../../../VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../../../../components/CommandPreviewModal'

interface NmapFinding {
  severity?: string
  type?: string
  port?: number
  protocol?: string
  service?: string
  state?: string
  os_details?: string
  description?: string
  details?: string
}

export const NmapSection: React.FC = () => {
  const { currentWorkspace } = useWorkspace()
  const [nmapTarget, setNmapTarget] = useState('')
  const [nmapScanType, setNmapScanType] = useState('comprehensive')
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview, openPreview } = commandPreview

  const advancedNmapMutation = useMutation({
    mutationFn: () => {
      if (!currentWorkspace?.id) {
        throw new Error('Workspace no seleccionado')
      }
      return integrationsAPI.advancedNmapScan(nmapTarget, nmapScanType, currentWorkspace.id)
    },
    onSuccess: () => {
      toast.success('Escaneo Nmap ejecutado correctamente')
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`)
    }
  })

  const handleNmapWithPreview = async () => {
    if (!currentWorkspace?.id) {
      toast.error('Workspace no seleccionado')
      return
    }
    if (!nmapTarget.trim()) {
      toast.error('Target es requerido')
      return
    }

    try {
      const preview = await integrationsAPI.previewNmapScan(nmapTarget, nmapScanType, currentWorkspace.id)
      openPreview(preview, 'Nmap Advanced', async () => {
        await advancedNmapMutation.mutateAsync()
      })
    } catch (error: any) {
      toast.error(`Error obteniendo preview: ${error.message}`)
    }
  }

  return (
    <div className="bg-gray-50 border border-red-500 rounded-xl p-6">
      <h3 className="text-lg font-bold text-red-400 mb-4 flex items-center gap-2">
        <Activity className="w-5 h-5" />
        Escaneo Nmap Avanzado
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-2">Objetivo</label>
          <input
            type="text"
            value={nmapTarget}
            onChange={(e) => setNmapTarget(e.target.value)}
            placeholder="192.168.1.0/24 o example.com"
            className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-2">Tipo de Escaneo</label>
          <select
            value={nmapScanType}
            onChange={(e) => setNmapScanType(e.target.value)}
            className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            <option value="quick">Rápido (-T4 -F)</option>
            <option value="service">Servicio (-sV -T4)</option>
            <option value="vulnerability">Vulnerabilidades (--script vuln)</option>
            <option value="os_detection">Detección OS (-O)</option>
            <option value="comprehensive">Completo (Todo)</option>
            <option value="stealth">Sigiloso (-sS -T3)</option>
            <option value="aggressive">Agresivo (-A -T4)</option>
          </select>
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleNmapWithPreview}
          disabled={advancedNmapMutation.isPending || !nmapTarget.trim()}
          className="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {advancedNmapMutation.isPending ? (
            <Loader className="w-4 h-4 animate-spin mr-2" />
          ) : (
            <Activity className="w-4 h-4 mr-2" />
          )}
          Ejecutar Escaneo Nmap
        </button>
        <button
          onClick={handleNmapWithPreview}
          disabled={!nmapTarget.trim()}
          className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-xl flex items-center gap-2 disabled:opacity-50"
        >
          <Eye className="w-4 h-4" />
          Preview
        </button>
      </div>

      {advancedNmapMutation.data && (
        <div className="mt-6">
          <div className="bg-white border border-gray-200 rounded-xl p-6 mb-4">
            <h4 className="font-semibold mb-4 text-gray-900">Resumen del Escaneo</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{advancedNmapMutation.data?.findings?.length || 0}</div>
                <div className="text-sm text-gray-600">Hallazgos</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {advancedNmapMutation.data?.findings?.filter((f: NmapFinding) => f.severity === 'critical').length || 0}
                </div>
                <div className="text-sm text-gray-600">Críticos</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {advancedNmapMutation.data?.findings?.filter((f: NmapFinding) => f.severity === 'high').length || 0}
                </div>
                <div className="text-sm text-gray-600">Altos</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-500">
                  {advancedNmapMutation.data?.findings?.filter((f: NmapFinding) => f.type === 'port').length || 0}
                </div>
                <div className="text-sm text-gray-600">Puertos</div>
              </div>
            </div>
            <div className="mt-4">
              <p className="text-sm text-gray-600">
                Comando: <code className="bg-black text-gray-900 px-2 py-1 rounded text-xs">{advancedNmapMutation.data?.command}</code>
              </p>
            </div>
          </div>

          {advancedNmapMutation.data?.findings && advancedNmapMutation.data.findings.length > 0 && (
            <div>
              <h4 className="font-semibold mb-2 text-red-400">Hallazgos Detectados</h4>
              <NmapFindings findings={advancedNmapMutation.data.findings} />
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

