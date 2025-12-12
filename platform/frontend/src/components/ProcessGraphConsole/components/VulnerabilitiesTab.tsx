/**
 * Vulnerabilities Tab Component
 * =============================
 * 
 * Componente para la pestaña de vulnerabilidades con distribución y métricas detalladas.
 */

import React from 'react'
import { Shield } from 'lucide-react'
import { Doughnut } from 'react-chartjs-2'
import ChartWrapper from './ChartWrapper'
import { generateVulnerabilityData, chartOptions } from '../utils/chartData'

interface PentestMetrics {
  vulnerabilities: {
    critical: number
    high: number
    medium: number
    low: number
  }
}

interface VulnerabilitiesTabProps {
  metrics: PentestMetrics
}

const VulnerabilitiesTab: React.FC<VulnerabilitiesTabProps> = ({ metrics }) => {
  const vulnerabilityData = generateVulnerabilityData({ vulnerabilities: metrics.vulnerabilities } as any)

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Gráfico de distribución de vulnerabilidades */}
        <ChartWrapper
          title="Distribución de Vulnerabilidades"
          titleColor="text-red-400"
          borderColor="border-red-500"
        >
          <Doughnut data={vulnerabilityData} options={chartOptions} />
        </ChartWrapper>

        {/* Métricas detalladas de vulnerabilidades */}
        <div className="space-y-4">
          <div className="bg-gray-800 p-4 rounded-lg border border-red-600">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Shield className="w-6 h-6 text-red-600" />
                <span className="text-red-400">Críticas</span>
              </div>
              <span className="text-xl font-bold text-red-600">{metrics.vulnerabilities.critical}</span>
            </div>
            <div className="mt-2 text-sm text-gray-400">
              Requieren atención inmediata
            </div>
          </div>

          <div className="bg-gray-800 p-4 rounded-lg border border-red-500">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Shield className="w-6 h-6 text-red-500" />
                <span className="text-red-400">Altas</span>
              </div>
              <span className="text-xl font-bold text-red-500">{metrics.vulnerabilities.high}</span>
            </div>
            <div className="mt-2 text-sm text-gray-400">
              Alto riesgo de explotación
            </div>
          </div>

          <div className="bg-gray-800 p-4 rounded-lg border border-yellow-500">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Shield className="w-6 h-6 text-yellow-500" />
                <span className="text-yellow-400">Medias</span>
              </div>
              <span className="text-xl font-bold text-yellow-500">{metrics.vulnerabilities.medium}</span>
            </div>
            <div className="mt-2 text-sm text-gray-400">
              Riesgo moderado
            </div>
          </div>

          <div className="bg-gray-800 p-4 rounded-lg border border-green-500">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Shield className="w-6 h-6 text-green-500" />
                <span className="text-green-400">Bajas</span>
              </div>
              <span className="text-xl font-bold text-green-500">{metrics.vulnerabilities.low}</span>
            </div>
            <div className="mt-2 text-sm text-gray-400">
              Riesgo mínimo
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default VulnerabilitiesTab


