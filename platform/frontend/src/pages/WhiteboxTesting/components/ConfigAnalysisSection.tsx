import React from 'react'
import { Settings, Loader } from 'lucide-react'
import { UseMutationResult } from '@tanstack/react-query'
import { ConfigIssuesList } from './ConfigIssuesList'

interface ConfigAnalysisSectionProps {
  mutation: UseMutationResult<any, any, any, any>
  onExecute: () => void
}

export const ConfigAnalysisSection: React.FC<ConfigAnalysisSectionProps> = ({ mutation, onExecute }) => {
  return (
    <div className="mt-4">
      <div className="bg-gray-900 border border-red-500 rounded-lg p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Análisis de Configuración
          </h3>
          <p className="text-red-600">
            Revisa configuraciones inseguras en servidores web, bases de datos y permisos
          </p>
        </div>
        <button
          onClick={onExecute}
          disabled={mutation.isPending}
          className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {mutation.isPending ? (
            <Loader className="w-4 h-4 animate-spin mr-2" />
          ) : (
            <Settings className="w-4 h-4 mr-2" />
          )}
          Ejecutar Análisis de Configuración
        </button>

        {mutation.data && (
          <div className="mt-6">
            <div className="bg-gray-800 border border-green-500 rounded-lg p-6 mb-4">
              <h4 className="font-semibold mb-4 text-green-400">Resumen de Configuración</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{mutation.data.data.summary.total_issues}</div>
                  <div className="text-sm text-gray-600">Total Problemas</div>
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
                  Tipos analizados: <span className="font-semibold">{mutation.data.data.config_types.join(', ')}</span>
                </p>
              </div>
            </div>

            {mutation.data.data.issues_found.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 text-red-400">Problemas de Configuración</h4>
                <ConfigIssuesList issues={mutation.data.data.issues_found} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}


