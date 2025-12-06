/**
 * Chart Wrapper Component
 * =======================
 * 
 * Componente wrapper para gráficos Chart.js con título y contenedor.
 */

import React from 'react'

interface ChartWrapperProps {
  title: string
  titleColor: string
  borderColor: string
  height?: string
  children: React.ReactNode
}

const ChartWrapper: React.FC<ChartWrapperProps> = ({
  title,
  titleColor,
  borderColor,
  height = 'h-64',
  children
}) => {
  return (
    <div className={`bg-gray-800 p-6 rounded-lg border ${borderColor}`}>
      <h3 className={`text-lg font-semibold ${titleColor} mb-4`}>{title}</h3>
      <div className={height}>
        {children}
      </div>
    </div>
  )
}

export default ChartWrapper


