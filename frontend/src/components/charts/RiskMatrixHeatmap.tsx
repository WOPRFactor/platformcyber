/**
 * RiskMatrixHeatmap - Matriz de riesgo 2D (Probabilidad vs Impacto)
 * Heatmap interactivo que muestra vulnerabilidades en una matriz de riesgo
 * Muy útil para presentaciones ejecutivas y priorización
 */

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { CHART_COLORS, CHART_CONFIG } from '../../config/chartConfig'
import ChartContainer from './ChartContainer'

interface RiskDataPoint {
  id: string
  name: string
  probability: number // 0-100
  impact: number // 0-100
  severity: 'critical' | 'high' | 'medium' | 'low'
  count?: number
  affected_hosts?: number
  cve?: string
}

interface RiskMatrixHeatmapProps {
  data: RiskDataPoint[]
  title?: string
  description?: string
  isLoading?: boolean
  onRefresh?: () => void
  onRiskClick?: (risk: RiskDataPoint) => void
  gridSize?: number // Tamaño de la grilla (default: 10x10)
}

const RiskMatrixHeatmap: React.FC<RiskMatrixHeatmapProps> = ({
  data,
  title = 'Matriz de Riesgo',
  description = 'Distribución de vulnerabilidades por probabilidad e impacto',
  isLoading = false,
  onRefresh,
  onRiskClick,
  gridSize = 10,
}) => {
  const [hoveredCell, setHoveredCell] = useState<{ x: number; y: number } | null>(null)
  const [selectedRisk, setSelectedRisk] = useState<RiskDataPoint | null>(null)

  // Crear matriz de riesgo
  const matrix = React.useMemo(() => {
    const matrix: (RiskDataPoint[])[][] = Array(gridSize)
      .fill(null)
      .map(() => Array(gridSize).fill(null).map(() => []))

    data.forEach(risk => {
      const x = Math.floor((risk.probability / 100) * (gridSize - 1))
      const y = Math.floor((risk.impact / 100) * (gridSize - 1))
      const clampedX = Math.max(0, Math.min(gridSize - 1, x))
      const clampedY = Math.max(0, Math.min(gridSize - 1, y))
      matrix[clampedY][clampedX].push(risk)
    })

    return matrix
  }, [data, gridSize])

  // Calcular intensidad de color por celda
  const getCellIntensity = (cell: RiskDataPoint[]): number => {
    if (cell.length === 0) return 0
    const maxSeverity = cell.reduce((max, risk) => {
      const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 }
      return Math.max(max, severityOrder[risk.severity] || 0)
    }, 0)
    return maxSeverity / 4
  }

  // Obtener color de celda basado en intensidad y posición
  const getCellColor = (x: number, y: number, intensity: number): string => {
    if (intensity === 0) return '#1F2937' // Gray-800 (vacío)

    // Zonas de riesgo:
    // - Esquina superior derecha (alto impacto, alta probabilidad) = Rojo
    // - Centro = Amarillo/Naranja
    // - Esquina inferior izquierda (bajo impacto, baja probabilidad) = Verde

    const riskLevel = (x + y) / (gridSize * 2) // 0-1
    const baseIntensity = intensity * 0.7 + riskLevel * 0.3

    if (riskLevel > 0.7) {
      // Zona crítica (rojo)
      const red = Math.floor(220 + baseIntensity * 35)
      const green = Math.floor(20 + baseIntensity * 20)
      const blue = Math.floor(20 + baseIntensity * 20)
      return `rgb(${red}, ${green}, ${blue})`
    } else if (riskLevel > 0.4) {
      // Zona media (amarillo/naranja)
      const red = Math.floor(200 + baseIntensity * 55)
      const green = Math.floor(150 + baseIntensity * 50)
      const blue = Math.floor(20 + baseIntensity * 20)
      return `rgb(${red}, ${green}, ${blue})`
    } else {
      // Zona baja (verde)
      const red = Math.floor(20 + baseIntensity * 30)
      const green = Math.floor(150 + baseIntensity * 80)
      const blue = Math.floor(50 + baseIntensity * 30)
      return `rgb(${red}, ${green}, ${blue})`
    }
  }

  // Obtener riesgos en una celda
  const getCellRisks = (x: number, y: number): RiskDataPoint[] => {
    return matrix[y]?.[x] || []
  }

  const cellSize = 100 / gridSize

  const isEmpty = data.length === 0

  return (
    <ChartContainer
      title={title}
      description={description}
      isLoading={isLoading}
      isEmpty={isEmpty}
      emptyMessage="No hay datos de riesgo para mostrar"
      onRefresh={onRefresh}
      height={600}
    >
      <div className="relative w-full h-full">
        {/* Grid Container */}
        <div className="relative" style={{ width: '100%', height: '500px' }}>
          {/* Y Axis Label (Impacto) */}
          <div
            className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-8 -rotate-90 text-sm font-semibold text-gray-300 whitespace-nowrap"
            style={{ writingMode: 'vertical-rl' }}
          >
            Impacto
          </div>

          {/* X Axis Label (Probabilidad) */}
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-8 text-sm font-semibold text-gray-300">
            Probabilidad
          </div>

          {/* Heatmap Grid */}
          <div className="relative ml-8 mb-8" style={{ width: 'calc(100% - 2rem)', height: 'calc(100% - 2rem)' }}>
            {Array(gridSize)
              .fill(null)
              .map((_, rowIndex) => (
                <div key={rowIndex} className="flex" style={{ height: `${cellSize}%` }}>
                  {Array(gridSize)
                    .fill(null)
                    .map((_, colIndex) => {
                      const cell = getCellRisks(colIndex, rowIndex)
                      const intensity = getCellIntensity(cell)
                      const color = getCellColor(colIndex, rowIndex, intensity)
                      const isHovered =
                        hoveredCell?.x === colIndex && hoveredCell?.y === rowIndex
                      const count = cell.length

                      return (
                        <motion.div
                          key={`${rowIndex}-${colIndex}`}
                          className="border border-gray-700 relative cursor-pointer"
                          style={{
                            width: `${cellSize}%`,
                            height: '100%',
                            backgroundColor: color,
                            opacity: isHovered ? 1 : intensity > 0 ? 0.8 : 0.3,
                          }}
                          onMouseEnter={() => setHoveredCell({ x: colIndex, y: rowIndex })}
                          onMouseLeave={() => setHoveredCell(null)}
                          onClick={() => {
                            if (cell.length > 0) {
                              setSelectedRisk(cell[0])
                              onRiskClick?.(cell[0])
                            }
                          }}
                          whileHover={{ scale: 1.1, zIndex: 10 }}
                          transition={{ duration: 0.2 }}
                        >
                          {/* Count badge */}
                          {count > 0 && (
                            <motion.div
                              initial={{ scale: 0 }}
                              animate={{ scale: 1 }}
                              className="absolute top-1 right-1 bg-gray-900 text-white text-xs font-bold px-1.5 py-0.5 rounded"
                            >
                              {count}
                            </motion.div>
                          )}

                          {/* Tooltip on hover */}
                          {isHovered && count > 0 && (
                            <motion.div
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              className="absolute z-20 bg-gray-900 border border-gray-700 rounded-lg p-3 shadow-xl"
                              style={{
                                bottom: '100%',
                                left: '50%',
                                transform: 'translateX(-50%)',
                                marginBottom: '8px',
                                minWidth: '200px',
                              }}
                            >
                              <div className="text-white font-semibold mb-2 text-sm">
                                {count} {count === 1 ? 'Riesgo' : 'Riesgos'}
                              </div>
                              <div className="space-y-1">
                                {cell.slice(0, 3).map((risk) => (
                                  <div key={risk.id} className="text-xs text-gray-300">
                                    • {risk.name}
                                  </div>
                                ))}
                                {cell.length > 3 && (
                                  <div className="text-xs text-gray-500">
                                    +{cell.length - 3} más
                                  </div>
                                )}
                              </div>
                            </motion.div>
                          )}
                        </motion.div>
                      )
                    })}
                </div>
              ))}
          </div>

          {/* Zone Labels */}
          <div className="absolute top-2 right-2 text-xs text-gray-500 space-y-1">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded" />
              <span>Crítico</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-yellow-500 rounded" />
              <span>Medio</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded" />
              <span>Bajo</span>
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-4 flex items-center justify-center space-x-6 text-xs text-gray-400">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-gray-700 rounded" />
            <span>Sin riesgos</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500/50 rounded" />
            <span>1-2 riesgos</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-yellow-500/70 rounded" />
            <span>3-5 riesgos</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500/80 rounded" />
            <span>6+ riesgos</span>
          </div>
        </div>

        {/* Selected Risk Details */}
        {selectedRisk && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-gray-700/50 rounded-lg border border-gray-600"
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="text-white font-semibold">{selectedRisk.name}</h4>
              <button
                onClick={() => setSelectedRisk(null)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Probabilidad:</span>
                <span className="text-white font-semibold ml-2">
                  {selectedRisk.probability}%
                </span>
              </div>
              <div>
                <span className="text-gray-400">Impacto:</span>
                <span className="text-white font-semibold ml-2">
                  {selectedRisk.impact}%
                </span>
              </div>
              {selectedRisk.count && (
                <div>
                  <span className="text-gray-400">Ocurrencias:</span>
                  <span className="text-white font-semibold ml-2">
                    {selectedRisk.count}
                  </span>
                </div>
              )}
              {selectedRisk.affected_hosts && (
                <div>
                  <span className="text-gray-400">Hosts Afectados:</span>
                  <span className="text-white font-semibold ml-2">
                    {selectedRisk.affected_hosts}
                  </span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </ChartContainer>
  )
}

export default RiskMatrixHeatmap




