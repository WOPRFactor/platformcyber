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
  if (!generatedReport) return null

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
            <option value="pdf">PDF</option>
            <option value="json">JSON</option>
          </select>
          <button
            onClick={handleExportReport}
            disabled={exportMutation.isPending}
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

      {generatedReport.report_type === 'executive_summary' && (
        <ExecutiveSummary data={generatedReport.data} />
      )}
      {generatedReport.report_type === 'technical_report' && (
        <TechnicalReport data={generatedReport.data} />
      )}
      {generatedReport.report_type === 'compliance_report' && (
        <ComplianceReport data={generatedReport.data} />
      )}
    </div>
  )
}

export default GeneratedReport

