import React from 'react'
import LoadingSpinner from '../../../components/LoadingSpinner'

interface WhiteboxSession {
  id: string
  target: string
  scan_type: string
  status: string
  created_at: string
}

interface SessionsHistoryProps {
  sessions: WhiteboxSession[] | undefined
  isLoading: boolean
}

export const SessionsHistory: React.FC<SessionsHistoryProps> = ({ sessions, isLoading }) => {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <LoadingSpinner />
      </div>
    )
  }

  if (!sessions || sessions.length === 0) {
    return (
      <p className="text-gray-500 text-center py-4">
        No hay sesiones de análisis registradas
      </p>
    )
  }

  return (
    <div className="space-y-2">
      {sessions.slice(0, 10).map((session: WhiteboxSession) => (
        <div key={session.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
          <div>
            <div className="font-medium">{session.target}</div>
            <div className="text-sm text-gray-600">
              {session.scan_type} - {new Date(session.created_at).toLocaleString()}
            </div>
          </div>
          <span className={`px-2 py-1 text-xs rounded ${
            session.status === 'completed' ? 'bg-green-100 text-green-800' :
            session.status === 'running' ? 'bg-blue-100 text-blue-800' :
            session.status === 'error' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
          }`}>
            {session.status}
          </span>
        </div>
      ))}
    </div>
  )
}


