import React from 'react'
import { BarChart3 } from 'lucide-react'
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'

interface ScanActivityData {
  time: string
  scans: number
  vulnerabilities: number
}

interface ScanActivityChartProps {
  data: ScanActivityData[]
}

export const ScanActivityChart: React.FC<ScanActivityChartProps> = ({ data }) => {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-green-400 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2" />
          Actividad de Escaneos
        </h2>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-blue-400 rounded-full"></div>
          <span className="text-xs text-gray-400">Escaneos</span>
          <div className="w-3 h-3 bg-red-400 rounded-full ml-4"></div>
          <span className="text-xs text-gray-400">Vulnerabilidades</span>
        </div>
      </div>

      <div className="h-64">
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%" minWidth={200} minHeight={200}>
            <RechartsLineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis
                dataKey="time"
                stroke="#9CA3AF"
                fontSize={12}
              />
              <YAxis stroke="#9CA3AF" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }}
              />
              <Line
                type="monotone"
                dataKey="scans"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="vulnerabilities"
                stroke="#EF4444"
                strokeWidth={2}
                dot={{ fill: '#EF4444', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6 }}
              />
            </RechartsLineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <BarChart3 size={48} className="mx-auto mb-4 opacity-50" />
              <p>No hay datos de actividad disponibles</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}


