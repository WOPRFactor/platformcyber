/**
 * Executive Report Modal
 * =====================
 * 
 * Modal para mostrar el reporte ejecutivo generado.
 */

import React from 'react'
import { X, Download, Calendar, Briefcase, AlertTriangle, CheckCircle, Clock, Target } from 'lucide-react'
import { toast } from 'sonner'

interface ExecutiveReportData {
  executive_summary: {
    total_scans: number
    total_vulnerabilities: number
    severity_distribution: Record<string, number>
    risk_level: string
    risk_score: number
    key_findings: string[]
  }
  metadata?: {
    report_type: string
    generated_at: string
    workspace_id: number
    workspace_name?: string
  }
  remediation_roadmap?: {
    immediate_action?: string[] | { items: string[]; timeframe?: string; priority?: string; count?: number }
    short_term?: string[] | { items: string[]; timeframe?: string; priority?: string; count?: number }
    medium_term?: string[] | { items: string[]; timeframe?: string; priority?: string; count?: number }
    long_term?: string[] | { items: string[]; timeframe?: string; priority?: string; count?: number }
  }
  risk_assessment?: {
    critical_count?: number
    high_count?: number
    medium_count?: number
    low_count?: number
    recommendations?: string[]
  }
  scan_summary?: Array<{
    id?: number
    scan_id?: number
    name?: string
    target?: string
    status: string
    created_at?: string
    started_at?: string
    completed_at?: string
    scan_type?: string
    tool?: string
  }>
}

interface ExecutiveReportModalProps {
  isOpen: boolean
  onClose: () => void
  reportData: ExecutiveReportData | null
  workspaceName?: string
}

const ExecutiveReportModal: React.FC<ExecutiveReportModalProps> = ({
  isOpen,
  onClose,
  reportData,
  workspaceName
}) => {
  console.log('🎨 ExecutiveReportModal renderizado:', { isOpen, hasReportData: !!reportData, reportData })
  
  if (!isOpen) {
    console.log('🚫 Modal no está abierto, no renderizando')
    return null
  }
  
  if (!reportData) {
    console.warn('⚠️ Modal está abierto pero no hay reportData')
    return null
  }
  
  console.log('✅ Renderizando modal con datos:', reportData)

  const { executive_summary, metadata, remediation_roadmap, risk_assessment, scan_summary } = reportData

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'critical':
        return 'text-red-400 bg-red-900/20 border-red-500'
      case 'high':
        return 'text-orange-400 bg-orange-900/20 border-orange-500'
      case 'medium':
        return 'text-yellow-400 bg-yellow-900/20 border-yellow-500'
      case 'low':
        return 'text-emerald-700 bg-emerald-50 border-emerald-200'
      default:
        return 'text-gray-500 bg-gray-50/20 border-gray-500'
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'text-red-400 bg-red-900/30'
      case 'high':
        return 'text-orange-400 bg-orange-900/30'
      case 'medium':
        return 'text-yellow-400 bg-yellow-900/30'
      case 'low':
        return 'text-blue-400 bg-blue-900/30'
      case 'info':
        return 'text-gray-500 bg-gray-50/30'
      default:
        return 'text-gray-500 bg-gray-50/30'
    }
  }

  const handleExportPDF = () => {
    toast.info('Exportación a PDF próximamente disponible')
  }

  return (
    <div className="fixed inset-0 z-[10000] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/70 backdrop-blur-sm z-[10001]"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-6xl max-h-[90vh] overflow-y-auto bg-gray-50 border border-gray-200/30 rounded-xl shadow-2xl z-[10002]">
        {/* Header */}
        <div className="sticky top-0 z-10 bg-gray-50 border-b border-gray-200/30 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-600/20 rounded-xl">
                <Target className="w-6 h-6 text-gray-900" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Reporte Ejecutivo</h2>
                {metadata && (
                  <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                    {workspaceName && (
                      <div className="flex items-center gap-1">
                        <Briefcase className="w-4 h-4" />
                        <span>{workspaceName}</span>
                      </div>
                    )}
                    {metadata.generated_at && (
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        <span>{new Date(metadata.generated_at).toLocaleString('es-AR')}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleExportPDF}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg flex items-center gap-2 transition-colors font-medium"
                title="Exportar a PDF"
              >
                <Download className="w-4 h-4" />
                Exportar PDF
              </button>
              <button
                onClick={onClose}
                className="text-gray-500 hover:text-gray-900 transition-colors p-2"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Risk Level Banner */}
          <div className={`border-2 rounded-xl p-4 ${getRiskColor(executive_summary.risk_level)}`}>
            <div className="flex items-center justify-between items-center">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-8 h-8" />
                <div>
                  <div className="text-sm font-medium opacity-80">Nivel de Riesgo</div>
                  <div className="text-2xl font-semibold text-gray-900">{executive_summary.risk_level}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium opacity-80">Puntuación</div>
                <div className="text-2xl font-semibold text-gray-900">{executive_summary.risk_score}</div>
              </div>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-blue-500/30 rounded-xl p-4 text-center">
              <div className="text-2xl font-semibold text-gray-900 text-blue-400">{executive_summary.total_scans}</div>
              <div className="text-sm text-gray-500 mt-1">Scans Totales</div>
            </div>
            <div className="bg-white border border-red-500/30 rounded-xl p-4 text-center">
              <div className="text-2xl font-semibold text-gray-900 text-red-400">{executive_summary.total_vulnerabilities}</div>
              <div className="text-sm text-gray-500 mt-1">Vulnerabilidades</div>
            </div>
            <div className="bg-white border border-yellow-500/30 rounded-xl p-4 text-center">
              <div className="text-2xl font-semibold text-gray-900 text-yellow-400">{executive_summary.risk_score}</div>
              <div className="text-sm text-gray-500 mt-1">Puntuación de Riesgo</div>
            </div>
            <div className="bg-white border border-gray-200/30 rounded-xl p-4 text-center">
              <div className={`text-lg font-bold px-3 py-1 rounded inline-block ${
                executive_summary.risk_level === 'Critical' ? 'bg-red-50 text-red-700 border border-red-200' :
                executive_summary.risk_level === 'High' ? 'bg-orange-50 text-orange-700 border border-orange-200' :
                executive_summary.risk_level === 'Medium' ? 'bg-yellow-50 text-yellow-700 border border-yellow-200' :
                'bg-emerald-50 text-emerald-700 border border-emerald-200'
              }`}>
                {executive_summary.risk_level}
              </div>
              <div className="text-sm text-gray-500 mt-1">Nivel de Riesgo</div>
            </div>
          </div>

          {/* Severity Distribution */}
          <div className="bg-white border border-gray-200/30 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Distribución por Severidad
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(executive_summary.severity_distribution).map(([severity, count]) => (
                <div key={severity} className={`${getSeverityColor(severity)} rounded-xl p-4 text-center`}>
                  <div className="text-2xl font-semibold text-gray-900">{count as number}</div>
                  <div className="text-sm font-medium mt-1 capitalize">{severity}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Key Findings */}
          <div className="bg-white border border-gray-200/30 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              Hallazgos Clave
            </h3>
            <div className="space-y-3">
              {executive_summary.key_findings.map((finding, index) => (
                <div key={index} className="flex items-start gap-3 bg-gray-50/50 rounded-xl p-3">
                  <CheckCircle className="w-5 h-5 text-gray-800 mt-0.5 flex-shrink-0" />
                  <p className="text-gray-600 flex-1">{finding}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Remediation Roadmap */}
          {remediation_roadmap && (
            <div className="bg-white border border-blue-500/30 rounded-xl p-6">
              <h3 className="text-xl font-bold text-blue-400 mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Roadmap de Remediation
              </h3>
              <div className="space-y-4">
                {remediation_roadmap.immediate_action && (
                  (Array.isArray(remediation_roadmap.immediate_action) && remediation_roadmap.immediate_action.length > 0) ||
                  (!Array.isArray(remediation_roadmap.immediate_action) && remediation_roadmap.immediate_action.items && Array.isArray(remediation_roadmap.immediate_action.items) && remediation_roadmap.immediate_action.items.length > 0)
                ) && (
                  <div>
                    <h4 className="text-lg font-semibold text-red-400 mb-2">
                      ⚡ Acciones Inmediatas 
                      {!Array.isArray(remediation_roadmap.immediate_action) && remediation_roadmap.immediate_action.timeframe && ` (${remediation_roadmap.immediate_action.timeframe})`}
                    </h4>
                    <ul className="space-y-2">
                      {(Array.isArray(remediation_roadmap.immediate_action) 
                        ? remediation_roadmap.immediate_action 
                        : (remediation_roadmap.immediate_action.items || [])
                      ).map((action: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2 text-gray-600">
                          <span className="text-red-400 mt-1">•</span>
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {remediation_roadmap.short_term && (
                  (Array.isArray(remediation_roadmap.short_term) && remediation_roadmap.short_term.length > 0) ||
                  (!Array.isArray(remediation_roadmap.short_term) && remediation_roadmap.short_term.items && Array.isArray(remediation_roadmap.short_term.items) && remediation_roadmap.short_term.items.length > 0)
                ) && (
                  <div>
                    <h4 className="text-lg font-semibold text-orange-400 mb-2">
                      📅 Corto Plazo 
                      {!Array.isArray(remediation_roadmap.short_term) && remediation_roadmap.short_term.timeframe && ` (${remediation_roadmap.short_term.timeframe})`}
                    </h4>
                    <ul className="space-y-2">
                      {(Array.isArray(remediation_roadmap.short_term) 
                        ? remediation_roadmap.short_term 
                        : (remediation_roadmap.short_term.items || [])
                      ).map((action: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2 text-gray-600">
                          <span className="text-orange-400 mt-1">•</span>
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {remediation_roadmap.medium_term && (
                  (Array.isArray(remediation_roadmap.medium_term) && remediation_roadmap.medium_term.length > 0) ||
                  (!Array.isArray(remediation_roadmap.medium_term) && remediation_roadmap.medium_term.items && Array.isArray(remediation_roadmap.medium_term.items) && remediation_roadmap.medium_term.items.length > 0)
                ) && (
                  <div>
                    <h4 className="text-lg font-semibold text-yellow-400 mb-2">
                      📆 Mediano Plazo 
                      {!Array.isArray(remediation_roadmap.medium_term) && remediation_roadmap.medium_term.timeframe && ` (${remediation_roadmap.medium_term.timeframe})`}
                    </h4>
                    <ul className="space-y-2">
                      {(Array.isArray(remediation_roadmap.medium_term) 
                        ? remediation_roadmap.medium_term 
                        : (remediation_roadmap.medium_term.items || [])
                      ).map((action: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2 text-gray-600">
                          <span className="text-yellow-400 mt-1">•</span>
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {remediation_roadmap.long_term && (
                  (Array.isArray(remediation_roadmap.long_term) && remediation_roadmap.long_term.length > 0) ||
                  (!Array.isArray(remediation_roadmap.long_term) && remediation_roadmap.long_term.items && Array.isArray(remediation_roadmap.long_term.items) && remediation_roadmap.long_term.items.length > 0)
                ) && (
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">
                      🎯 Largo Plazo 
                      {!Array.isArray(remediation_roadmap.long_term) && remediation_roadmap.long_term.timeframe && ` (${remediation_roadmap.long_term.timeframe})`}
                    </h4>
                    <ul className="space-y-2">
                      {(Array.isArray(remediation_roadmap.long_term) 
                        ? remediation_roadmap.long_term 
                        : (remediation_roadmap.long_term.items || [])
                      ).map((action: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2 text-gray-600">
                          <span className="text-gray-900 mt-1">•</span>
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Risk Assessment Recommendations */}
          {risk_assessment && risk_assessment.recommendations && risk_assessment.recommendations.length > 0 && (
            <div className="bg-white border border-purple-500/30 rounded-xl p-6">
              <h3 className="text-xl font-bold text-purple-400 mb-4 flex items-center gap-2">
                <Target className="w-5 h-5" />
                Recomendaciones
              </h3>
              <ul className="space-y-2">
                {risk_assessment.recommendations.map((recommendation, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-gray-600">
                    <span className="text-purple-400 mt-1">•</span>
                    <span>{recommendation}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Scan Summary */}
          {scan_summary && scan_summary.length > 0 && (
            <div className="bg-white border border-cyan-500/30 rounded-xl p-6">
              <h3 className="text-xl font-bold text-cyan-400 mb-4 flex items-center gap-2">
                <Briefcase className="w-5 h-5" />
                Resumen de Scans ({scan_summary.length})
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-2 px-4 text-gray-500">ID</th>
                      <th className="text-left py-2 px-4 text-gray-500">Nombre</th>
                      <th className="text-left py-2 px-4 text-gray-500">Estado</th>
                      <th className="text-left py-2 px-4 text-gray-500">Fecha</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scan_summary.slice(0, 10).map((scan) => {
                      const scanId = scan.scan_id || scan.id || Math.random()
                      const scanName = scan.target || scan.name || 'Sin nombre'
                      const scanDate = scan.started_at || scan.created_at || scan.completed_at
                      return (
                        <tr key={scanId} className="border-b border-gray-200/50 hover:bg-gray-50/50">
                          <td className="py-2 px-4 text-gray-600">#{scanId}</td>
                          <td className="py-2 px-4 text-gray-600">{scanName}</td>
                          <td className="py-2 px-4">
                            <span className={`px-2 py-1 rounded text-xs ${
                              scan.status === 'completed' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                              scan.status === 'running' ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                              scan.status === 'failed' ? 'bg-red-50 text-red-700 border border-red-200' :
                              scan.status === 'cancelled' ? 'bg-yellow-50 text-yellow-700 border border-yellow-200' :
                              'bg-gray-50 text-gray-700 border border-gray-200'
                            }`}>
                              {scan.status}
                            </span>
                          </td>
                          <td className="py-2 px-4 text-gray-500 text-sm">
                            {scanDate ? new Date(scanDate).toLocaleDateString('es-AR') : 'N/A'}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
                {scan_summary.length > 10 && (
                  <div className="mt-4 text-center text-gray-500 text-sm">
                    Mostrando 10 de {scan_summary.length} scans
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ExecutiveReportModal

