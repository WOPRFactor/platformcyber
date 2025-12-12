/**
 * ClearLogsModal Component
 * ========================
 * 
 * Modal de confirmación para limpiar logs con opción de exportar antes.
 */

import React, { useState } from 'react'
import { X, Trash2, Download, AlertTriangle } from 'lucide-react'
import { useWorkspace } from '../../contexts/WorkspaceContext'
import { useWorkspaceLogsStats } from '../../hooks/useWorkspaceLogsStats'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { workspacesAPI } from '../../lib/api/workspaces/workspaces'

interface ClearLogsModalProps {
  isOpen: boolean
  onClose: () => void
  onClear: () => void
}

export const ClearLogsModal: React.FC<ClearLogsModalProps> = ({
  isOpen,
  onClose,
  onClear
}) => {
  const { currentWorkspace } = useWorkspace()
  const { stats } = useWorkspaceLogsStats()
  const queryClient = useQueryClient()
  const [exportBeforeDelete, setExportBeforeDelete] = useState(true)

  const deleteMutation = useMutation({
    mutationFn: async (exportFirst: boolean) => {
      if (!currentWorkspace?.id) return
      return await workspacesAPI.deleteWorkspaceLogs(currentWorkspace.id, exportFirst)
    },
    onSuccess: async (data, exportFirst) => {
      if (exportFirst && data.export_url) {
        // Descargar el archivo exportado
        try {
          const blob = await workspacesAPI.exportWorkspaceLogs(currentWorkspace!.id, 'json')
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `workspace_${currentWorkspace!.id}_logs_${new Date().toISOString().split('T')[0]}.json`
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          URL.revokeObjectURL(url)
        } catch (e) {
          console.error('Error descargando export:', e)
        }
      }
      // Invalidar queries para refrescar datos
      queryClient.invalidateQueries({ queryKey: ['workspace-logs', currentWorkspace?.id] })
      queryClient.invalidateQueries({ queryKey: ['workspace-logs-stats', currentWorkspace?.id] })
      // Limpiar logs en memoria del hook
      onClear()
      onClose()
    }
  })

  if (!isOpen) return null

  const handleConfirm = () => {
    deleteMutation.mutate(exportBeforeDelete)
  }

  return (
    <div className="fixed inset-0 z-[60] bg-black bg-opacity-75 flex items-center justify-center">
      <div className="bg-gray-800 border border-green-500 rounded-lg shadow-2xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-green-500">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-yellow-400" />
            <h3 className="text-lg font-medium text-cyan-400">Limpiar Logs</h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-red-400 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {stats && (
            <div className="bg-gray-900 rounded p-3 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Total de logs:</span>
                <span className="text-green-400 font-mono">{stats.totalLogs.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Tamaño:</span>
                <span className="text-green-400 font-mono">{stats.sizeMB.toFixed(2)} MB</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Rango de fechas:</span>
                <span className="text-green-400 text-xs">{stats.dateRangeText}</span>
              </div>
            </div>
          )}

          <div className="text-sm text-gray-300">
            <p className="mb-3">
              ⚠️ Los logs del workspace <span className="text-cyan-400 font-semibold">{currentWorkspace?.name}</span> serán eliminados.
            </p>
          </div>

          {/* Opciones */}
          <div className="space-y-2">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={exportBeforeDelete}
                onChange={(e) => setExportBeforeDelete(e.target.checked)}
                className="w-4 h-4 text-cyan-500 bg-gray-700 border-gray-600 rounded focus:ring-cyan-500"
              />
              <span className="text-sm text-gray-300">☑ Exportar logs antes de eliminar</span>
            </label>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-2 p-4 border-t border-green-500">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-400 hover:text-gray-300 transition-colors"
            disabled={deleteMutation.isPending}
          >
            Cancelar
          </button>
          {exportBeforeDelete ? (
            <button
              onClick={handleConfirm}
              disabled={deleteMutation.isPending}
              className="px-4 py-2 text-sm bg-green-500 text-black hover:bg-green-400 rounded transition-colors flex items-center space-x-2 disabled:opacity-50"
            >
              <Download className="w-4 h-4" />
              <span>{deleteMutation.isPending ? 'Exportando...' : 'Exportar y Borrar'}</span>
            </button>
          ) : (
            <button
              onClick={handleConfirm}
              disabled={deleteMutation.isPending}
              className="px-4 py-2 text-sm bg-red-500 text-white hover:bg-red-400 rounded transition-colors flex items-center space-x-2 disabled:opacity-50"
            >
              <Trash2 className="w-4 h-4" />
              <span>{deleteMutation.isPending ? 'Eliminando...' : 'Solo Borrar'}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  )
}


