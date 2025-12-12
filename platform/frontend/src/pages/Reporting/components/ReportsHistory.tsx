/**
 * Reports History Component
 * ==========================
 * 
 * Componente para mostrar historial de reportes generados.
 */

import React, { useState, useMemo } from 'react'
import { Download, Trash2, Loader, Filter, X } from 'lucide-react'
import LoadingSpinner from '../../../components/LoadingSpinner'
import { reportingAPI } from '../../../lib/api/reporting'
import { toast } from 'sonner'

interface ReportHistoryItem {
  id: number
  title: string
  report_type: 'executive' | 'technical' | 'compliance' | 'full'
  format: 'pdf' | 'html' | 'json' | 'markdown'
  status: string
  workspace_id: number
  workspace_name?: string
  created_at: string
  generated_at: string | null
  file_size: number | null
  content?: any
}

interface ReportsHistoryProps {
  workspaceId?: number
  reports?: ReportHistoryItem[]
  reportsLoading: boolean
  onRefresh: () => void
}

const ReportsHistory: React.FC<ReportsHistoryProps> = ({
  workspaceId,
  reports = [],
  reportsLoading,
  onRefresh
}) => {
  // Asegurar que reports sea un array
  const reportsArray = Array.isArray(reports) ? reports : (reports?.reports || [])
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [deletingAll, setDeletingAll] = useState(false)
  const [filterType, setFilterType] = useState<'all' | 'executive' | 'technical' | 'compliance' | 'full'>('all')

  // Filtrar reportes por tipo
  const filteredReports = useMemo(() => {
    if (filterType === 'all') {
      return reportsArray
    }
    return reportsArray.filter((report: ReportHistoryItem) => report.report_type === filterType)
  }, [reportsArray, filterType])

  const handleDownloadReport = async (report: ReportHistoryItem) => {
    try {
      // Descargar el PDF real del servidor
      const blob = await reportingAPI.downloadReportPDF(report.id)
      
      // Crear URL del blob y descargar
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${report.title.replace(/\s+/g, '-')}-${report.id}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
      toast.success('Reporte descargado exitosamente')
    } catch (error: any) {
      console.error('Error descargando reporte:', error)
      toast.error(`Error descargando reporte: ${error.message || 'Error desconocido'}`)
    }
  }

  const handleDeleteReport = async (report: ReportHistoryItem) => {
    // Confirmar eliminación
    if (!window.confirm(`¿Estás seguro de que deseas eliminar el reporte "${report.title}"?`)) {
      return
    }

    setDeletingId(report.id)
    try {
      const result = await reportingAPI.deleteReport(report.id)
      
      if (result.success) {
        toast.success('Reporte eliminado exitosamente')
        // Recargar lista de reportes
        onRefresh()
      } else {
        toast.error(result.error || 'Error al eliminar el reporte')
      }
    } catch (error: any) {
      console.error('Error eliminando reporte:', error)
      const errorMessage = error.response?.data?.error || error.response?.data?.message || error.message || 'Error desconocido'
      toast.error(`Error eliminando reporte: ${errorMessage}`)
    } finally {
      setDeletingId(null)
    }
  }

  const handleDeleteAll = async () => {
    const reportsToDelete = filteredReports.length > 0 ? filteredReports : reportsArray
    const count = reportsToDelete.length
    
    if (count === 0) {
      toast.info('No hay reportes para eliminar')
      return
    }

    const message = filterType !== 'all' 
      ? `¿Estás seguro de que deseas eliminar todos los ${count} reportes de tipo "${filterType}"?`
      : `¿Estás seguro de que deseas eliminar TODOS los ${count} reportes? Esta acción no se puede deshacer.`
    
    if (!window.confirm(message)) {
      return
    }

    setDeletingAll(true)
    let successCount = 0
    let errorCount = 0

    try {
      // Eliminar todos los reportes en paralelo
      const deletePromises = reportsToDelete.map(async (report: ReportHistoryItem) => {
        try {
          const result = await reportingAPI.deleteReport(report.id)
          if (result.success) {
            successCount++
          } else {
            errorCount++
          }
        } catch (error) {
          errorCount++
          console.error(`Error eliminando reporte ${report.id}:`, error)
        }
      })

      await Promise.all(deletePromises)

      if (successCount > 0) {
        toast.success(`${successCount} reporte${successCount > 1 ? 's' : ''} eliminado${successCount > 1 ? 's' : ''} exitosamente`)
      }
      if (errorCount > 0) {
        toast.error(`${errorCount} reporte${errorCount > 1 ? 's' : ''} no se pudieron eliminar`)
      }

      // Recargar lista de reportes
      onRefresh()
    } catch (error: any) {
      console.error('Error eliminando reportes:', error)
      toast.error(`Error al eliminar reportes: ${error.message || 'Error desconocido'}`)
    } finally {
      setDeletingAll(false)
    }
  }

  return (
    <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-green-400">Historial de Reportes</h2>
          <p className="text-green-600">
            Reportes generados y disponibles para descarga
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Filtro por tipo de reporte */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as typeof filterType)}
              className="bg-gray-900 border border-gray-700 text-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-green-500"
            >
              <option value="all">Todos los tipos</option>
              <option value="technical">Técnico</option>
              <option value="executive">Ejecutivo</option>
              <option value="compliance">Cumplimiento</option>
              <option value="full">Completo</option>
            </select>
            {filterType !== 'all' && (
              <button
                onClick={() => setFilterType('all')}
                className="text-gray-400 hover:text-gray-300 p-1"
                title="Limpiar filtro"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          {filteredReports && filteredReports.length > 0 && (
            <button
              onClick={handleDeleteAll}
              disabled={deletingAll || reportsLoading}
              className="bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg text-sm flex items-center gap-2 transition-colors"
              title={filterType !== 'all' ? `Eliminar todos los reportes de tipo ${filterType}` : 'Eliminar todos los reportes'}
            >
              {deletingAll ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Eliminando...
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4" />
                  Eliminar {filterType !== 'all' ? `Todos (${filteredReports.length})` : 'Todos'}
                </>
              )}
            </button>
          )}
          <button
            onClick={onRefresh}
            className="btn-secondary px-4 py-2"
            title="Actualizar lista de reportes"
            disabled={deletingAll}
          >
            🔄 Refresh
          </button>
        </div>
      </div>
      {reportsLoading ? (
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      ) : filteredReports && filteredReports.length > 0 ? (
        <div className="space-y-2">
          {filterType !== 'all' && (
            <div className="mb-3 text-sm text-gray-400">
              Mostrando {filteredReports.length} de {reportsArray.length} reportes
              {filterType !== 'all' && ` (filtrado por: ${filterType})`}
            </div>
          )}
          {filteredReports.map((report: ReportHistoryItem) => (
            <div key={report.id} className="flex items-center justify-between p-4 bg-gray-900 border border-gray-700 rounded-lg hover:border-green-500 transition-colors">
              <div className="flex-1">
                <div className="font-medium text-green-400">{report.title}</div>
                <div className="text-sm text-gray-400 mt-1">
                  {report.workspace_name && <span className="mr-3">Workspace: {report.workspace_name}</span>}
                  <span>{new Date(report.created_at).toLocaleString('es-AR')}</span>
                  {report.file_size && <span className="ml-3">- {(report.file_size / 1024).toFixed(1)} KB</span>}
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <span className={`px-2 py-1 text-xs rounded ${
                    report.report_type === 'executive' ? 'bg-blue-900 text-blue-300' :
                    report.report_type === 'technical' ? 'bg-purple-900 text-purple-300' :
                    report.report_type === 'compliance' ? 'bg-yellow-900 text-yellow-300' :
                    'bg-green-900 text-green-300'
                  }`}>
                    {report.report_type.toUpperCase()}
                  </span>
                  <span className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded">
                    {report.format.toUpperCase()}
                  </span>
                  <span className={`px-2 py-1 text-xs rounded ${
                    report.status === 'completed' ? 'bg-green-900 text-green-300' :
                    report.status === 'failed' ? 'bg-red-900 text-red-300' :
                    'bg-yellow-900 text-yellow-300'
                  }`}>
                    {report.status}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2 ml-4">
                <button
                  onClick={() => handleDownloadReport(report)}
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm flex items-center gap-2 transition-colors"
                  title="Descargar reporte"
                  disabled={reportsLoading}
                >
                  <Download className="w-4 h-4" />
                  Descargar
                </button>
                <button
                  onClick={() => handleDeleteReport(report)}
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Eliminar reporte"
                  disabled={reportsLoading || deletingId === report.id}
                >
                  {deletingId === report.id ? (
                    <Loader className="w-4 h-4 animate-spin" />
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
                  Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : reportsArray && reportsArray.length > 0 && filterType !== 'all' ? (
        <p className="text-gray-500 text-center py-4">
          No hay reportes de tipo "{filterType}" en el historial
        </p>
      ) : (
        <p className="text-gray-500 text-center py-4">
          No hay reportes generados
        </p>
      )}
    </div>
  )
}

export default ReportsHistory

