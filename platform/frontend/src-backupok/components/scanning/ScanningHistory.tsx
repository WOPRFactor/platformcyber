/**
 * ScanningHistory Component
 * =========================
 * 
 * Muestra el historial de sesiones de escaneo.
 */

import React from 'react'
import { ScanSession } from '../../types'
import LoadingSpinner from '../LoadingSpinner'
import { toast } from 'sonner'

interface ScanningHistoryProps {
  sessions: ScanSession[] | undefined
  sessionsLoading: boolean
  tasks: any[]
  killTask: (taskId: string) => void
}

const ScanningHistory: React.FC<ScanningHistoryProps> = ({
  sessions,
  sessionsLoading,
  tasks,
  killTask
}) => {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Historial de Escaneos</h2>
        <p className="text-gray-500">
          Sesiones de escaneo recientes y su estado
        </p>
      </div>
      {sessionsLoading ? (
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      ) : sessions && sessions.length > 0 ? (
        <div className="space-y-2">
          {sessions.slice(0, 10).map((session: ScanSession) => (
            <div key={session.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div>
                <div className="font-medium">{session.target}</div>
                <div className="text-sm text-gray-600">
                  {session.scan_type} - {new Date(session.start_time || '').toLocaleString()}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 text-xs rounded ${
                  session.status === 'completed' ? 'bg-green-100 text-green-800' :
                  session.status === 'running' ? 'bg-blue-100 text-blue-800' :
                  session.status === 'error' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {session.status}
                </span>
                {session.status === 'running' && (
                  <button
                    onClick={() => {
                      const runningTask = tasks.find(t =>
                        t.status === 'running' &&
                        t.module === 'scanning' &&
                        t.target === session.target
                      )
                      if (runningTask) {
                        killTask(runningTask.id)
                        toast.success(`Proceso terminado: ${session.target}`)
                      } else {
                        toast.warning('No se encontró el proceso activo correspondiente')
                      }
                    }}
                    className="px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                    title="Terminar proceso"
                  >
                    Kill
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500 text-center py-4">
          No hay sesiones de escaneo registradas
        </p>
      )}
    </div>
  )
}

export default ScanningHistory

