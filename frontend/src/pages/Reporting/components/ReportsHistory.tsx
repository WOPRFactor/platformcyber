/**
 * Reports History Component
 * ==========================
 * 
 * Componente para mostrar historial de reportes generados.
 */

import React from 'react'
import { Download, Loader } from 'lucide-react'
import LoadingSpinner from '../../../components/LoadingSpinner'
import { reportingAPI } from '../../../lib/api/reporting'
import { toast } from 'sonner'

interface ReportListItem {
  filename: string
  created: string
  size: number
  format: string
}

interface ReportsHistoryProps {
  reports: ReportListItem[] | undefined
  reportsLoading: boolean
  onRefresh: () => void
}

const ReportsHistory: React.FC<ReportsHistoryProps> = ({
  reports,
  reportsLoading,
  onRefresh
}) => {
  const handleDownloadReport = async (filename: string) => {
    try {
      const blob = await reportingAPI.downloadReport(filename)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      toast.success('Reporte descargado exitosamente')
    } catch (error: any) {
      toast.error(`Error descargando reporte: ${error.message}`)
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
        <button
          onClick={onRefresh}
          className="btn-secondary px-4 py-2"
          title="Actualizar lista de reportes"
        >
          🔄 Refresh
        </button>
      </div>
      {reportsLoading ? (
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      ) : reports && reports.length > 0 ? (
        <div className="space-y-2">
          {reports.map((report: ReportListItem, idx: number) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div>
                <div className="font-medium">{report.filename}</div>
                <div className="text-sm text-gray-600">
                  {new Date(report.created).toLocaleString()} - {(report.size / 1024).toFixed(1)} KB
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                  {report.format.toUpperCase()}
                </span>
                <button
                  onClick={() => handleDownloadReport(report.filename)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm flex items-center gap-1"
                >
                  <Download className="w-3 h-3" />
                  Descargar
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500 text-center py-4">
          No hay reportes generados
        </p>
      )}
    </div>
  )
}

export default ReportsHistory

