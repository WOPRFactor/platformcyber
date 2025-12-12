/**
 * Reports Tab Component
 * =====================
 * 
 * Componente para la pestaña de análisis automático de reportes.
 */

import React from 'react'
import { FileText, Loader } from 'lucide-react'
import { UseMutationResult } from '@tanstack/react-query'

interface ReportData {
  content: string
  type: string
  target_info: any
}

interface ReportsTabProps {
  reportData: ReportData
  setReportData: (data: ReportData) => void
  onAnalyze: () => void
  reportAnalysisMutation: UseMutationResult<any, any, any>
}

const ReportsTab: React.FC<ReportsTabProps> = ({
  reportData,
  setReportData,
  onAnalyze,
  reportAnalysisMutation
}) => {
  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center space-x-2">
        <FileText size={20} />
        <span>Análisis Automático de Reportes</span>
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">Tipo de Reporte</label>
            <select
              value={reportData.type}
              onChange={(e) => setReportData({...reportData, type: e.target.value})}
              className="input w-full"
            >
              <option value="vulnerability_scan">Escaneo de Vulnerabilidades</option>
              <option value="penetration_test">Prueba de Penetración</option>
              <option value="web_application">Aplicación Web</option>
              <option value="network_audit">Auditoría de Red</option>
              <option value="compliance_check">Chequeo de Cumplimiento</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">Contenido del Reporte</label>
            <textarea
              value={reportData.content}
              onChange={(e) => setReportData({...reportData, content: e.target.value})}
              className="input w-full h-48 resize-none"
              placeholder="Pega aquí el contenido del reporte para análisis automático..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">Información del Objetivo</label>
            <input
              type="text"
              placeholder="IP, dominio o nombre del objetivo"
              className="input w-full"
              onChange={(e) => setReportData({...reportData, target_info: {target: e.target.value}})}
            />
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Análisis Automático</h3>
          <div className="bg-gray-50/50 p-4 rounded border border-gray-200/20">
            <p className="text-sm text-gray-500 mb-4">
              La IA analizará automáticamente el reporte y generará:
              resumen ejecutivo, hallazgos críticos, recomendaciones prioritarias y métricas de riesgo.
            </p>
            <button
              onClick={onAnalyze}
              disabled={reportAnalysisMutation.isPending || !reportData.content.trim()}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              {reportAnalysisMutation.isPending ? (
                <Loader size={16} className="animate-spin" />
              ) : (
                <FileText size={16} />
              )}
              <span>Analizar Reporte</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ReportsTab


