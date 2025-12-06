/**
 * Report Generator Component
 * ===========================
 * 
 * Componente para generar reportes según el tipo seleccionado.
 */

import React from 'react'
import { BarChart3, Target, Shield, Loader } from 'lucide-react'
import { UseMutationResult } from '@tanstack/react-query'

interface ReportGeneratorProps {
  activeTab: string
  complianceStandard: string
  executiveMutation: UseMutationResult<any, any, any>
  technicalMutation: UseMutationResult<any, any, any>
  complianceMutation: UseMutationResult<any, any, any>
  handleGenerateReport: (reportType: string) => void
}

const ReportGenerator: React.FC<ReportGeneratorProps> = ({
  activeTab,
  complianceStandard,
  executiveMutation,
  technicalMutation,
  complianceMutation,
  handleGenerateReport
}) => {
  return (
    <div className="w-full">
        {activeTab === 'executive' && (
          <div className="mt-4">
            <div className="bg-gray-900 border border-red-500 rounded-lg p-6">
              <div className="mb-4">
                <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Resumen Ejecutivo
                </h3>
                <p className="text-red-600">
                  Reporte de alto nivel para stakeholders y directivos
                </p>
              </div>
              <button
                onClick={() => handleGenerateReport('executive')}
                disabled={executiveMutation.isPending}
                className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {executiveMutation.isPending ? (
                  <Loader className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <BarChart3 className="w-4 h-4 mr-2" />
                )}
                Generar Resumen Ejecutivo
              </button>
            </div>
          </div>
        )}

        {activeTab === 'technical' && (
          <div className="mt-4">
            <div className="bg-gray-900 border border-red-500 rounded-lg p-6">
              <div className="mb-4">
                <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Reporte Técnico Detallado
                </h3>
                <p className="text-red-600">
                  Reporte técnico completo con todos los hallazgos y metodología
                </p>
              </div>
              <button
                onClick={() => handleGenerateReport('technical')}
                disabled={technicalMutation.isPending}
                className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {technicalMutation.isPending ? (
                  <Loader className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <Target className="w-4 h-4 mr-2" />
                )}
                Generar Reporte Técnico
              </button>
            </div>
          </div>
        )}

        {activeTab === 'compliance' && (
          <div className="mt-4">
            <div className="bg-gray-900 border border-red-500 rounded-lg p-6">
              <div className="mb-4">
                <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  Reporte de Cumplimiento - {complianceStandard.toUpperCase()}
                </h3>
                <p className="text-red-600">
                  Evaluación de cumplimiento con estándares de seguridad específicos
                </p>
              </div>
              <button
                onClick={() => handleGenerateReport('compliance')}
                disabled={complianceMutation.isPending}
                className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {complianceMutation.isPending ? (
                  <Loader className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <Shield className="w-4 h-4 mr-2" />
                )}
                Generar Reporte de Cumplimiento
              </button>
            </div>
          </div>
        )}
    </div>
  )
}

export default ReportGenerator

