/**
 * ChartContainer - Wrapper profesional para todos los charts
 * Proporciona: título, descripción, loading state, empty state, actions
 */

import React from 'react'
import { motion } from 'framer-motion'
import { Download, Maximize2, RefreshCw } from 'lucide-react'
import LoadingSpinner from '../LoadingSpinner'

interface ChartContainerProps {
  title: string
  description?: string
  children: React.ReactNode
  isLoading?: boolean
  isEmpty?: boolean
  emptyMessage?: string
  onRefresh?: () => void
  onExport?: () => void
  onExpand?: () => void
  actions?: React.ReactNode
  className?: string
  height?: number | string
}

const ChartContainer: React.FC<ChartContainerProps> = ({
  title,
  description,
  children,
  isLoading = false,
  isEmpty = false,
  emptyMessage = 'No hay datos disponibles',
  onRefresh,
  onExport,
  onExpand,
  actions,
  className = '',
  height = 400,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`bg-gray-800 rounded-xl border border-gray-700 overflow-hidden ${className}`}
    >
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white flex items-center">
              {title}
            </h3>
            {description && (
              <p className="text-sm text-gray-400 mt-1">{description}</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-2 ml-4">
            {actions}
            
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
                title="Actualizar"
              >
                <RefreshCw size={16} />
              </button>
            )}

            {onExport && (
              <button
                onClick={onExport}
                className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
                title="Exportar"
              >
                <Download size={16} />
              </button>
            )}

            {onExpand && (
              <button
                onClick={onExpand}
                className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
                title="Expandir"
              >
                <Maximize2 size={16} />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div
        className="relative"
        style={{ height: typeof height === 'number' ? `${height}px` : height }}
      >
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-800/50 backdrop-blur-sm">
            <LoadingSpinner message="Cargando datos..." />
          </div>
        ) : isEmpty ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500">
            <svg
              className="w-16 h-16 mb-4 opacity-50"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            <p className="text-sm font-medium">{emptyMessage}</p>
          </div>
        ) : (
          <div className="p-6 h-full">
            {children}
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default ChartContainer




