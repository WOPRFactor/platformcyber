/**
 * Predictive Tab Component
 * ========================
 * 
 * Componente para la pestaña de análisis predictivo.
 */

import React from 'react'
import { TrendingUp, Loader } from 'lucide-react'
import { UseMutationResult } from '@tanstack/react-query'

interface PredictiveTabProps {
  onAnalyze: () => void
  predictiveAnalysisMutation: UseMutationResult<any, any, any>
}

const PredictiveTab: React.FC<PredictiveTabProps> = ({ onAnalyze, predictiveAnalysisMutation }) => {
  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center space-x-2">
        <TrendingUp size={20} />
        <span>Análisis Predictivo de Vulnerabilidades</span>
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Información del Objetivo</h3>
          <div className="space-y-2">
            <input
              type="text"
              placeholder="IP o dominio objetivo"
              className="input w-full"
              defaultValue="192.168.1.100"
            />
            <input
              type="text"
              placeholder="Puertos encontrados"
              className="input w-full"
              defaultValue="80, 443, 22"
            />
            <textarea
              placeholder="Resultados de escaneo previos..."
              className="input w-full h-24 resize-none"
              defaultValue="HTTP service detected&#10;SSL/TLS enabled&#10;Possible outdated software"
            />
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Análisis Predictivo</h3>
          <div className="bg-gray-50/50 p-4 rounded border border-gray-200/20">
            <p className="text-sm text-gray-500 mb-2">
              La IA analizará el objetivo y predecirá posibles vulnerabilidades basándose en patrones históricos.
            </p>
            <button
              onClick={onAnalyze}
              disabled={predictiveAnalysisMutation.isPending}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              {predictiveAnalysisMutation.isPending ? (
                <Loader size={16} className="animate-spin" />
              ) : (
                <TrendingUp size={16} />
              )}
              <span>Iniciar Análisis Predictivo</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PredictiveTab


