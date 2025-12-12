/**
 * Generated Report Component
 * ===========================
 * 
 * Componente para mostrar reporte generado con opciones de exportación.
 */

import React from 'react'
import { Download, Loader } from 'lucide-react'
import { UseMutationResult } from '@tanstack/react-query'
import ExecutiveSummary from './ExecutiveSummary'
import TechnicalReport from './TechnicalReport'
import ComplianceReport from './ComplianceReport'

interface GeneratedReportProps {
  generatedReport: any
  exportFormat: 'json' | 'html' | 'pdf'
  setExportFormat: (format: 'json' | 'html' | 'pdf') => void
  exportMutation: UseMutationResult<any, any, any>
  handleExportReport: () => void
}

const GeneratedReport: React.FC<GeneratedReportProps> = ({
  generatedReport,
  exportFormat,
  setExportFormat,
  exportMutation,
  handleExportReport
}) => {
  console.log('🎨 GeneratedReport rendering with:', generatedReport)

  if (!generatedReport) {
    console.log('❌ generatedReport is null/undefined')
    return null
  }

  // Determinar tipo de reporte desde metadata o estructura
  const reportType = generatedReport.metadata?.report_type ||
                     (generatedReport.executive_summary ? 'executive' :
                      generatedReport.technical_details ? 'technical' :
                      generatedReport.compliance_mapping ? 'compliance' : 'full')

  console.log('📋 Report type determined:', reportType)

  return (
    <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-green-400">Reporte Generado</h2>
        <div className="flex gap-2">
          <select
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value as 'json' | 'html' | 'pdf')}
            className="bg-gray-900 border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="html">HTML</option>
            <option value="json">JSON</option>
            <option value="pdf" disabled>PDF (Próximamente)</option>
          </select>
          <button
            onClick={handleExportReport}
            disabled={exportMutation.isPending || exportFormat === 'pdf'}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {exportMutation.isPending ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            Exportar
          </button>
        </div>
      </div>

      {(reportType === 'executive' || reportType === 'full') && generatedReport.executive_summary && (
        <div>
          <h3 className="text-green-400 text-lg font-bold mb-2">📊 Resumen Ejecutivo</h3>
          <ExecutiveSummary data={generatedReport} />
        </div>
      )}
      {(reportType === 'technical' || reportType === 'full') && generatedReport.technical_details && (
        <TechnicalReport data={generatedReport} />
      )}
      {(reportType === 'compliance' || reportType === 'full') && generatedReport.compliance_mapping && (
        <ComplianceReport data={generatedReport} />
      )}
      
      {reportType === 'full' && (
        <div className="mt-4 p-4 bg-gray-900 rounded">
          <p className="text-green-400 text-sm">
            Este es un reporte completo que incluye todas las secciones. Usa las pestañas arriba para ver secciones específicas.
          </p>
        </div>
      )}
    </div>
  )
}

export default GeneratedReport

