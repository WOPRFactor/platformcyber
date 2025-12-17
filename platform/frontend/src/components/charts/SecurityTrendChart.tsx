/**
 * SecurityTrendChart - Tendencia de seguridad en el tiempo
 * Line/Area chart que muestra la evolución de vulnerabilidades
 */

import React from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { motion } from 'framer-motion'
import { format, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'
import { CHART_COLORS, CHART_CONFIG } from '../../config/chartConfig'
import ChartContainer from './ChartContainer'

interface TrendDataPoint {
  date: string // ISO string
  critical: number
  high: number
  medium: number
  low: number
  total: number
}

interface SecurityTrendChartProps {
  data: TrendDataPoint[]
  title?: string
  description?: string
  isLoading?: boolean
  onRefresh?: () => void
  timeRange?: '7d' | '30d' | '90d' | 'all'
  showTotal?: boolean
}

const SecurityTrendChart: React.FC<SecurityTrendChartProps> = ({
  data,
  title = 'Tendencia de Seguridad',
  description = 'Evolución de vulnerabilidades en el tiempo',
  isLoading = false,
  onRefresh,
  timeRange = '30d',
  showTotal = true,
}) => {
  // Validar que data sea un array
  const safeData = Array.isArray(data) ? data : []
  
  // Formatear datos para el chart
  const chartData = safeData.map(item => ({
    ...item,
    formattedDate: item.date ? format(parseISO(item.date), 'dd MMM', { locale: es }) : '',
  }))

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null

    const data = payload[0].payload
    const date = parseISO(data.date)

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-gray-50 border border-gray-200 rounded-xl p-4 shadow-xl"
      >
        <div className="text-white font-semibold mb-3 border-b border-gray-200 pb-2">
          {format(date, "d 'de' MMMM, yyyy", { locale: es })}
        </div>
        
        {showTotal && (
          <div className="flex justify-between items-center mb-2 pb-2 border-b border-gray-800">
            <span className="text-gray-500 text-sm">Total:</span>
            <span className="text-white font-bold text-lg">{data.total}</span>
          </div>
        )}

        <div className="space-y-2">
          {payload
            .filter((item: any) => item.dataKey !== 'total')
            .sort((a: any, b: any) => b.value - a.value)
            .map((item: any) => (
              <div key={item.dataKey} className="flex justify-between items-center">
                <div className="flex items-center space-x-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-gray-500 text-sm capitalize">{item.name}:</span>
                </div>
                <span className="text-white font-semibold ml-4">{item.value}</span>
              </div>
            ))}
        </div>
      </motion.div>
    )
  }

  // Calcular estadísticas para mostrar en la descripción
  const stats = React.useMemo(() => {
    if (data.length < 2) return null

    const first = data[0].total
    const last = data[data.length - 1].total
    const change = last - first
    const changePercent = first === 0 ? 0 : (change / first) * 100

    return {
      change,
      changePercent,
      isImproving: change < 0, // Menos vulnerabilidades = mejora
    }
  }, [data])

  const isEmpty = data.length === 0

  return (
    <ChartContainer
      title={title}
      description={
        stats
          ? `${description} • ${stats.isImproving ? '📉' : '📈'} ${Math.abs(stats.changePercent).toFixed(1)}% ${stats.isImproving ? 'mejora' : 'incremento'}`
          : description
      }
      isLoading={isLoading}
      isEmpty={isEmpty}
      emptyMessage="No hay datos históricos disponibles"
      onRefresh={onRefresh}
      height={400}
    >
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={chartData}
          margin={CHART_CONFIG.margins.default}
        >
          {/* Gradientes */}
          <defs>
            <linearGradient id="criticalGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS.severity.critical} stopOpacity={0.8} />
              <stop offset="95%" stopColor={CHART_COLORS.severity.critical} stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="highGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS.severity.high} stopOpacity={0.8} />
              <stop offset="95%" stopColor={CHART_COLORS.severity.high} stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="mediumGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS.severity.medium} stopOpacity={0.8} />
              <stop offset="95%" stopColor={CHART_COLORS.severity.medium} stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="lowGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS.severity.low} stopOpacity={0.8} />
              <stop offset="95%" stopColor={CHART_COLORS.severity.low} stopOpacity={0.1} />
            </linearGradient>
          </defs>

          <CartesianGrid {...CHART_CONFIG.grid} />

          <XAxis
            dataKey="formattedDate"
            {...CHART_CONFIG.axis}
            tick={CHART_CONFIG.axis.tick}
          />

          <YAxis
            {...CHART_CONFIG.axis}
            tick={CHART_CONFIG.axis.tick}
            label={{
              value: 'Cantidad',
              angle: -90,
              position: 'insideLeft',
              ...CHART_CONFIG.axis.label,
            }}
          />

          <Tooltip content={<CustomTooltip />} />

          <Legend
            wrapperStyle={CHART_CONFIG.legend.wrapperStyle}
            iconType={CHART_CONFIG.legend.iconType}
            formatter={(value: string) => (
              <span style={{ color: CHART_COLORS.text.secondary, fontSize: '13px', fontWeight: 500 }}>
                {value.charAt(0).toUpperCase() + value.slice(1)}
              </span>
            )}
          />

          {/* Areas stacked */}
          <Area
            type="monotone"
            dataKey="critical"
            name="Crítico"
            stackId="1"
            stroke={CHART_COLORS.severity.critical}
            fill="url(#criticalGradient)"
            strokeWidth={2}
            animationDuration={1000}
          />

          <Area
            type="monotone"
            dataKey="high"
            name="Alto"
            stackId="1"
            stroke={CHART_COLORS.severity.high}
            fill="url(#highGradient)"
            strokeWidth={2}
            animationDuration={1200}
          />

          <Area
            type="monotone"
            dataKey="medium"
            name="Medio"
            stackId="1"
            stroke={CHART_COLORS.severity.medium}
            fill="url(#mediumGradient)"
            strokeWidth={2}
            animationDuration={1400}
          />

          <Area
            type="monotone"
            dataKey="low"
            name="Bajo"
            stackId="1"
            stroke={CHART_COLORS.severity.low}
            fill="url(#lowGradient)"
            strokeWidth={2}
            animationDuration={1600}
          />
        </AreaChart>
      </ResponsiveContainer>
    </ChartContainer>
  )
}

export default SecurityTrendChart




