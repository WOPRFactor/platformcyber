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
  const handleDownloadReport = async (report: ReportHistoryItem) => {
    try {
      // Obtener el reporte completo
      const response = await reportingAPI.getReport(report.id)
      
      if (response.status === 'success' && response.report.content) {
        // Generar HTML del reporte
        const htmlContent = generateReportHTML(response.report.content)
        
        // Crear blob y descargar
        const blob = new Blob([htmlContent], { type: 'text/html' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${report.title.replace(/\s+/g, '-')}-${report.id}.html`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        
        toast.success('Reporte descargado exitosamente')
      } else {
        toast.error('No se pudo obtener el contenido del reporte')
      }
    } catch (error: any) {
      console.error('Error descargando reporte:', error)
      toast.error(`Error descargando reporte: ${error.message || 'Error desconocido'}`)
    }
  }
  
  const generateReportHTML = (reportData: any): string => {
    const reportType = reportData.metadata?.report_type || 'full'
    const workspaceName = reportData.metadata?.workspace_id || 'Unknown'
    const generatedAt = reportData.metadata?.generated_at 
      ? new Date(reportData.metadata.generated_at).toLocaleString('es-AR')
      : new Date().toLocaleString('es-AR')
    
    let html = `<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Pentesting</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #e0e0e0; }
        .container { max-width: 1200px; margin: 0 auto; background: #2a2a2a; padding: 30px; border-radius: 8px; }
        h1 { color: #4ade80; border-bottom: 2px solid #4ade80; padding-bottom: 10px; }
        h2 { color: #60a5fa; margin-top: 30px; }
        h3 { color: #a78bfa; }
        .metadata { background: #1a1a1a; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .stat { display: inline-block; margin: 10px 20px 10px 0; padding: 10px 20px; background: #3a3a3a; border-radius: 5px; }
        .stat-value { font-size: 24px; font-weight: bold; color: #4ade80; }
        .stat-label { font-size: 12px; color: #9ca3af; }
        .finding { background: #2a2a2a; padding: 15px; margin: 10px 0; border-left: 4px solid #4ade80; border-radius: 4px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #3a3a3a; }
        th { background: #1a1a1a; color: #4ade80; }
        .severity-critical { color: #ef4444; }
        .severity-high { color: #f97316; }
        .severity-medium { color: #eab308; }
        .severity-low { color: #3b82f6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Reporte de Pentesting</h1>
        <div class="metadata">
            <p><strong>Workspace:</strong> ${workspaceName}</p>
            <p><strong>Tipo de Reporte:</strong> ${reportType.toUpperCase()}</p>
            <p><strong>Generado:</strong> ${generatedAt}</p>
        </div>`
    
    // Agregar resumen ejecutivo si existe
    if (reportData.executive_summary) {
      const es = reportData.executive_summary
      html += `
        <h2>📈 Resumen Ejecutivo</h2>
        <div class="stat">
            <div class="stat-value">${es.total_scans || 0}</div>
            <div class="stat-label">Scans Totales</div>
        </div>
        <div class="stat">
            <div class="stat-value">${es.total_vulnerabilities || 0}</div>
            <div class="stat-label">Vulnerabilidades</div>
        </div>
        <div class="stat">
            <div class="stat-value">${es.risk_score || 0}</div>
            <div class="stat-label">Puntuación de Riesgo</div>
        </div>
        <div class="stat">
            <div class="stat-value">${es.risk_level || 'N/A'}</div>
            <div class="stat-label">Nivel de Riesgo</div>
        </div>`
      
      if (es.severity_distribution) {
        html += `<h3>Distribución por Severidad</h3><table><tr><th>Severidad</th><th>Cantidad</th></tr>`
        Object.entries(es.severity_distribution).forEach(([severity, count]) => {
          html += `<tr><td class="severity-${severity}">${severity.toUpperCase()}</td><td>${count}</td></tr>`
        })
        html += `</table>`
      }
      
      if (es.key_findings && Array.isArray(es.key_findings)) {
        html += `<h3>Hallazgos Clave</h3>`
        es.key_findings.forEach((finding: string) => {
          html += `<div class="finding">${finding}</div>`
        })
      }
    }
    
    html += `
    </div>
</body>
</html>`
    
    return html
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Historial de Reportes</h2>
          <p className="text-gray-500">
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
          {reports.map((report: ReportHistoryItem) => (
            <div key={report.id} className="flex items-center justify-between p-4 bg-gray-50 border border-gray-200 rounded-xl hover:border-gray-200 transition-colors">
              <div className="flex-1">
                <div className="font-medium text-gray-900">{report.title}</div>
                <div className="text-sm text-gray-500 mt-1">
                  {report.workspace_name && <span className="mr-3">Workspace: {report.workspace_name}</span>}
                  <span>{new Date(report.created_at).toLocaleString('es-AR')}</span>
                  {report.file_size && <span className="ml-3">- {(report.file_size / 1024).toFixed(1)} KB</span>}
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <span className={`px-2 py-1 text-xs rounded ${
                    report.report_type === 'executive' ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                    report.report_type === 'technical' ? 'bg-purple-50 text-purple-700 border border-purple-200' :
                    report.report_type === 'compliance' ? 'bg-yellow-50 text-yellow-700 border border-yellow-200' :
                    'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  }`}>
                    {report.report_type.toUpperCase()}
                  </span>
                  <span className="px-2 py-1 bg-gray-700 text-gray-600 text-xs rounded">
                    {report.format.toUpperCase()}
                  </span>
                  <span className={`px-2 py-1 text-xs rounded ${
                    report.status === 'completed' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                    report.status === 'failed' ? 'bg-red-50 text-red-700 border border-red-200' :
                    'bg-yellow-50 text-yellow-700 border border-yellow-200'
                  }`}>
                    {report.status}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2 ml-4">
                <button
                  onClick={() => handleDownloadReport(report)}
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl text-sm flex items-center gap-2 transition-colors"
                  title="Descargar reporte"
                >
                  <Download className="w-4 h-4" />
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

