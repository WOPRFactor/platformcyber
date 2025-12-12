import React from 'react'
import { AlertTriangle, CheckCircle } from 'lucide-react'

interface SystemInfo {
  memory?: {
    percent: number
  }
  disk?: {
    percent: number
  }
}

interface SecurityAlertsProps {
  totalVulnerabilities: number
  systemInfo: SystemInfo | null
}

export const SecurityAlerts: React.FC<SecurityAlertsProps> = ({ totalVulnerabilities, systemInfo }) => {
  return (
    <div className="card">
      <h2 className="text-xl font-bold text-green-400 mb-4 flex items-center">
        <AlertTriangle className="w-5 h-5 mr-2" />
        Alertas de Seguridad
      </h2>

      <div className="space-y-3">
        {totalVulnerabilities > 10 ? (
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
            <div className="flex items-start space-x-3">
              <AlertTriangle size={20} className="text-red-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-red-400 font-medium text-sm">Alto Riesgo Detectado</p>
                <p className="text-red-300 text-xs mt-1">
                  {totalVulnerabilities} vulnerabilidades requieren atención inmediata
                </p>
              </div>
            </div>
          </div>
        ) : totalVulnerabilities > 5 ? (
          <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
            <div className="flex items-start space-x-3">
              <AlertTriangle size={20} className="text-yellow-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-yellow-400 font-medium text-sm">Riesgo Moderado</p>
                <p className="text-yellow-300 text-xs mt-1">
                  {totalVulnerabilities} vulnerabilidades detectadas
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
            <div className="flex items-start space-x-3">
              <CheckCircle size={20} className="text-green-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-green-400 font-medium text-sm">Estado Seguro</p>
                <p className="text-green-300 text-xs mt-1">
                  {totalVulnerabilities === 0 ? 'Sin vulnerabilidades detectadas' :
                   `${totalVulnerabilities} vulnerabilidades bajo control`}
                </p>
              </div>
            </div>
          </div>
        )}

        {systemInfo?.memory && systemInfo.memory.percent > 80 && (
          <div className="p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg">
            <div className="flex items-start space-x-3">
              <AlertTriangle size={20} className="text-orange-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-orange-400 font-medium text-sm">Alto Uso de Memoria</p>
                <p className="text-orange-300 text-xs mt-1">
                  {systemInfo.memory.percent}% de uso - Considere optimización
                </p>
              </div>
            </div>
          </div>
        )}

        {systemInfo?.disk && systemInfo.disk.percent > 90 && (
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
            <div className="flex items-start space-x-3">
              <AlertTriangle size={20} className="text-red-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-red-400 font-medium text-sm">Disco Casi Lleno</p>
                <p className="text-red-300 text-xs mt-1">
                  {systemInfo.disk.percent}% de uso - Limpieza requerida
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}


