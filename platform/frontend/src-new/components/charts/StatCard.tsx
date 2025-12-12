/**
 * StatCard - Tarjeta de estadística animada con count-up effect
 * Muestra métricas clave con tendencias y animaciones profesionales
 */

import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus, LucideIcon } from 'lucide-react'

interface StatCardProps {
  title: string
  value: number
  icon: LucideIcon
  trend?: {
    value: number // porcentaje de cambio
    isPositive?: boolean // si es positivo o negativo (para contexto)
  }
  format?: 'number' | 'percent' | 'currency'
  color?: 'green' | 'blue' | 'amber' | 'red' | 'purple' | 'gray'
  suffix?: string
  prefix?: string
  className?: string
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon: Icon,
  trend,
  format = 'number',
  color = 'green',
  suffix = '',
  prefix = '',
  className = '',
}) => {
  const [displayValue, setDisplayValue] = useState(0)

  // Count-up animation
  useEffect(() => {
    const duration = 1000 // 1 segundo
    const steps = 60
    const increment = value / steps
    const stepDuration = duration / steps

    let current = 0
    const timer = setInterval(() => {
      current += increment
      if (current >= value) {
        setDisplayValue(value)
        clearInterval(timer)
      } else {
        setDisplayValue(Math.floor(current))
      }
    }, stepDuration)

    return () => clearInterval(timer)
  }, [value])

  // Color schemes
  const colorSchemes = {
    green: {
      bg: 'bg-green-500/10',
      text: 'text-green-400',
      icon: 'text-green-500',
      border: 'border-green-500/30',
      glow: 'shadow-green-500/20',
    },
    blue: {
      bg: 'bg-blue-500/10',
      text: 'text-blue-400',
      icon: 'text-blue-500',
      border: 'border-blue-500/30',
      glow: 'shadow-blue-500/20',
    },
    amber: {
      bg: 'bg-amber-500/10',
      text: 'text-amber-400',
      icon: 'text-amber-500',
      border: 'border-amber-500/30',
      glow: 'shadow-amber-500/20',
    },
    red: {
      bg: 'bg-red-500/10',
      text: 'text-red-400',
      icon: 'text-red-500',
      border: 'border-red-500/30',
      glow: 'shadow-red-500/20',
    },
    purple: {
      bg: 'bg-purple-500/10',
      text: 'text-purple-400',
      icon: 'text-purple-500',
      border: 'border-purple-500/30',
      glow: 'shadow-purple-500/20',
    },
    gray: {
      bg: 'bg-gray-500/10',
      text: 'text-gray-400',
      icon: 'text-gray-500',
      border: 'border-gray-500/30',
      glow: 'shadow-gray-500/20',
    },
  }

  const scheme = colorSchemes[color]

  // Format value
  const formatValue = (val: number): string => {
    if (format === 'percent') return `${val.toFixed(1)}%`
    if (format === 'currency') return `$${val.toLocaleString()}`
    if (val >= 1000000) return `${(val / 1000000).toFixed(1)}M`
    if (val >= 1000) return `${(val / 1000).toFixed(1)}K`
    return val.toLocaleString()
  }

  // Trend icon
  const getTrendIcon = () => {
    if (!trend) return null
    if (trend.value === 0) return <Minus className="w-4 h-4" />
    if (trend.value > 0) return <TrendingUp className="w-4 h-4" />
    return <TrendingDown className="w-4 h-4" />
  }

  // Trend color
  const getTrendColor = () => {
    if (!trend) return ''
    if (trend.value === 0) return 'text-gray-400'
    
    // En seguridad, menos vulnerabilidades es positivo
    if (trend.isPositive === false) {
      return trend.value > 0 ? 'text-red-400' : 'text-green-400'
    }
    
    // Por defecto, más es positivo
    return trend.value > 0 ? 'text-green-400' : 'text-red-400'
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className={`
        relative overflow-hidden
        bg-gray-800 rounded-xl 
        border ${scheme.border}
        p-6
        shadow-lg ${scheme.glow}
        hover:shadow-xl hover:border-opacity-100
        transition-all duration-300
        ${className}
      `}
    >
      {/* Background decoration */}
      <div className={`absolute top-0 right-0 ${scheme.bg} w-32 h-32 rounded-full -mr-16 -mt-16 opacity-30`} />
      
      {/* Content */}
      <div className="relative z-10">
        {/* Header: Icon + Title */}
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 ${scheme.bg} rounded-lg ${scheme.border} border`}>
            <Icon className={`w-6 h-6 ${scheme.icon}`} />
          </div>

          {/* Trend badge */}
          {trend && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className={`
                flex items-center space-x-1 
                px-2 py-1 
                rounded-full 
                text-xs font-semibold
                ${getTrendColor()}
                bg-gray-900/50
              `}
            >
              {getTrendIcon()}
              <span>{Math.abs(trend.value).toFixed(1)}%</span>
            </motion.div>
          )}
        </div>

        {/* Value */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className={`text-3xl font-bold ${scheme.text} mb-1`}>
            {prefix}{formatValue(displayValue)}{suffix}
          </div>
          
          <div className="text-sm text-gray-400 font-medium">
            {title}
          </div>
        </motion.div>

        {/* Bottom pulse indicator (optional) */}
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

export default StatCard
