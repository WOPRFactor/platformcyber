import React from 'react'
import { Activity, Shield, AlertTriangle, CheckCircle, Clock, Zap, TrendingUp } from 'lucide-react'

interface KPICard {
  title: string
  value: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  bgColor: string
  trend: string | null
  subtitle: string
}

interface KPICardsProps {
  kpiCards: KPICard[]
  healthStatus: string | undefined
  activeScans: number
  totalVulnerabilities: number
}

export const KPICards: React.FC<KPICardsProps> = ({
  kpiCards,
  healthStatus,
  activeScans,
  totalVulnerabilities
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {kpiCards.map((kpi, index) => {
        const Icon = kpi.icon
        return (
          <div key={index} className={`card ${kpi.bgColor} relative overflow-hidden`}>
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm text-gray-500 mb-1">{kpi.title}</p>
                <p className={`text-2xl font-semibold text-gray-900 ${kpi.color} mb-1`}>
                  {kpi.value}
                </p>
                <p className="text-xs text-gray-500">{kpi.subtitle}</p>
                {kpi.trend && (
                  <div className="flex items-center mt-2">
                    <TrendingUp size={12} className="text-gray-900 mr-1" />
                    <span className="text-xs text-gray-900">{kpi.trend}</span>
                  </div>
                )}
              </div>
              <div className="flex flex-col items-end">
                <Icon className={`w-8 h-8 ${kpi.color} mb-2`} />
                <div className={`w-2 h-2 rounded-full animate-pulse ${
                  kpi.title === 'Estado del Sistema' ?
                    (healthStatus === 'healthy' ? 'bg-green-400' : 'bg-red-400') :
                  kpi.title === 'Escaneos Activos' ?
                    (activeScans > 0 ? 'bg-cyan-400' : 'bg-gray-400') :
                    'bg-blue-400'
                }`}></div>
              </div>
            </div>

            {kpi.title === 'Vulnerabilidades' && totalVulnerabilities > 0 && (
              <div className="mt-3">
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-red-400 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min((totalVulnerabilities / 20) * 100, 100)}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {totalVulnerabilities > 10 ? 'Requiere atención inmediata' : 'Bajo riesgo'}
                </p>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}


