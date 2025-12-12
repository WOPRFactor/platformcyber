/**
 * Progress Tab Component
 * ======================
 * 
 * Componente para la pestaña de progreso con gráficos y lista de tareas.
 */

import React from 'react'
import { Bar } from 'react-chartjs-2'
import { Task } from '../../../contexts/ConsoleContext'
import ChartWrapper from './ChartWrapper'
import { generateProgressData, chartOptions } from '../utils/chartData'

interface ProgressTabProps {
  tasks: Task[]
}

const ProgressTab: React.FC<ProgressTabProps> = ({ tasks }) => {
  const progressData = generateProgressData(tasks)

  return (
    <div className="space-y-6">
      <ChartWrapper
        title="Progreso de Tareas Activas"
        titleColor="text-gray-900"
        borderColor="border-gray-200"
        height="h-80"
      >
        <Bar data={progressData} options={chartOptions} />
      </ChartWrapper>

      {/* Lista de tareas con progreso */}
      <div className="bg-white p-6 rounded-xl border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Detalle de Tareas</h3>
        <div className="space-y-4">
          {tasks.map((task) => (
            <div key={task.id} className="flex items-center justify-between p-3 bg-gray-700 rounded">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-gray-900">{task.name}</span>
                  <span className="text-sm text-gray-500">{task.progress}%</span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div
                    className="bg-red-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${task.progress}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ProgressTab


