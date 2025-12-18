import React from 'react'
import { Activity, AlertTriangle } from 'lucide-react'
import LoadingSpinner from '../../../components/LoadingSpinner'

interface SystemInfo {
  cpu_count: number
  cpu_percent?: number
  memory: {
    available: number
    percent: number
    total: number
  }
  disk: {
    free: number
    percent: number
    total: number
  }
  platform: string
  python_version: string
}

interface SystemInfoProps {
  systemInfo: SystemInfo | null
  isLoading: boolean
}

export const SystemInfo: React.FC<SystemInfoProps> = ({ systemInfo, isLoading }) => {
  if (isLoading) {
    return (
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Activity className="w-5 h-5 mr-2" />
          Información del Sistema
        </h2>
        <LoadingSpinner message="Cargando información del sistema..." />
      </div>
    )
  }

  if (!systemInfo) {
    return (
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Activity className="w-5 h-5 mr-2" />
          Información del Sistema
        </h2>
        <div className="text-center py-8 text-red-400">
          <AlertTriangle size={48} className="mx-auto mb-4 opacity-50" />
          <p>No se pudo obtener información del sistema</p>
          <p className="text-sm mt-2">Verifique la conexión con el backend</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Activity className="w-5 h-5 mr-2" />
        Información del Sistema
      </h2>

      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Hardware</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-500">CPU:</span>
              <div className="flex items-center space-x-2">
                <span className="text-gray-900 font-medium">
                  {systemInfo.cpu_count || 'Cargando...'} núcleos
                  {systemInfo.cpu_percent !== undefined && ` (${systemInfo.cpu_percent.toFixed(1)}%)`}
                </span>
                <div className="w-16 bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      (systemInfo.cpu_percent || 0) > 80 ? 'bg-red-400' :
                      (systemInfo.cpu_percent || 0) > 60 ? 'bg-yellow-400' : 'bg-green-400'
                    }`}
                    style={{ width: `${systemInfo.cpu_percent || 0}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-gray-500">Memoria:</span>
              <div className="flex items-center space-x-2">
                <span className="text-blue-400 font-medium">
                  {`${((systemInfo.memory.total - systemInfo.memory.available) / 1024 / 1024 / 1024).toFixed(1)}/` +
                    `${(systemInfo.memory.total / 1024 / 1024 / 1024).toFixed(1)} GB`}
                </span>
                <div className="w-16 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      systemInfo.memory.percent > 80 ? 'bg-red-400' :
                      systemInfo.memory.percent > 60 ? 'bg-yellow-400' : 'bg-blue-400'
                    }`}
                    style={{ width: `${systemInfo.memory.percent || 0}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-gray-500">Disco:</span>
              <div className="flex items-center space-x-2">
                <span className="text-purple-400 font-medium">
                  {`${((systemInfo.disk.total - systemInfo.disk.free) / 1024 / 1024 / 1024).toFixed(1)}/` +
                    `${(systemInfo.disk.total / 1024 / 1024 / 1024).toFixed(1)} GB`}
                </span>
                <div className="w-16 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      systemInfo.disk.percent > 90 ? 'bg-red-400' :
                      systemInfo.disk.percent > 70 ? 'bg-yellow-400' : 'bg-purple-400'
                    }`}
                    style={{ width: `${systemInfo.disk.percent || 0}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-gray-200">
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-500">Python Version:</span>
            <span className="text-gray-900">{systemInfo.python_version || 'Cargando...'}</span>
          </div>
          <div className="flex justify-between items-center text-sm mt-1">
            <span className="text-gray-500">Plataforma:</span>
            <span className="text-gray-900">{systemInfo.platform || 'Cargando...'}</span>
          </div>
        </div>
      </div>
    </div>
  )
}


