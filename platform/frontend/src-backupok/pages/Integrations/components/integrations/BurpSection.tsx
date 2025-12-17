import React, { useState } from 'react'
import { Shield, CheckCircle, XCircle, Loader, Play, Eye } from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { integrationsAPI } from '../../../../lib/api/integrations'
import { useWorkspace } from '../../../../contexts/WorkspaceContext'
import { useCommandPreview } from '../../../VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../../../../components/CommandPreviewModal'

export const BurpSection: React.FC = () => {
  const { currentWorkspace } = useWorkspace()
  const [burpUrl, setBurpUrl] = useState('')
  const [burpScanId, setBurpScanId] = useState('')
  const queryClient = useQueryClient()
  const hasToken = !!localStorage.getItem('access_token')
  const isAuthenticated = true // TODO: Get from context
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview, openPreview } = commandPreview

  const { data: burpStatus, refetch: refetchBurpStatus } = useQuery({
    queryKey: ['burp_status'],
    queryFn: integrationsAPI.checkBurpStatus,
    enabled: isAuthenticated && hasToken,
    refetchInterval: (isAuthenticated && hasToken) ? 30000 : false,
  })

  const checkBurpMutation = useMutation({
    mutationFn: integrationsAPI.checkBurpStatus,
    onSuccess: (data) => {
      if (data.connected) {
        toast.success('Conexión con Burp Suite exitosa')
      } else {
        toast.error(`Error de conexión: ${data.error}`)
      }
      refetchBurpStatus()
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`)
    }
  })

  const startBurpScanMutation = useMutation({
    mutationFn: () => {
      if (!currentWorkspace?.id) {
        throw new Error('Workspace no seleccionado')
      }
      return integrationsAPI.startBurpScan(burpUrl, currentWorkspace.id)
    },
    onSuccess: (data) => {
      setBurpScanId(data?.scan_id || '')
      toast.success('Escaneo iniciado correctamente')
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`)
    }
  })

  const handleBurpWithPreview = async () => {
    if (!currentWorkspace?.id) {
      toast.error('Workspace no seleccionado')
      return
    }
    if (!burpUrl.trim()) {
      toast.error('URL es requerida')
      return
    }

    try {
      const preview = await integrationsAPI.previewBurpScan(burpUrl, currentWorkspace.id)
      openPreview(preview, 'Burp Suite', async () => {
        await startBurpScanMutation.mutateAsync()
      })
    } catch (error: any) {
      toast.error(`Error obteniendo preview: ${error.message}`)
    }
  }

  return (
    <div className="space-y-6">
      {/* Status Card */}
      <div className="bg-gray-50 border border-red-500 rounded-xl p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-red-600" />
            <h3 className="text-lg font-bold text-red-400">Burp Suite Professional</h3>
          </div>
          <div className="flex items-center gap-2">
            {burpStatus?.connected ? (
              <CheckCircle className="w-5 h-5 text-gray-500" />
            ) : (
              <XCircle className="w-5 h-5 text-red-600" />
            )}
            <span className={burpStatus?.connected ? 'text-gray-500' : 'text-red-600'}>
              {burpStatus?.connected ? 'Conectado' : 'Desconectado'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <div className="text-sm text-gray-600">Estado API</div>
            <div className={`text-lg font-bold ${burpStatus?.connected ? 'text-gray-500' : 'text-red-600'}`}>
              {burpStatus?.connected ? 'Activo' : 'Inactivo'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600">Versión</div>
            <div className="text-lg font-bold text-blue-600">
              {burpStatus?.version || 'Desconocida'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600">Scanner</div>
            <div className="text-lg font-bold text-purple-600">
              {burpStatus?.status || 'Desconocido'}
            </div>
          </div>
        </div>

        <button
          onClick={() => checkBurpMutation.mutate()}
          disabled={checkBurpMutation.isPending}
          className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {checkBurpMutation.isPending ? (
            <Loader className="w-4 h-4 animate-spin mr-2" />
          ) : (
            <Shield className="w-4 h-4 mr-2" />
          )}
          Verificar Conexión
        </button>

        {burpStatus?.error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
            <p className="text-red-800 text-sm">{burpStatus.error}</p>
          </div>
        )}
      </div>

      {/* Scan Form */}
      <div className="bg-gray-50 border border-red-500 rounded-xl p-6">
        <h3 className="text-lg font-bold text-red-400 mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5" />
          Escaneo Activo con Burp
        </h3>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-900 mb-2">URL Objetivo</label>
          <input
            type="url"
            value={burpUrl}
            onChange={(e) => setBurpUrl(e.target.value)}
            placeholder="https://example.com"
            className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500"
          />
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleBurpWithPreview}
            disabled={startBurpScanMutation.isPending || !burpUrl.trim()}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded flex items-center gap-2 disabled:opacity-50"
          >
            {startBurpScanMutation.isPending ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            Iniciar Escaneo
          </button>
          <button
            onClick={handleBurpWithPreview}
            disabled={!burpUrl.trim()}
            className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded flex items-center gap-2 disabled:opacity-50"
          >
            <Eye className="w-4 h-4" />
            Preview
          </button>

          {burpScanId && (
            <button
              onClick={() => queryClient.invalidateQueries({ queryKey: ['burp_scan_status', burpScanId] })}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center gap-2"
            >
              <CheckCircle className="w-4 h-4" />
              Verificar Estado
            </button>
          )}
        </div>

        {startBurpScanMutation.data && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
            <p className="text-green-800">
              Escaneo iniciado. ID: <code>{startBurpScanMutation.data?.scan_id}</code>
            </p>
          </div>
        )}
      </div>

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

