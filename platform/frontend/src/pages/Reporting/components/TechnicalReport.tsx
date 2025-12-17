/**
 * Technical Report Component
 * ===========================
 * 
 * Componente para renderizar reporte técnico.
 */

import React from 'react'

interface TechnicalReportData {
  vulnerability_summary: {
    high: number
    medium: number
    low: number
    info: number
  }
  scan_methodology: {
    reconnaissance: any[]
    scanning: any[]
    vulnerability_assessment: any[]
    exploitation: any[]
    post_exploitation: any[]
  }
}

interface TechnicalReportProps {
  data: TechnicalReportData
}

const TechnicalReport: React.FC<TechnicalReportProps> = ({ data }) => {
  return (
    <div className="space-y-6">
      <div className="bg-gray-100 border border-gray-300 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔧 Resumen de Vulnerabilidades</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-red-100 rounded">
            <div className="text-2xl font-bold text-red-600">{data.vulnerability_summary.high}</div>
            <div className="text-sm text-red-800">Alta Severidad</div>
          </div>
          <div className="text-center p-4 bg-orange-100 rounded">
            <div className="text-2xl font-bold text-orange-600">{data.vulnerability_summary.medium}</div>
            <div className="text-sm text-orange-800">Media Severidad</div>
          </div>
          <div className="text-center p-4 bg-yellow-100 rounded">
            <div className="text-2xl font-bold text-yellow-600">{data.vulnerability_summary.low}</div>
            <div className="text-sm text-yellow-800">Baja Severidad</div>
          </div>
          <div className="text-center p-4 bg-gray-100 rounded">
            <div className="text-2xl font-bold text-gray-600">{data.vulnerability_summary.info}</div>
            <div className="text-sm text-gray-800">Informativas</div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-blue-500 rounded-xl p-6">
        <h3 className="text-xl font-bold text-blue-400 mb-4">📋 Metodología de Escaneo</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <h4 className="font-semibold mb-2 text-blue-300">Reconocimiento</h4>
            <div className="text-sm text-blue-200">{data.scan_methodology.reconnaissance.length} sesiones</div>
          </div>
          <div>
            <h4 className="font-semibold mb-2 text-blue-300">Escaneo</h4>
            <div className="text-sm text-blue-200">{data.scan_methodology.scanning.length} sesiones</div>
          </div>
          <div>
            <h4 className="font-semibold mb-2 text-blue-300">Evaluación de Vuln.</h4>
            <div className="text-sm text-blue-200">{data.scan_methodology.vulnerability_assessment.length} sesiones</div>
          </div>
          <div>
            <h4 className="font-semibold mb-2 text-blue-300">Explotación</h4>
            <div className="text-sm text-blue-200">{data.scan_methodology.exploitation.length} sesiones</div>
          </div>
          <div>
            <h4 className="font-semibold mb-2 text-blue-300">Post-Explotación</h4>
            <div className="text-sm text-blue-200">{data.scan_methodology.post_exploitation.length} sesiones</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TechnicalReport

