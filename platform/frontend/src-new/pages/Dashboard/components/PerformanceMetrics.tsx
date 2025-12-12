import React from 'react'
import { TrendingUp } from 'lucide-react'

interface PerformanceMetricsProps {
  totalScans: number
  scanSessions: Array<{ status: string }> | undefined
  totalVulnerabilities: number
  avgScanTime: number
  completedAudits: number
}

export const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({
  totalScans,
  scanSessions,
  totalVulnerabilities,
  avgScanTime,
  completedAudits
}) => {
  const successRate = totalScans > 0 
    ? Math.round(((totalScans - (scanSessions?.filter(s => s.status === 'error').length || 0)) / totalScans) * 100)
    : 0

  const detectionEfficiency = totalScans > 0 
    ? Math.round((totalVulnerabilities / totalScans) * 100) / 100
    : 0

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <TrendingUp className="w-5 h-5 mr-2" />
        Rendimiento
      </h2>

      <div className="space-y-4">
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-500">Disponibilidad del Sistema</span>
            <span className="text-gray-900 text-sm font-medium">99.9%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div className="bg-green-400 h-2 rounded-full" style={{ width: '99.9%' }}></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-500">Tasa de Éxito de Escaneos</span>
            <span className="text-blue-400 text-sm font-medium">
              {successRate}%
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div className="bg-blue-400 h-2 rounded-full" style={{
              width: `${successRate}%`
            }}></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-500">Eficiencia de Detección</span>
            <span className="text-purple-400 text-sm font-medium">
              {detectionEfficiency} vuln/escaneo
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div className="bg-purple-400 h-2 rounded-full" style={{
              width: `${Math.min((totalVulnerabilities / Math.max(totalScans, 1)) * 20, 100)}%`
            }}></div>
          </div>
        </div>

        <div className="pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {Math.round(avgScanTime) || 'N/A'}
              </p>
              <p className="text-xs text-gray-500">Min promedio</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-cyan-400">
                {completedAudits}
              </p>
              <p className="text-xs text-gray-500">Auditorías OK</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}


