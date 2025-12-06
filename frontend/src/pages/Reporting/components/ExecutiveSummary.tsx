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
    total_sessions: number
    completed_sessions: number
    critical_findings: number
    risk_level: string
    risk_score: number
    scan_types_performed: string[]
  }
  key_findings: Array<{
    finding: string
    scan_type: string
    target: string
    timestamp?: string
  }>
  recommendations: string[]
}

interface ExecutiveSummaryProps {
  data: ExecutiveSummaryData
}

const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({ data }) => {
  return (
    <div className="space-y-6">
      <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
        <h3 className="text-xl font-bold text-green-400 mb-4">📊 Resumen Ejecutivo</h3>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{data.executive_summary.total_sessions}</div>
            <div className="text-sm text-gray-600">Sesiones Totales</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">{data.executive_summary.completed_sessions}</div>
            <div className="text-sm text-gray-600">Completadas</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-red-600">{data.executive_summary.critical_findings}</div>
            <div className="text-sm text-gray-600">Hallazgos Críticos</div>
          </div>
          <div className={`text-center p-2 rounded ${
            data.executive_summary.risk_level === 'CRITICAL' ? 'bg-red-100 text-red-800' :
            data.executive_summary.risk_level === 'HIGH' ? 'bg-orange-100 text-orange-800' :
            data.executive_summary.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
            'bg-green-100 text-green-800'
          }`}>
            <div className="text-2xl font-bold">{data.executive_summary.risk_score}</div>
            <div className="text-sm">{data.executive_summary.risk_level}</div>
          </div>
        </div>

        <div className="mb-4">
          <h4 className="font-semibold mb-2">Tipos de Escaneo Realizados:</h4>
          <div className="flex flex-wrap gap-2">
            {data.executive_summary.scan_types_performed.map((type, idx) => (
              <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                {type.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      </div>

      {data.key_findings.length > 0 && (
        <div className="bg-gray-800 border border-red-500 rounded-lg p-6">
          <h3 className="text-xl font-bold text-red-400 mb-4">🔴 Hallazgos Críticos</h3>
          <div className="space-y-2">
            {data.key_findings.map((finding, idx) => (
              <div key={idx} className="border border-red-300 rounded p-3 bg-red-50">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-medium text-red-800">{finding.finding}</div>
                    <div className="text-sm text-red-600">
                      {finding.scan_type} - {finding.target}
                    </div>
                  </div>
                  <div className="text-sm text-red-500">
                    {finding.timestamp ? new Date(finding.timestamp).toLocaleDateString() : 'N/A'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-gray-800 border border-blue-500 rounded-lg p-6">
        <h3 className="text-xl font-bold text-blue-400 mb-4">📝 Recomendaciones</h3>
        <ul className="space-y-2">
          {data.recommendations.map((rec, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <span className="text-blue-700">{rec}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default ExecutiveSummary

