import React from 'react'
import { Clock } from 'lucide-react'
import LoadingSpinner from '../../../components/LoadingSpinner'

interface ScanSession {
  id: number
  target: string
  status: string
  scan_type?: string
  ports_found?: number
  vulnerabilities?: number
  start_time?: string
  duration?: number
}

interface RecentActivityProps {
  sessions: ScanSession[] | undefined
  isLoading: boolean
}

export const RecentActivity: React.FC<RecentActivityProps> = ({ sessions, isLoading }) => {
  if (isLoading) {
    return (
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Clock className="w-5 h-5 mr-2" />
          Actividad Reciente
        </h2>
        <LoadingSpinner message="Cargando actividad..." />
      </div>
    )
  }

  if (!sessions || sessions.length === 0) {
    return (
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Clock className="w-5 h-5 mr-2" />
          Actividad Reciente
        </h2>
        <div className="text-center py-12 text-gray-500">
          <Clock size={48} className="mx-auto mb-4 opacity-50" />
          <p className="text-lg font-medium mb-2">No hay actividad reciente</p>
          <p className="text-sm">Las sesiones de escaneo aparecerán aquí</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Clock className="w-5 h-5 mr-2" />
        Actividad Reciente
      </h2>

      <div className="space-y-4">
        {sessions.slice(0, 5).map((session) => (
          <div key={session.id} className="flex items-start space-x-3 p-3 bg-white/30 rounded-xl hover:bg-white/50 transition-colors">
            <div className={`w-3 h-3 rounded-full mt-1.5 flex-shrink-0 ${
              session.status === 'running' ? 'bg-green-400 animate-pulse' :
              session.status === 'completed' ? 'bg-blue-400' :
              session.status === 'error' ? 'bg-red-400' : 'bg-gray-400'
            }`} />

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <p className="text-white font-medium truncate">{session.target}</p>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  session.status === 'running' ? 'bg-red-600/20 text-gray-900' :
                  session.status === 'completed' ? 'bg-blue-500/20 text-blue-400' :
                  session.status === 'error' ? 'bg-red-500/20 text-red-400' :
                  'bg-gray-500/20 text-gray-500'
                }`}>
                  {session.status === 'running' ? 'Activo' :
                   session.status === 'completed' ? 'Completado' :
                   session.status === 'error' ? 'Error' : 'Pendiente'}
                </span>
              </div>

              <div className="flex items-center space-x-4 text-xs text-gray-500 mb-2">
                <span>{session.scan_type || 'Escaneo'}</span>
                <span>•</span>
                <span>{session.ports_found || 0} puertos</span>
                <span>•</span>
                <span className={session.vulnerabilities && session.vulnerabilities > 0 ? 'text-red-400' : 'text-gray-900'}>
                  {session.vulnerabilities || 0} vuln
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  {session.start_time ? new Date(session.start_time).toLocaleString() : 'N/A'}
                </span>
                {session.duration && (
                  <span className="text-xs text-gray-500">
                    {Math.round(session.duration)}min
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}

        {sessions.length > 5 && (
          <div className="text-center pt-2 border-t border-gray-200">
            <button className="text-gray-900 hover:text-gray-700 text-sm font-medium transition-colors">
              Ver todas las sesiones ({sessions.length})
            </button>
          </div>
        )}
      </div>
    </div>
  )
}


