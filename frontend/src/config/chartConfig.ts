/**
 * Chart Configuration - Sistema centralizado de colores y estilos para visualizaciones
 * Diseñado para dark theme con paleta cybersecurity
 */

// ═══════════════════════════════════════════════════════════════════════
// PALETA DE COLORES
// ═══════════════════════════════════════════════════════════════════════

export const CHART_COLORS = {
  // Severidades (estándar en cybersecurity)
  severity: {
    critical: '#DC2626',   // Red-600 - Crítico
    high: '#F59E0B',       // Amber-500 - Alto
    medium: '#FBBF24',     // Yellow-400 - Medio
    low: '#3B82F6',        // Blue-500 - Bajo
    info: '#6B7280',       // Gray-500 - Informativo
  },

  // Estados de procesos
  status: {
    success: '#10B981',    // Green-500 - Éxito
    warning: '#F59E0B',    // Amber-500 - Advertencia
    error: '#EF4444',      // Red-500 - Error
    running: '#8B5CF6',    // Purple-500 - En ejecución
    pending: '#6B7280',    // Gray-500 - Pendiente
    completed: '#10B981',  // Green-500 - Completado
    failed: '#DC2626',     // Red-600 - Fallido
  },

  // Gradientes para áreas y líneas
  gradients: {
    primary: ['#10B981', '#059669'],      // Green gradient
    secondary: ['#3B82F6', '#2563EB'],    // Blue gradient
    danger: ['#EF4444', '#DC2626'],       // Red gradient
    warning: ['#F59E0B', '#D97706'],      // Amber gradient
    success: ['#10B981', '#059669'],      // Green gradient
    purple: ['#8B5CF6', '#7C3AED'],       // Purple gradient
  },

  // Colores de fondo y UI
  background: {
    card: '#1F2937',       // Gray-800
    hover: '#374151',      // Gray-700
    border: '#4B5563',     // Gray-600
    grid: '#374151',       // Gray-700 (para grids de charts)
  },

  // Texto
  text: {
    primary: '#F9FAFB',    // Gray-50
    secondary: '#D1D5DB',  // Gray-300
    muted: '#9CA3AF',      // Gray-400
  },

  // Paleta extendida para múltiples series
  series: [
    '#10B981', // Green
    '#3B82F6', // Blue
    '#F59E0B', // Amber
    '#8B5CF6', // Purple
    '#EC4899', // Pink
    '#14B8A6', // Teal
    '#F97316', // Orange
    '#6366F1', // Indigo
  ],
}

// ═══════════════════════════════════════════════════════════════════════
// CONFIGURACIÓN DE CHARTS
// ═══════════════════════════════════════════════════════════════════════

export const CHART_CONFIG = {
  // Configuración de tooltip global
  tooltip: {
    contentStyle: {
      backgroundColor: '#1F2937',
      border: '1px solid #4B5563',
      borderRadius: '8px',
      padding: '12px',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
    },
    labelStyle: {
      color: '#F9FAFB',
      fontWeight: 600,
      marginBottom: '4px',
    },
    itemStyle: {
      color: '#D1D5DB',
    },
  },

  // Configuración de ejes
  axis: {
    stroke: '#4B5563',
    tick: {
      fill: '#9CA3AF',
      fontSize: 12,
    },
    label: {
      fill: '#D1D5DB',
      fontSize: 13,
      fontWeight: 500,
    },
  },

  // Configuración de grids
  grid: {
    stroke: '#374151',
    strokeDasharray: '3 3',
    opacity: 0.3,
  },

  // Configuración de leyenda
  legend: {
    wrapperStyle: {
      paddingTop: '20px',
    },
    iconType: 'circle' as const,
    iconSize: 10,
  },

  // Animaciones
  animation: {
    duration: 800,
    easing: 'ease-out' as const,
  },

  // Margins por defecto
  margins: {
    default: { top: 20, right: 30, left: 20, bottom: 20 },
    withLegend: { top: 20, right: 30, left: 20, bottom: 50 },
    compact: { top: 10, right: 20, left: 10, bottom: 10 },
  },
}

// ═══════════════════════════════════════════════════════════════════════
// MAPEO DE SEVERIDADES
// ═══════════════════════════════════════════════════════════════════════

export const SEVERITY_CONFIG = {
  critical: {
    color: CHART_COLORS.severity.critical,
    label: 'Crítico',
    icon: '🔴',
    order: 0,
  },
  high: {
    color: CHART_COLORS.severity.high,
    label: 'Alto',
    icon: '🟠',
    order: 1,
  },
  medium: {
    color: CHART_COLORS.severity.medium,
    label: 'Medio',
    icon: '🟡',
    order: 2,
  },
  low: {
    color: CHART_COLORS.severity.low,
    label: 'Bajo',
    icon: '🔵',
    order: 3,
  },
  info: {
    color: CHART_COLORS.severity.info,
    label: 'Info',
    icon: '⚪',
    order: 4,
  },
}

// ═══════════════════════════════════════════════════════════════════════
// UTILIDADES
// ═══════════════════════════════════════════════════════════════════════

/**
 * Obtiene el color para una severidad
 */
export const getSeverityColor = (severity: string): string => {
  const normalizedSeverity = severity.toLowerCase()
  return CHART_COLORS.severity[normalizedSeverity as keyof typeof CHART_COLORS.severity] 
    || CHART_COLORS.severity.info
}

/**
 * Obtiene el color para un estado
 */
export const getStatusColor = (status: string): string => {
  const normalizedStatus = status.toLowerCase()
  return CHART_COLORS.status[normalizedStatus as keyof typeof CHART_COLORS.status] 
    || CHART_COLORS.status.pending
}

/**
 * Formatea números grandes
 */
export const formatNumber = (num: number): string => {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

/**
 * Formatea porcentajes
 */
export const formatPercent = (value: number): string => {
  return `${value.toFixed(1)}%`
}

/**
 * Calcula porcentaje
 */
export const calculatePercent = (value: number, total: number): number => {
  if (total === 0) return 0
  return (value / total) * 100
}

/**
 * Genera gradiente para ResponsiveContainer
 */
export const generateGradientId = (name: string): string => {
  return `gradient-${name.toLowerCase().replace(/\s+/g, '-')}`
}

// ═══════════════════════════════════════════════════════════════════════
// TIPOS
// ═══════════════════════════════════════════════════════════════════════

export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low' | 'info'
export type StatusLevel = 'success' | 'warning' | 'error' | 'running' | 'pending' | 'completed' | 'failed'

export interface ChartDataPoint {
  name: string
  value: number
  color?: string
}

export interface TimeSeriesDataPoint {
  date: string
  value: number
  category?: string
}

export interface SeverityDataPoint {
  severity: SeverityLevel
  count: number
  percentage?: number
}

