/**
 * ScanningProgressHeader Component
 * ==================================
 * 
 * Muestra la barra de progreso del escaneo activo.
 */

import React from 'react'
import { CheckCircle, XCircle, Loader2 } from 'lucide-react'

interface ScanningProgressHeaderProps {
  scanProgress: {
    progress: number
    status: string
    message: string
    target: string
    scan_type: string
  } | null
}

const ScanningProgressHeader: React.FC<ScanningProgressHeaderProps> = ({ scanProgress }) => {
  if (!scanProgress) return null

  return (
    <div className="bg-gradient-to-r from-blue-900 to-purple-900 border border-blue-500 rounded-xl p-6 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {scanProgress.status === 'running' && <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />}
          {scanProgress.status === 'completed' && <CheckCircle className="w-6 h-6 text-gray-900" />}
          {scanProgress.status === 'error' && <XCircle className="w-6 h-6 text-red-400" />}
          <div>
            <h3 className="text-lg font-bold text-white">
              Escaneo en Progreso: {scanProgress.target}
            </h3>
            <p className="text-blue-300">
              Tipo: <span className="font-semibold text-blue-200">{scanProgress.scan_type}</span>
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-white">{scanProgress.progress}%</div>
          <div className={`text-sm font-medium ${
            scanProgress.status === 'running' ? 'text-blue-300' :
            scanProgress.status === 'completed' ? 'text-gray-700' :
            'text-red-300'
          }`}>
            {scanProgress.status === 'running' ? 'Ejecutando' :
             scanProgress.status === 'completed' ? 'Completado' :
             'Error'}
          </div>
        </div>
      </div>

      {/* Barra de progreso */}
      <div className="w-full bg-gray-700 rounded-full h-4 mb-3 overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ${
            scanProgress.status === 'running' ? 'bg-blue-500' :
            scanProgress.status === 'completed' ? 'bg-red-600' :
            'bg-red-500'
          }`}
          style={{ width: `${scanProgress.progress}%` }}
        />
      </div>
      <p className="text-blue-200 text-sm">{scanProgress.message}</p>
    </div>
  )
}

export default ScanningProgressHeader

