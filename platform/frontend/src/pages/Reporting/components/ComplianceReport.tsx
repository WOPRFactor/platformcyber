/**
 * Compliance Report Component
 * ============================
 * 
 * Componente para renderizar reporte de cumplimiento.
 */

import React from 'react'
import { CheckCircle, XCircle } from 'lucide-react'

interface ComplianceReportData {
  standard: string
  compliance_score: number
  requirements: Array<{
    id: string
    description: string
    status: 'PASS' | 'FAIL'
  }>
  violations: string[]
  recommendations: string[]
}

interface ComplianceReportProps {
  data: ComplianceReportData
}

const ComplianceReport: React.FC<ComplianceReportProps> = ({ data }) => {
  return (
    <div className="space-y-6">
      <div className="bg-gray-100 border border-gray-300 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 Reporte de Cumplimiento - {data.standard}</h3>

        <div className="text-center mb-6">
          <div className={`inline-block p-6 rounded-full ${
            data.compliance_score >= 80 ? 'bg-green-100' :
            data.compliance_score >= 60 ? 'bg-yellow-100' : 'bg-red-100'
          }`}>
            <div className={`text-4xl font-bold ${
              data.compliance_score >= 80 ? 'text-gray-500' :
              data.compliance_score >= 60 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {data.compliance_score}%
            </div>
            <div className="text-sm text-gray-600">Puntuación de Cumplimiento</div>
          </div>
        </div>

        <div className="mb-6">
          <h4 className="font-semibold mb-3">Requisitos Evaluados:</h4>
          <div className="space-y-2">
            {data.requirements.map((req, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 border rounded">
                <div>
                  <div className="font-medium">{req.id}: {req.description}</div>
                </div>
                <span className={`px-3 py-1 rounded text-sm ${
                  req.status === 'PASS' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {req.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {data.violations.length > 0 && (
          <div className="mb-6">
            <h4 className="font-semibold mb-3 text-red-400">Violaciones Identificadas:</h4>
            <ul className="space-y-1">
              {data.violations.map((violation, idx) => (
                <li key={idx} className="flex items-start gap-2 text-red-700">
                  <XCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>{violation}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div>
          <h4 className="font-semibold mb-3 text-blue-400">Recomendaciones:</h4>
          <ul className="space-y-1">
            {data.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start gap-2 text-blue-700">
                <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

export default ComplianceReport

