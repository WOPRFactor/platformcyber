/**
 * ChartContainer - Wrapper profesional para todos los charts
 * Diseño Enterprise con fondo claro
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
  emptyMessage = 'No data available',
  onRefresh,
  onExport,
  onExpand,
  actions,
  className = '',
  height = 400,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`bg-gray-100 rounded-xl border border-gray-300 shadow-sm overflow-hidden ${className}`}
    >
      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-base font-semibold text-gray-900">
              {title}
            </h3>
            {description && (
              <p className="text-sm text-gray-500 mt-0.5">{description}</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1 ml-4">
            {actions}
            
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="p-2 text-gray-500 hover:text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
                title="Refresh"
              >
                <RefreshCw size={16} />
              </button>
            )}

            {onExport && (
              <button
                onClick={onExport}
                className="p-2 text-gray-500 hover:text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
                title="Export"
              >
                <Download size={16} />
              </button>
            )}

            {onExpand && (
              <button
                onClick={onExpand}
                className="p-2 text-gray-500 hover:text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
                title="Expand"
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
          <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm">
            <LoadingSpinner message="Loading data..." />
          </div>
        ) : isEmpty ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500">
            <svg
              className="w-12 h-12 mb-3 opacity-50"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            <p className="text-sm">{emptyMessage}</p>
          </div>
        ) : (
          <div className="p-5 h-full">
            {children}
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default ChartContainer

