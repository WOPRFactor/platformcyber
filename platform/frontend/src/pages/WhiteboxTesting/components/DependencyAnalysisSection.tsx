import React from 'react'
import { Package, Loader } from 'lucide-react'
import { UseMutationResult } from '@tanstack/react-query'
import { DependencyFindingsList } from './DependencyFindingsList'

interface DependencyAnalysisSectionProps {
  mutation: UseMutationResult<any, any, any, any>
  onExecute: () => void
}

export const DependencyAnalysisSection: React.FC<DependencyAnalysisSectionProps> = ({ mutation, onExecute }) => {
  return (
    <div className="mt-4">
      <div className="bg-gray-900 border border-red-500 rounded-lg p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
            <Package className="w-5 h-5" />
            Análisis de Dependencias
          </h3>
          <p className="text-red-600">
            Identifica dependencias vulnerables y paquetes desactualizados
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
            <Package className="w-4 h-4 mr-2" />
          )}
          Ejecutar Análisis de Dependencias
        </button>

        {mutation.data && (
          <div className="mt-6">
            <div className="bg-gray-800 border border-green-500 rounded-lg p-6 mb-4">
              <h4 className="font-semibold mb-4 text-green-400">Resumen de Dependencias</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{mutation.data.data.summary.total_vulnerable}</div>
                  <div className="text-sm text-gray-600">Vulnerables</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{mutation.data.data.summary.total_outdated}</div>
                  <div className="text-sm text-gray-600">Desactualizadas</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{mutation.data.data.summary.severity_breakdown.critical || 0}</div>
                  <div className="text-sm text-gray-600">Críticas</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{mutation.data.data.summary.severity_breakdown.high || 0}</div>
                  <div className="text-sm text-gray-600">Altas</div>
                </div>
              </div>
              <div className="mt-4">
                <p className="text-sm text-gray-600">
                  Gestor detectado: <span className="font-semibold">{mutation.data.data.package_manager}</span>
                </p>
              </div>
            </div>

            {mutation.data.data.vulnerable_dependencies.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 text-red-400">Dependencias Vulnerables</h4>
                <DependencyFindingsList dependencies={mutation.data.data.vulnerable_dependencies} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}


