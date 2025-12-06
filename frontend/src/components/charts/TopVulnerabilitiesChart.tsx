/**
 * TopVulnerabilitiesChart - Top 10 vulnerabilidades más comunes
 * Horizontal bar chart con colores por severidad
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
  Cell,
} from 'recharts'
import { motion } from 'framer-motion'
import { CHART_COLORS, CHART_CONFIG, getSeverityColor } from '../../config/chartConfig'
import ChartContainer from './ChartContainer'

interface VulnerabilityData {
  name: string
  count: number
  severity: 'critical' | 'high' | 'medium' | 'low'
  cve?: string
  affected_hosts?: number
}

interface TopVulnerabilitiesChartProps {
  data: VulnerabilityData[]
  title?: string
  description?: string
  isLoading?: boolean
  onRefresh?: () => void
  maxItems?: number
  onVulnerabilityClick?: (vuln: VulnerabilityData) => void
}

const TopVulnerabilitiesChart: React.FC<TopVulnerabilitiesChartProps> = ({
  data,
  title = 'Top Vulnerabilidades',
  description = 'Vulnerabilidades más frecuentes encontradas',
  isLoading = false,
  onRefresh,
  maxItems = 10,
  onVulnerabilityClick,
}) => {
  // Ordenar por count y tomar top N
  const chartData = [...data]
    .sort((a, b) => b.count - a.count)
    .slice(0, maxItems)
    .map(item => ({
      ...item,
      // Truncar nombre largo
      displayName: item.name.length > 40 
        ? item.name.substring(0, 37) + '...' 
        : item.name,
    }))

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null

    const data = payload[0].payload as VulnerabilityData & { displayName: string }

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-gray-900 border border-gray-700 rounded-lg p-4 shadow-xl max-w-sm"
      >
        <div className="flex items-center space-x-2 mb-3">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: getSeverityColor(data.severity) }}
          />
          <span className="text-xs font-semibold text-gray-400 uppercase">
            {data.severity}
          </span>
        </div>

        <div className="text-white font-semibold mb-3 text-sm leading-tight">
          {data.name}
        </div>

        {data.cve && (
          <div className="text-xs text-blue-400 mb-2 font-mono">{data.cve}</div>
        )}

        <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-800">
          <div>
            <div className="text-gray-500 text-xs mb-1">Ocurrencias</div>
            <div className="text-white font-bold text-lg">{data.count}</div>
          </div>
          {data.affected_hosts && (
            <div>
              <div className="text-gray-500 text-xs mb-1">Hosts Afectados</div>
              <div className="text-white font-bold text-lg">{data.affected_hosts}</div>
            </div>
          )}
        </div>
      </motion.div>
    )
  }

  // Custom label para mostrar el count en la barra
  const CustomLabel = (props: any) => {
    const { x, y, width, value } = props
    return (
      <text
        x={x + width + 8}
        y={y + 14}
        fill={CHART_COLORS.text.secondary}
        fontSize={12}
        fontWeight={600}
      >
        {value}
      </text>
    )
  }

  const isEmpty = chartData.length === 0

  return (
    <ChartContainer
      title={title}
      description={description}
      isLoading={isLoading}
      isEmpty={isEmpty}
      emptyMessage="No hay vulnerabilidades para mostrar"
      onRefresh={onRefresh}
      height={Math.max(400, chartData.length * 50)}
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 20, right: 60, left: 20, bottom: 20 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke={CHART_COLORS.background.grid}
            opacity={0.3}
            horizontal={true}
            vertical={false}
          />

          <XAxis
            type="number"
            {...CHART_CONFIG.axis}
            tick={CHART_CONFIG.axis.tick}
          />

          <YAxis
            type="category"
            dataKey="displayName"
            {...CHART_CONFIG.axis}
            tick={CHART_CONFIG.axis.tick}
            width={200}
          />

          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }} />

          <Bar
            dataKey="count"
            radius={[0, 8, 8, 0]}
            label={<CustomLabel />}
            animationDuration={1000}
            animationBegin={0}
            cursor={onVulnerabilityClick ? 'pointer' : 'default'}
            onClick={(data) => onVulnerabilityClick?.(data)}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={getSeverityColor(entry.severity)}
                opacity={0.9}
                style={{
                  filter: 'drop-shadow(0px 2px 4px rgba(0, 0, 0, 0.3))',
                }}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Legend manual con badges */}
      <div className="flex flex-wrap gap-3 justify-center mt-4 px-6 pb-4">
        {['critical', 'high', 'medium', 'low'].map((severity) => {
          const count = chartData.filter(v => v.severity === severity).length
          if (count === 0) return null

          return (
            <div
              key={severity}
              className="flex items-center space-x-2 px-3 py-1.5 bg-gray-700/50 rounded-full"
            >
              <div
                className="w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: getSeverityColor(severity) }}
              />
              <span className="text-xs text-gray-300 capitalize">{severity}</span>
              <span className="text-xs text-white font-semibold">({count})</span>
            </div>
          )
        })}
      </div>
    </ChartContainer>
  )
}

export default TopVulnerabilitiesChart




