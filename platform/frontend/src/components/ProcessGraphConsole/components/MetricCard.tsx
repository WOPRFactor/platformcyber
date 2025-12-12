/**
 * Metric Card Component
 * =====================
 * 
 * Componente reutilizable para mostrar métricas en tarjetas.
 */

import React from 'react'
import { LucideIcon } from 'lucide-react'

interface MetricCardProps {
  label: string
  value: string | number
  icon: LucideIcon
  borderColor: string
  textColor: string
  iconColor: string
}

const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  icon: Icon,
  borderColor,
  textColor,
  iconColor
}) => {
  return (
    <div className={`bg-gray-800 p-4 rounded-lg border ${borderColor}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className={`text-2xl font-bold ${textColor}`}>
            {value}
          </p>
        </div>
        <Icon className={`w-8 h-8 ${iconColor}`} />
      </div>
    </div>
  )
}

export default MetricCard


