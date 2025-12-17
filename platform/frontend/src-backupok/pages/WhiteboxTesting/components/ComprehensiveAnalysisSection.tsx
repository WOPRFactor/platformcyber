import React from 'react'
import { Search, Loader } from 'lucide-react'
import { UseMutationResult } from '@tanstack/react-query'

interface ComprehensiveAnalysisSectionProps {
  mutation: UseMutationResult<any, any, any, any>
  onExecute: () => void
}

export const ComprehensiveAnalysisSection: React.FC<ComprehensiveAnalysisSectionProps> = ({ mutation, onExecute }) => {
  return (
    <div className="mt-4">
      <div className="bg-gray-50 border border-red-500 rounded-xl p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
            <Search className="w-5 h-5" />
            Análisis Whitebox Completo
          </h3>
          <p className="text-red-600">
            Ejecuta todos los análisis whitebox disponibles en secuencia
          </p>
        </div>
        <div className="border border-yellow-500 bg-yellow-50 p-4 rounded-xl mb-4">
          <p className="text-yellow-800">
            🔍 <strong>Análisis completo puede tomar tiempo</strong> dependiendo del tamaño del codebase
          </p>
        </div>
        <button
          onClick={onExecute}
          disabled={mutation.isPending}
          className="w-full bg-gradient-to-r from-red-600 to-purple-600 hover:from-red-700 hover:to-purple-700 text-white px-4 py-2 rounded-xl flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {mutation.isPending ? (
            <Loader className="w-4 h-4 animate-spin mr-2" />
          ) : (
            <Search className="w-4 h-4 mr-2" />
          )}
          Ejecutar Análisis Completo
        </button>

        {mutation.data && (
          <div className="mt-6">
            <div className="bg-white border border-gray-200 rounded-xl p-6 mb-4">
              <h4 className="font-semibold mb-4 text-gray-900">Resumen del Análisis Completo</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{mutation.data.summary.total_phases}</div>
                  <div className="text-sm text-gray-600">Fases Ejecutadas</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-500">{mutation.data.summary.successful_phases}</div>
                  <div className="text-sm text-gray-600">Exitosas</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{mutation.data.summary.total_findings}</div>
                  <div className="text-sm text-gray-600">Hallazgos Totales</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{mutation.data.summary.failed_phases}</div>
                  <div className="text-sm text-gray-600">Fallidas</div>
                </div>
              </div>
              <div className="mt-4">
                <p className="text-sm text-gray-500">{mutation.data.summary.recommendation}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}


