import React from 'react'
import LoadingSpinner from '../../../../components/LoadingSpinner'
import { IntegrationSession } from '../../../../types'

interface IntegrationHistoryProps {
  sessions: IntegrationSession[] | undefined
  isLoading: boolean
}

export const IntegrationHistory: React.FC<IntegrationHistoryProps> = ({
  sessions,
  isLoading
}) => {
  return (
    <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-green-400">Historial de Integraciones</h2>
        <p className="text-green-600">
          Sesiones de herramientas avanzadas ejecutadas
        </p>
      </div>
      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      ) : sessions && sessions.length > 0 ? (
        <div className="space-y-2">
          {sessions.slice(0, 10).map((session: IntegrationSession) => (
            <div key={session?.id || Math.random()} className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div>
                <div className="font-medium">{session?.target || 'Unknown'}</div>
                <div className="text-sm text-gray-600">
                  {session?.scan_type?.replace('_', ' ') || 'Unknown'} - {session?.created_at ? new Date(session.created_at).toLocaleString() : 'Unknown'}
                </div>
              </div>
              <span className={`px-2 py-1 text-xs rounded ${
                session?.status === 'completed' ? 'bg-green-100 text-green-800' :
                session?.status === 'running' ? 'bg-blue-100 text-blue-800' :
                session?.status === 'error' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {session?.status || 'unknown'}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500 text-center py-4">
          No hay sesiones de integraciones registradas
        </p>
      )}
    </div>
  )
}


