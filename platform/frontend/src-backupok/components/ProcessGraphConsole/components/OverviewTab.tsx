/**
 * Overview Tab Component
 * =======================
 * 
 * Componente para la pestaña de vista general con métricas principales.
 */

import React from 'react'
import { Search, Shield, Activity, BarChart3 } from 'lucide-react'
import { Doughnut } from 'react-chartjs-2'
import MetricCard from './MetricCard'
import ChartWrapper from './ChartWrapper'
import { generateVulnerabilityData, chartOptions } from '../utils/chartData'

interface PentestMetrics {
  openPorts: number
  vulnerabilities: {
    critical: number
    high: number
    medium: number
    low: number
  }
  scannedHosts: number
  discoveredServices: number
  foundUrls: number
  sensitiveFiles: number
  scanProgress: number
}

interface OverviewTabProps {
  metrics: PentestMetrics
}

const OverviewTab: React.FC<OverviewTabProps> = ({ metrics }) => {
  const vulnerabilityData = generateVulnerabilityData(metrics)
  const totalVulnerabilities = Object.values(metrics.vulnerabilities).reduce((a, b) => a + b, 0)

  return (
    <div className="space-y-6">
      {/* Métricas principales de pentesting */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          label="Puertos Abiertos"
          value={metrics.openPorts}
          icon={Search}
          borderColor="border-blue-500"
          textColor="text-blue-400"
          iconColor="text-blue-400"
        />
        <MetricCard
          label="Vulnerabilidades"
          value={totalVulnerabilities}
          icon={Shield}
          borderColor="border-red-500"
          textColor="text-red-400"
          iconColor="text-red-400"
        />
        <MetricCard
          label="Hosts Escaneados"
          value={metrics.scannedHosts}
          icon={Activity}
          borderColor="border-gray-200"
          textColor="text-gray-900"
          iconColor="text-gray-900"
        />
        <MetricCard
          label="Progreso Global"
          value={`${metrics.scanProgress}%`}
          icon={BarChart3}
          borderColor="border-yellow-500"
          textColor="text-yellow-400"
          iconColor="text-yellow-400"
        />
      </div>

      {/* Gráfico de distribución de vulnerabilidades */}
      <ChartWrapper
        title="Resumen de Vulnerabilidades"
        titleColor="text-red-400"
        borderColor="border-red-500"
      >
        <Doughnut data={vulnerabilityData} options={chartOptions} />
      </ChartWrapper>
    </div>
  )
}

export default OverviewTab


