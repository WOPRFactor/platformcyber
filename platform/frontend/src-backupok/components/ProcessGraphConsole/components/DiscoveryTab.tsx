/**
 * Discovery Tab Component
 * =======================
 * 
 * Componente para la pestaña de descubrimientos con gráficos y métricas.
 */

import React from 'react'
import { Search, Activity, BarChart3, Shield } from 'lucide-react'
import { Bar, Line } from 'react-chartjs-2'
import ChartWrapper from './ChartWrapper'
import { generateDiscoveryData, generateDiscoveryHistoryData, chartOptions } from '../utils/chartData'
import { Log } from '../../../contexts/ConsoleContext'

interface PentestMetrics {
  openPorts: number
  discoveredServices: number
  foundUrls: number
  sensitiveFiles: number
}

interface DiscoveryTabProps {
  metrics: PentestMetrics
  logs: Log[]
}

const DiscoveryTab: React.FC<DiscoveryTabProps> = ({ metrics, logs }) => {
  const discoveryData = generateDiscoveryData(metrics as any)
  const discoveryHistoryData = generateDiscoveryHistoryData(logs)

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Gráfico de barras de descubrimientos */}
        <ChartWrapper
          title="Descubrimientos del Pentesting"
          titleColor="text-blue-400"
          borderColor="border-blue-500"
        >
          <Bar data={discoveryData} options={chartOptions} />
        </ChartWrapper>

        {/* Métricas detalladas de descubrimientos */}
        <div className="space-y-4">
          <div className="bg-white p-4 rounded-xl border border-blue-500">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Search className="w-6 h-6 text-blue-400" />
                <span className="text-blue-400">Puertos Abiertos</span>
              </div>
              <span className="text-xl font-bold text-blue-400">{metrics.openPorts}</span>
            </div>
            <div className="mt-2 text-sm text-gray-500">
              TCP/UDP ports discovered
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-purple-500">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Activity className="w-6 h-6 text-purple-400" />
                <span className="text-purple-400">Servicios</span>
              </div>
              <span className="text-xl font-bold text-purple-400">{metrics.discoveredServices}</span>
            </div>
            <div className="mt-2 text-sm text-gray-500">
              HTTP, SSH, FTP, etc.
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <BarChart3 className="w-6 h-6 text-gray-900" />
                <span className="text-gray-900">URLs</span>
              </div>
              <span className="text-lg font-semibold text-gray-900">{metrics.foundUrls}</span>
            </div>
            <div className="mt-2 text-sm text-gray-500">
              Web pages discovered
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-red-500">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Shield className="w-6 h-6 text-red-400" />
                <span className="text-red-400">Archivos Sensibles</span>
              </div>
              <span className="text-xl font-bold text-red-400">{metrics.sensitiveFiles}</span>
            </div>
            <div className="mt-2 text-sm text-gray-500">
              Config files, backups, etc.
            </div>
          </div>
        </div>
      </div>

      {/* Gráfico histórico de descubrimientos */}
      <ChartWrapper
        title="Evolución de Descubrimientos"
        titleColor="text-gray-900"
        borderColor="border-gray-200"
        height="h-80"
      >
        <Line data={discoveryHistoryData} options={chartOptions} />
      </ChartWrapper>
    </div>
  )
}

export default DiscoveryTab


