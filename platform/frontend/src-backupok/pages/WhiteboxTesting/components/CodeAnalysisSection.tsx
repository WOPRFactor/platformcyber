import React from 'react'
import { Code, Loader } from 'lucide-react'
import { UseMutationResult } from '@tanstack/react-query'
import { CodeFindingsList } from './CodeFindingsList'

interface CodeAnalysisSectionProps {
  mutation: UseMutationResult<any, any, any, any>
  onExecute: () => void
}

export const CodeAnalysisSection: React.FC<CodeAnalysisSectionProps> = ({ mutation, onExecute }) => {
  return (
    <div className="mt-4">
      <div className="bg-gray-50 border border-red-500 rounded-xl p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
            <Code className="w-5 h-5" />
            Análisis Estático de Código
          </h3>
          <p className="text-red-600">
            Detecta vulnerabilidades, malas prácticas y problemas de seguridad en el código fuente
          </p>
        </div>
        <button
          onClick={onExecute}
          disabled={mutation.isPending}
          className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {mutation.isPending ? (
            <Loader className="w-4 h-4 animate-spin mr-2" />
          ) : (
            <Code className="w-4 h-4 mr-2" />
          )}
          Ejecutar Análisis de Código
        </button>

        {mutation.data && (
          <div className="mt-6">
            <div className="bg-white border border-gray-200 rounded-xl p-6 mb-4">
              <h4 className="font-semibold mb-4 text-gray-900">Resumen del Análisis</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{mutation.data.data.summary.total_findings}</div>
                  <div className="text-sm text-gray-600">Total Hallazgos</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{mutation.data.data.summary.severity_breakdown.critical || 0}</div>
                  <div className="text-sm text-gray-600">Críticos</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{mutation.data.data.summary.severity_breakdown.high || 0}</div>
                  <div className="text-sm text-gray-600">Altos</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">{mutation.data.data.summary.severity_breakdown.medium || 0}</div>
                  <div className="text-sm text-gray-600">Medios</div>
                </div>
              </div>
              <div className="mt-4">
                <p className="text-sm text-gray-600">
                  Lenguaje detectado: <span className="font-semibold">{mutation.data.data.language}</span>
                </p>
                <p className="text-sm text-gray-600">
                  Tipo más común: <span className="font-semibold">{mutation.data.data.summary.most_common_type}</span>
                </p>
              </div>
            </div>

            {mutation.data.data.findings.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 text-red-400">Hallazgos Detectados</h4>
                <CodeFindingsList findings={mutation.data.data.findings} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}


