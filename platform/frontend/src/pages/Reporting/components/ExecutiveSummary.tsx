/**
 * Executive Summary Component
 * ============================
 * 
 * Componente para renderizar resumen ejecutivo.
 */

import React from 'react'
import { CheckCircle } from 'lucide-react'

interface ExecutiveSummaryData {
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
  }
}

interface ExecutiveSummaryProps {
  data: ExecutiveSummaryData
}

const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({ data }) => {
  return (
    <div className="space-y-6">
      <div className="bg-gray-100 border border-gray-300 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Resumen Ejecutivo</h3>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-semibold text-gray-900 text-blue-600">{data.executive_summary.total_scans}</div>
            <div className="text-sm text-gray-500">Scans Totales</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-semibold text-gray-900 text-gray-500">{data.executive_summary.total_vulnerabilities}</div>
            <div className="text-sm text-gray-500">Vulnerabilidades</div>
          </div>
          <div className="text-center">
            <div className={`text-2xl font-semibold text-gray-900 ${
              data.executive_summary.risk_level === 'Critical' ? 'text-red-600' :
              data.executive_summary.risk_level === 'High' ? 'text-orange-600' :
              data.executive_summary.risk_level === 'Medium' ? 'text-yellow-600' :
              'text-gray-500'
            }`}>
              {data.executive_summary.risk_score}
            </div>
            <div className="text-sm text-gray-500">Puntuación de Riesgo</div>
          </div>
          <div className="text-center">
            <div className={`text-lg font-bold px-2 py-1 rounded ${
              data.executive_summary.risk_level === 'Critical' ? 'bg-red-50 text-red-700 border border-red-200' :
              data.executive_summary.risk_level === 'High' ? 'bg-orange-50 text-orange-700 border border-orange-200' :
              data.executive_summary.risk_level === 'Medium' ? 'bg-yellow-50 text-yellow-700 border border-yellow-200' :
              'bg-emerald-50 text-emerald-700 border border-emerald-200'
            }`}>
              {data.executive_summary.risk_level}
            </div>
            <div className="text-sm text-gray-500">Nivel de Riesgo</div>
          </div>
        </div>

        <div className="bg-gray-50 p-4 rounded-xl">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">🔍 Hallazgos Clave</h4>
          <div className="space-y-2">
            {data.executive_summary.key_findings.map((finding, index) => (
              <div key={index} className="flex items-start space-x-2">
                <CheckCircle className="w-5 h-5 text-gray-800 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-gray-600">{finding}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

        <div className="bg-gray-50 p-4 rounded-xl">
          <h4 className="text-lg font-semibold text-blue-400 mb-2">📊 Distribución por Severidad</h4>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(data.executive_summary.severity_distribution).map(([severity, count]) => (
              <div key={severity} className="text-center">
                <div className={`text-2xl font-bold ${
                  severity === 'critical' ? 'text-red-400' :
                  severity === 'high' ? 'text-orange-400' :
                  severity === 'medium' ? 'text-yellow-400' :
                  severity === 'low' ? 'text-blue-400' :
                  'text-gray-500'
                }`}>
                  {count as number}
                </div>
                <div className="text-sm text-gray-500 capitalize">{severity}</div>
              </div>
            ))}
          </div>
        </div>

        {data.metadata && (
          <div className="mt-4 p-4 bg-gray-50 rounded">
            <h4 className="text-lg font-semibold text-purple-400 mb-2">📄 Información del Reporte</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Tipo:</span>
                <span className="ml-2 text-gray-200 capitalize">{data.metadata.report_type}</span>
              </div>
              <div>
                <span className="text-gray-500">Workspace:</span>
                <span className="ml-2 text-gray-200">#{data.metadata.workspace_id}</span>
              </div>
              <div>
                <span className="text-gray-500">Generado:</span>
                <span className="ml-2 text-gray-200">
                  {new Date(data.metadata.generated_at).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        )}
    </div>
  )
}

export default ExecutiveSummary

