/**
 * ArchiveWorkspaceModal Component
 * ===============================
 * 
 * Modal para archivar un workspace con opciones de exportar logs y mantener datos.
 */

import React, { useState } from 'react'
import { X, Archive, Download, AlertTriangle, CheckSquare, Square } from 'lucide-react'
import { useWorkspace } from '../contexts/WorkspaceContext'
import { useWorkspaceLogsStats } from '../hooks/useWorkspaceLogsStats'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { workspacesAPI } from '../lib/api/workspaces/workspaces'
import { toast } from 'sonner'

interface ArchiveWorkspaceModalProps {
  isOpen: boolean
  onClose: () => void
  workspaceId: number
}

export const ArchiveWorkspaceModal: React.FC<ArchiveWorkspaceModalProps> = ({
  isOpen,
  onClose,
  workspaceId
}) => {
  const { currentWorkspace, workspaces } = useWorkspace()
  const workspace = workspaces.find(w => w.id === workspaceId) || currentWorkspace
  const { stats } = useWorkspaceLogsStats()
  const queryClient = useQueryClient()

  const [exportLogs, setExportLogs] = useState(true)
  const [keepFindings, setKeepFindings] = useState(false)
  const [keepReports, setKeepReports] = useState(false)

  const archiveMutation = useMutation({
    mutationFn: async (options: {
      export_logs: boolean
      keep_findings: boolean
      keep_reports: boolean
    }) => {
      return await workspacesAPI.archiveWorkspace(workspaceId, options)
    },
    onSuccess: async (data) => {
      // Si se exportaron logs, descargar el archivo
      if (exportLogs && data.export_url) {
        try {
          const blob = await workspacesAPI.exportWorkspaceLogs(workspaceId, 'json')
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `workspace_${workspaceId}_logs_${new Date().toISOString().split('T')[0]}.json`
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          URL.revokeObjectURL(url)
          toast.success('Logs exportados y descargados')
        } catch (e) {
          console.error('Error descargando export:', e)
          toast.error('Error al descargar logs exportados')
        }
      }

      // Invalidar queries
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
      queryClient.invalidateQueries({ queryKey: ['workspace-logs', workspaceId] })
      queryClient.invalidateQueries({ queryKey: ['workspace-logs-stats', workspaceId] })

      toast.success('Workspace archivado exitosamente')
      onClose()
    },
    onError: (error: any) => {
      toast.error(`Error al archivar workspace: ${error.message || 'Error desconocido'}`)
    }
  })

  if (!isOpen || !workspace) return null

  const handleConfirm = () => {
    archiveMutation.mutate({
      export_logs: exportLogs,
      keep_findings: keepFindings,
      keep_reports: keepReports
    })
  }

  return (
    <div className="fixed inset-0 z-[60] bg-black bg-opacity-75 flex items-center justify-center">
      <div className="bg-white border border-gray-200 rounded-xl shadow-2xl max-w-lg w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <Archive className="w-5 h-5 text-yellow-400" />
            <h3 className="text-lg font-medium text-cyan-400">Completar Proyecto</h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-red-400 transition-colors"
            disabled={archiveMutation.isPending}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          <div className="text-sm text-gray-600">
            <p className="mb-2">
              Estás a punto de archivar el workspace <span className="text-cyan-400 font-semibold">{workspace.name}</span>.
            </p>
            <p className="text-gray-500 text-xs">
              Esto cambiará el estado del workspace a "archivado" y eliminará los logs.
            </p>
          </div>

          {/* Estadísticas de logs */}
          {stats && stats.total_logs > 0 && (
            <div className="bg-gray-50 rounded p-3 space-y-2 text-sm border border-yellow-500/30">
              <div className="flex items-center space-x-2 text-yellow-400">
                <AlertTriangle className="w-4 h-4" />
                <span className="font-semibold">Advertencia</span>
              </div>
              <div className="text-gray-600">
                Los logs del workspace serán eliminados:
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">Total de logs:</span>
                <span className="text-gray-900 font-mono">{stats.total_logs.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">Tamaño:</span>
                <span className="text-gray-900 font-mono">{stats.sizeMB.toFixed(2)} MB</span>
              </div>
            </div>
          )}

          {/* Opciones */}
          <div className="space-y-3">
            <label className="flex items-start space-x-3 cursor-pointer group">
              <div className="mt-0.5">
                {exportLogs ? (
                  <CheckSquare className="w-5 h-5 text-gray-900" />
                ) : (
                  <Square className="w-5 h-5 text-gray-500 group-hover:text-gray-500" />
                )}
              </div>
              <div className="flex-1">
                <div className="text-sm text-gray-600 font-medium">
                  ☑ Exportar logs antes de eliminar
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Se generará un archivo JSON con todos los logs antes de eliminarlos
                </div>
              </div>
              <input
                type="checkbox"
                checked={exportLogs}
                onChange={(e) => setExportLogs(e.target.checked)}
                className="sr-only"
              />
            </label>

            <label className="flex items-start space-x-3 cursor-pointer group">
              <div className="mt-0.5">
                {keepFindings ? (
                  <CheckSquare className="w-5 h-5 text-gray-900" />
                ) : (
                  <Square className="w-5 h-5 text-gray-500 group-hover:text-gray-500" />
                )}
              </div>
              <div className="flex-1">
                <div className="text-sm text-gray-600 font-medium">
                  ☐ Mantener vulnerabilidades encontradas
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Las vulnerabilidades detectadas se conservarán en el workspace
                </div>
              </div>
              <input
                type="checkbox"
                checked={keepFindings}
                onChange={(e) => setKeepFindings(e.target.checked)}
                className="sr-only"
              />
            </label>

            <label className="flex items-start space-x-3 cursor-pointer group">
              <div className="mt-0.5">
                {keepReports ? (
                  <CheckSquare className="w-5 h-5 text-gray-900" />
                ) : (
                  <Square className="w-5 h-5 text-gray-500 group-hover:text-gray-500" />
                )}
              </div>
              <div className="flex-1">
                <div className="text-sm text-gray-600 font-medium">
                  ☐ Mantener reportes generados
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Los reportes PDF/HTML generados se conservarán
                </div>
              </div>
              <input
                type="checkbox"
                checked={keepReports}
                onChange={(e) => setKeepReports(e.target.checked)}
                className="sr-only"
              />
            </label>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-2 p-4 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-500 hover:text-gray-600 transition-colors"
            disabled={archiveMutation.isPending}
          >
            Cancelar
          </button>
          <button
            onClick={handleConfirm}
            disabled={archiveMutation.isPending}
            className="px-4 py-2 text-sm bg-yellow-500 text-black hover:bg-yellow-400 rounded transition-colors flex items-center space-x-2 disabled:opacity-50"
          >
            <Archive className="w-4 h-4" />
            <span>{archiveMutation.isPending ? 'Archivando...' : 'Completar Proyecto'}</span>
          </button>
        </div>
      </div>
    </div>
  )
}


