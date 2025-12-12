import React from 'react'
import { RefreshCw, Shield } from 'lucide-react'

interface DashboardHeaderProps {
  user: { username: string; role: string } | null
  healthStatus: string | undefined
  selectedTimeRange: '1h' | '24h' | '7d' | '30d'
  onTimeRangeChange: (range: '1h' | '24h' | '7d' | '30d') => void
  onRefresh: () => void
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  user,
  healthStatus,
  selectedTimeRange,
  onTimeRangeChange,
  onRefresh
}) => {
  return (
    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900 text-gray-900">
          Dashboard Ejecutivo
        </h1>
        <p className="text-gray-500 mt-2">
          Bienvenido de vuelta, {user?.username}
        </p>
        <div className="flex items-center space-x-4 mt-3">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${healthStatus === 'healthy' ? 'bg-green-400' : 'bg-red-400'}`}></div>
            <span className="text-sm text-gray-500">
              Sistema {healthStatus === 'healthy' ? 'Operativo' : 'Con Problemas'}
            </span>
          </div>
          <div className="text-sm text-gray-500">
            Última actualización: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">Rango:</span>
          <select
            value={selectedTimeRange}
            onChange={(e) => onTimeRangeChange(e.target.value as any)}
            className="bg-white border border-gray-200 rounded px-3 py-1 text-sm text-white focus:outline-none focus:border-gray-200"
          >
            <option value="1h">Última hora</option>
            <option value="24h">Últimas 24h</option>
            <option value="7d">Últimos 7 días</option>
            <option value="30d">Últimos 30 días</option>
          </select>
        </div>

        <button
          onClick={onRefresh}
          className="flex items-center space-x-2 px-4 py-2 rounded-md text-gray-900 hover:bg-gray-700 transition-colors border border-gray-200/30"
          title="Actualizar todas las métricas"
        >
          <RefreshCw size={16} />
          <span className="hidden md:inline">Actualizar</span>
        </button>

        <div className="flex items-center space-x-2">
          <Shield className="w-5 h-5 text-gray-900" />
          <span className="text-sm bg-red-600/20 text-gray-900 px-3 py-1 rounded-full">
            {user?.role}
          </span>
        </div>
      </div>
    </div>
  )
}


