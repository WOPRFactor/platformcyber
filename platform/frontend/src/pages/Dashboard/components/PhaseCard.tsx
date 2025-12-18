import React from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle, Clock, Play, AlertCircle } from 'lucide-react'
import { motion } from 'framer-motion'

interface PhaseCardProps {
  phase: {
    id: string
    name: string
    route: string
    completed: number
    total: number
    totalExecutions?: number
    icon: React.ComponentType<{ className?: string }>
    color: string
    bgColor: string
  }
}

export const PhaseCard: React.FC<PhaseCardProps> = ({ phase }) => {
  const navigate = useNavigate()
  const progress = phase.total > 0 ? (phase.completed / phase.total) * 100 : 0
  const percentage = Math.round(progress)

  // Determinar estado de la fase
  let status: 'pending' | 'in_progress' | 'completed' = 'pending'
  let statusIcon = Clock
  let statusText = 'Pendiente'
  let statusColor = 'text-gray-500'

  if (phase.completed >= phase.total && phase.total > 0) {
    status = 'completed'
    statusIcon = CheckCircle
    statusText = 'Completada'
    statusColor = 'text-green-400'
  } else if (phase.completed > 0) {
    status = 'in_progress'
    statusIcon = Play
    statusText = 'En progreso'
    statusColor = 'text-blue-400'
  }

  const StatusIcon = statusIcon

  // Determinar si la card está pendiente (más sutil)
  const isPending = phase.completed === 0

  // Mapear colores de fase a esquemas de color
  const getColorScheme = () => {
    if (isPending) {
      return {
        bg: 'bg-gray-500/10',
        icon: 'text-gray-500',
        border: 'border-gray-500/30',
        progress: 'bg-gray-300',
      }
    }

    // Mapear colores según la fase
    const colorMap: Record<string, any> = {
      'text-blue-400': {
        bg: 'bg-blue-500/10',
        icon: 'text-blue-500',
        border: 'border-blue-500/30',
        progress: 'bg-blue-400',
      },
      'text-cyan-400': {
        bg: 'bg-cyan-500/10',
        icon: 'text-cyan-500',
        border: 'border-cyan-500/30',
        progress: 'bg-cyan-400',
      },
      'text-red-400': {
        bg: 'bg-red-500/10',
        icon: 'text-red-500',
        border: 'border-red-500/30',
        progress: 'bg-red-400',
      },
      'text-orange-400': {
        bg: 'bg-orange-500/10',
        icon: 'text-orange-500',
        border: 'border-orange-500/30',
        progress: 'bg-orange-400',
      },
      'text-purple-400': {
        bg: 'bg-purple-500/10',
        icon: 'text-purple-500',
        border: 'border-purple-500/30',
        progress: 'bg-purple-400',
      },
      'text-green-400': {
        bg: 'bg-green-500/10',
        icon: 'text-green-500',
        border: 'border-green-500/30',
        progress: 'bg-green-400',
      },
    }

    return colorMap[phase.color] || colorMap['text-blue-400']
  }

  const scheme = getColorScheme()

  // Determinar color de la barra de progreso
  const getProgressColor = () => {
    if (percentage >= 100) return 'bg-green-400'
    if (percentage >= 50) return scheme.progress
    if (percentage > 0) return 'bg-yellow-400'
    return 'bg-gray-300'
  }

  // Limitar el ancho de la barra visualmente al 100%, pero mostrar el porcentaje real
  const visualProgressWidth = Math.min(percentage, 100)

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      onClick={() => navigate(phase.route)}
      className={`
        relative overflow-hidden
        bg-gray-100 border border-gray-300 rounded-xl 
        p-6
        shadow-sm
        hover:shadow-md hover:border-gray-400
        transition-all duration-300
        cursor-pointer
        ${isPending ? 'opacity-75' : ''}
      `}
    >
      {/* Background decoration */}
      <div className={`absolute top-0 right-0 ${scheme.bg} w-32 h-32 rounded-full -mr-16 -mt-16 opacity-30`} />
      
      {/* Content */}
      <div className="relative z-10">
        {/* Header: Icon */}
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 ${scheme.bg} rounded-lg ${scheme.border} border`}>
            <phase.icon className={`w-6 h-6 ${scheme.icon}`} />
          </div>

          {/* Status badge */}
          <div className="flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-semibold bg-gray-50">
            <StatusIcon className={`w-4 h-4 ${statusColor}`} />
            <span className={statusColor}>{statusText}</span>
          </div>
        </div>

        {/* Value */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="text-3xl font-bold text-gray-900 mb-1">
            {phase.completed}/{phase.total}
          </div>
          
          <div className="text-sm text-gray-500 font-medium mb-1">
            {phase.name}
          </div>

          {/* Total de ejecuciones (híbrido) */}
          {phase.totalExecutions !== undefined && phase.totalExecutions > 0 && (
            <div className="text-xs text-gray-400 mb-3">
              {phase.totalExecutions} ejecución{phase.totalExecutions !== 1 ? 'es' : ''}
            </div>
          )}
        </motion.div>

        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden mb-2">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${visualProgressWidth}%` }}
            transition={{ duration: 1, delay: 0.3 }}
            className={`h-1.5 rounded-full ${getProgressColor()}`}
          />
        </div>

        {/* Percentage */}
        <div className="text-xs text-gray-500">
          {percentage}% completado{percentage > 100 ? ' ✓' : ''}
        </div>

        {/* Bottom pulse indicator */}
        <motion.div
          className={`absolute bottom-0 left-0 right-0 h-1 ${scheme.bg}`}
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 1, delay: 0.5 }}
        />
      </div>
    </motion.div>
  )
}
