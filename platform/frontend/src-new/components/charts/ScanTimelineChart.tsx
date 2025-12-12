/**
 * ScanTimelineChart - Timeline de escaneos realizados
 * Bar chart que muestra la frecuencia de escaneos por día/semana
 */

import React from 'react'
import {
  BarChart,
  Bar,
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
import { CHART_COLORS, CHART_CONFIG, getStatusColor } from '../../config/chartConfig'
import ChartContainer from './ChartContainer'

interface ScanData {
  date: string // ISO string
  completed: number
  failed: number
  running: number
  total: number
}

interface ScanTimelineChartProps {
  data: ScanData[]
  title?: string
  description?: string
  isLoading?: boolean
  onRefresh?: () => void
  timeRange?: '7d' | '30d' | '90d'
}

const ScanTimelineChart: React.FC<ScanTimelineChartProps> = ({
  data,
  title = 'Actividad de Escaneos',
  description = 'Historial de escaneos realizados',
  isLoading = false,
  onRefresh,
  timeRange = '30d',
}) => {
  // Formatear datos
  const chartData = data.map(item => ({
    ...item,
    completed: item.completed || 0,
    failed: item.failed || 0,
    running: item.running || 0,
    total: item.total || 0,
    formattedDate: item.date ? format(parseISO(item.date), 'dd MMM', { locale: es }) : '',
    fullDate: item.date ? parseISO(item.date) : new Date(),
  }))

  // Calcular estadísticas
  const stats = React.useMemo(() => {
    const totalScans = data.reduce((sum, item) => sum + (item.total || 0), 0)
    const totalCompleted = data.reduce((sum, item) => sum + (item.completed || 0), 0)
    const totalFailed = data.reduce((sum, item) => sum + (item.failed || 0), 0)
    const successRate = totalScans > 0 ? (totalCompleted / totalScans) * 100 : 0

    return { 
      totalScans: totalScans || 0, 
      totalCompleted: totalCompleted || 0, 
      totalFailed: totalFailed || 0, 
      successRate: isNaN(successRate) ? 0 : successRate 
    }
  }, [data])

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null

    const data = payload[0].payload

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-gray-50 border border-gray-200 rounded-xl p-4 shadow-xl"
      >
        <div className="text-white font-semibold mb-3 border-b border-gray-200 pb-2">
          {format(data.fullDate, "d 'de' MMMM", { locale: es })}
        </div>

        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-600" />
              <span className="text-gray-500 text-sm">Completados:</span>
            </div>
            <span className="text-white font-bold ml-4">{data.completed}</span>
          </div>

          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-gray-500 text-sm">Fallidos:</span>
            </div>
            <span className="text-white font-bold ml-4">{data.failed}</span>
          </div>

          {data.running > 0 && (
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-purple-500" />
                <span className="text-gray-500 text-sm">En ejecución:</span>
              </div>
              <span className="text-white font-bold ml-4">{data.running}</span>
            </div>
          )}

          <div className="flex justify-between items-center pt-2 mt-2 border-t border-gray-800">
            <span className="text-gray-500 text-sm font-semibold">Total:</span>
            <span className="text-white font-bold text-lg ml-4">{data.total}</span>
          </div>
        </div>
      </motion.div>
    )
  }

  const isEmpty = data.length === 0

  return (
    <ChartContainer
      title={title}
      description={`${description} • ${stats.totalScans} scans • ${stats.successRate.toFixed(1)}% éxito`}
      isLoading={isLoading}
      isEmpty={isEmpty}
      emptyMessage="No hay escaneos registrados"
      onRefresh={onRefresh}
      height={350}
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={CHART_CONFIG.margins.withLegend}
        >
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

          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }} />

          <Legend
            wrapperStyle={CHART_CONFIG.legend.wrapperStyle}
            iconType={CHART_CONFIG.legend.iconType}
            formatter={(value: string) => {
              const labels: Record<string, string> = {
                completed: 'Completados',
                failed: 'Fallidos',
                running: 'En ejecución',
              }
              return (
                <span style={{ color: CHART_COLORS.text.secondary, fontSize: '13px', fontWeight: 500 }}>
                  {labels[value] || value}
                </span>
              )
            }}
          />

          {/* Bars stacked */}
          <Bar
            dataKey="completed"
            name="completed"
            stackId="scans"
            fill={CHART_COLORS.status.completed}
            radius={[0, 0, 0, 0]}
            animationDuration={800}
          />

          <Bar
            dataKey="failed"
            name="failed"
            stackId="scans"
            fill={CHART_COLORS.status.failed}
            radius={[0, 0, 0, 0]}
            animationDuration={1000}
          />

          <Bar
            dataKey="running"
            name="running"
            stackId="scans"
            fill={CHART_COLORS.status.running}
            radius={[8, 8, 0, 0]}
            animationDuration={1200}
          />
        </BarChart>
      </ResponsiveContainer>

      {/* Quick stats badges */}
      <div className="flex flex-wrap gap-3 justify-center mt-2 px-6 pb-4">
        <div className="flex items-center space-x-2 px-3 py-1.5 bg-red-600/10 border border-gray-200/30 rounded-xl">
          <span className="text-xs text-gray-500">Completados:</span>
          <span className="text-sm text-gray-900 font-bold">{stats.totalCompleted || 0}</span>
        </div>
        <div className="flex items-center space-x-2 px-3 py-1.5 bg-red-500/10 border border-red-500/30 rounded-xl">
          <span className="text-xs text-gray-500">Fallidos:</span>
          <span className="text-sm text-red-400 font-bold">{stats.totalFailed || 0}</span>
        </div>
        <div className="flex items-center space-x-2 px-3 py-1.5 bg-blue-500/10 border border-blue-500/30 rounded-xl">
          <span className="text-xs text-gray-500">Tasa de éxito:</span>
          <span className="text-sm text-blue-400 font-bold">{isNaN(stats.successRate) ? '0.0' : stats.successRate.toFixed(1)}%</span>
        </div>
      </div>
    </ChartContainer>
  )
}

export default ScanTimelineChart




