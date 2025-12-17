/**
 * Running Scans Monitor Component
 * ================================
 *
 * Consola para ver y cancelar scans en ejecución.
 */

import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { X, Clock, AlertTriangle, Loader2, Trash2, RefreshCw, Trash } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../lib/api/shared/client'

interface RunningScan {
  id: number
  scan_type: string
  target: string
  workspace_id: number
  user_id: number
  started_at: string | null
  progress: number
  options: Record<string, any>
  elapsed_time: {
    hours: number
    minutes: number
    seconds: number
  } | null
  tool?: string
}

interface RunningScansResponse {
  scans: RunningScan[]
  total: number
}

/**
 * Obtiene los scans en ejecución
 */
const getRunningScans = async (): Promise<RunningScansResponse> => {
  try {
    const response = await api.get<RunningScansResponse>('system/running-scans')
    return response.data
  } catch (error: any) {
    // Log detallado del error para debugging
    console.error('[RunningScansMonitor] Error fetching running scans:', {
      message: error?.message,
      response: error?.response?.data,
      status: error?.response?.status,
      code: error?.code,
      config: {
        url: error?.config?.url,
        method: error?.config?.method,
        headers: error?.config?.headers
      }
    })
    
    // Re-lanzar el error para que React Query lo maneje
    throw error
  }
}

/**
 * Cancela un scan
 */
const cancelScan = async (scanId: number): Promise<{ message: string; scan_id: number; process_terminated: boolean }> => {
  const response = await api.post(`system/scans/${scanId}/cancel`)
  return response.data
}

/**
 * Cancela todos los scans en ejecución
 */
const cancelAllScans = async (): Promise<{ message: string; cancelled: number; failed: number; total: number; cancelled_ids: number[]; failed_ids: number[] }> => {
  const response = await api.post('system/scans/cancel-all')
  return response.data
}

const RunningScansMonitor: React.FC = () => {
  const queryClient = useQueryClient()
  const [autoRefresh, setAutoRefresh] = useState(true)

  // Query para obtener scans en ejecución
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['running-scans'],
    queryFn: getRunningScans,
    refetchInterval: autoRefresh ? 5000 : false, // Auto-refresh cada 5 segundos
    staleTime: 0,
    retry: 3, // Reintentar 3 veces en caso de error
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Backoff exponencial
    onError: (err: any) => {
      console.error('[RunningScansMonitor] Error fetching running scans:', err)
      // No mostrar toast para errores de red temporales, solo loguear
      if (err.message?.includes('Network Error') || err.code === 'ERR_NETWORK') {
        console.warn('[RunningScansMonitor] Network error, will retry automatically')
      }
    }
  })

  // Mutation para cancelar scan
  const cancelMutation = useMutation({
    mutationFn: cancelScan,
    onSuccess: (data, scanId) => {
      toast.success(`Scan ${scanId} cancelado exitosamente`)
      queryClient.invalidateQueries({ queryKey: ['running-scans'] })
    },
    onError: (error: any, scanId) => {
      toast.error(`Error cancelando scan ${scanId}: ${error.message}`)
    }
  })

  // Mutation para cancelar todos los scans
  const cancelAllMutation = useMutation({
    mutationFn: cancelAllScans,
    onSuccess: (data) => {
      if (data.cancelled > 0) {
        toast.success(`${data.cancelled} scan(s) cancelado(s) exitosamente`)
      }
      if (data.failed > 0) {
        toast.warning(`${data.failed} scan(s) no pudieron ser cancelado(s)`)
      }
      if (data.cancelled === 0 && data.failed === 0) {
        toast.info('No hay scans en ejecución para cancelar')
      }
      queryClient.invalidateQueries({ queryKey: ['running-scans'] })
    },
    onError: (error: any) => {
      toast.error(`Error cancelando scans: ${error.message}`)
    }
  })

  const handleCancel = (scanId: number) => {
    if (window.confirm(`¿Estás seguro de cancelar el scan ${scanId}?`)) {
      cancelMutation.mutate(scanId)
    }
  }

  const handleCancelAll = () => {
    if (total === 0) {
      toast.info('No hay scans en ejecución para cancelar')
      return
    }
    
    if (window.confirm(`¿Estás seguro de cancelar TODOS los ${total} scan(s) en ejecución?\n\nEsta acción no se puede deshacer.`)) {
      cancelAllMutation.mutate()
    }
  }

  const formatElapsedTime = (elapsed: { hours: number; minutes: number; seconds: number } | null): string => {
    if (!elapsed) return 'N/A'
    
    if (elapsed.hours >= 1) {
      return `${Math.floor(elapsed.hours)}h ${Math.floor(elapsed.minutes % 60)}m`
    } else if (elapsed.minutes >= 1) {
      return `${Math.floor(elapsed.minutes)}m ${Math.floor(elapsed.seconds % 60)}s`
    } else {
      return `${Math.floor(elapsed.seconds)}s`
    }
  }

  const getScanTypeColor = (scanType: string): string => {
    const colors: Record<string, string> = {
      'reconnaissance': 'bg-blue-500/20 text-blue-400 border-blue-500',
      'port_scan': 'bg-red-600/20 text-gray-900 border-gray-200',
      'vulnerability': 'bg-yellow-500/20 text-yellow-400 border-yellow-500',
      'exploitation': 'bg-red-500/20 text-red-400 border-red-500',
      'post_exploitation': 'bg-purple-500/20 text-purple-400 border-purple-500',
    }
    return colors[scanType] || 'bg-gray-500/20 text-gray-500 border-gray-500'
  }

  if (isLoading) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-gray-900" />
          <span className="ml-2 text-gray-900">Cargando scans en ejecución...</span>
        </div>
      </div>
    )
  }

  if (error) {
    const errorMessage = (error as any)?.message || 'Error desconocido'
    const isNetworkError = errorMessage.includes('Network Error') || errorMessage.includes('ERR_NETWORK')
    const isAuthError = (error as any)?.response?.status === 401 || (error as any)?.response?.status === 403
    
    return (
      <div className="bg-white border border-red-500 rounded-xl p-6">
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-2 text-red-400">
            <AlertTriangle className="w-5 h-5" />
            <span>Error cargando scans: {errorMessage}</span>
          </div>
          
          {isNetworkError && (
            <div className="text-sm text-yellow-400 bg-yellow-500/10 border border-yellow-500/20 rounded p-2">
              <p>Error de red. Verificando conexión con el backend...</p>
              <p className="text-xs mt-1 text-gray-500">El sistema reintentará automáticamente.</p>
            </div>
          )}
          
          {isAuthError && (
            <div className="text-sm text-yellow-400 bg-yellow-500/10 border border-yellow-500/20 rounded p-2">
              <p>Error de autenticación. Por favor, recarga la página.</p>
            </div>
          )}
          
          <button
            onClick={() => refetch()}
            className="mt-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded transition-colors text-sm"
          >
            <RefreshCw className="w-4 h-4 inline mr-2" />
            Reintentar
          </button>
        </div>
      </div>
    )
  }

  const scans = data?.scans || []
  const total = data?.total || 0

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      {/* Botón para cancelar todos - Arriba de todo */}
      {total > 0 && (
        <div className="mb-4 pb-4 border-b border-gray-200">
          <button
            onClick={handleCancelAll}
            disabled={cancelAllMutation.isPending}
            className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-semibold"
            title="Cancelar todos los scans en ejecución"
          >
            {cancelAllMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Cancelando todos los scans...</span>
              </>
            ) : (
              <>
                <Trash className="w-4 h-4" />
                <span>Cancelar Todos los Scans ({total})</span>
              </>
            )}
          </button>
        </div>
      )}

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-gray-900" />
          <h2 className="text-lg font-semibold text-gray-900">Scans en Ejecución</h2>
          <span className="px-2 py-1 text-xs rounded bg-red-600/20 text-gray-900">
            {total}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 text-sm text-gray-500 cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-200 text-gray-500 focus:ring-red-500"
            />
            <span>Auto-refresh</span>
          </label>
          <button
            onClick={() => refetch()}
            className="p-2 text-gray-900 hover:text-gray-700 hover:bg-red-600/10 rounded transition-colors"
            title="Actualizar"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {total === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Clock className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>No hay scans en ejecución</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {scans.map((scan) => (
            <div
              key={scan.id}
              className="bg-gray-50 border border-gray-200 rounded-xl p-4 hover:border-gray-200 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-2 py-1 text-xs rounded border ${getScanTypeColor(scan.scan_type)}`}>
                      {scan.scan_type}
                    </span>
                    {scan.tool && (
                      <span className="text-xs text-gray-500">
                        {scan.tool}
                      </span>
                    )}
                    <span className="text-xs text-gray-500">
                      ID: {scan.id}
                    </span>
                  </div>
                  
                  <div className="mb-2">
                    <p className="text-sm font-medium text-gray-200">
                      Target: <span className="text-gray-900">{scan.target}</span>
                    </p>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-xs text-gray-500 mb-2">
                    <div>
                      <span className="text-gray-500">Tiempo:</span>{' '}
                      <span className="text-gray-600">{formatElapsedTime(scan.elapsed_time)}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Progreso:</span>{' '}
                      <span className="text-gray-600">{scan.progress}%</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Workspace:</span>{' '}
                      <span className="text-gray-600">{scan.workspace_id}</span>
                    </div>
                  </div>

                  {/* Progress bar */}
                  {scan.progress > 0 && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-red-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${scan.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                <button
                  onClick={() => handleCancel(scan.id)}
                  disabled={cancelMutation.isPending}
                  className="ml-4 p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Cancelar scan"
                >
                  {cancelMutation.isPending && cancelMutation.variables === scan.id ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default RunningScansMonitor
