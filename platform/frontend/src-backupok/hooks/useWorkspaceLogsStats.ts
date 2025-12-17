/**
 * useWorkspaceLogsStats Hook
 * ===========================
 * 
 * Hook para obtener y formatear estadísticas de logs de un workspace.
 */

import { useQuery } from '@tanstack/react-query'
import { useWorkspace } from '../contexts/WorkspaceContext'
import { workspacesAPI } from '../lib/api/workspaces/workspaces'

export const useWorkspaceLogsStats = () => {
  const { currentWorkspace } = useWorkspace()

  const { data: stats, isLoading } = useQuery({
    queryKey: ['workspace-logs-stats', currentWorkspace?.id],
    queryFn: async () => {
      if (!currentWorkspace?.id) return null
      return await workspacesAPI.getWorkspaceLogsStats(currentWorkspace.id)
    },
    enabled: !!currentWorkspace?.id,
    staleTime: 2 * 60 * 1000, // 2 minutos
    refetchInterval: 30 * 1000 // Actualizar cada 30 segundos
  })

  // Formatear estadísticas para mostrar
  const formattedStats = stats ? {
    totalLogs: stats.total_logs || 0,
    sizeMB: stats.size_mb || 0,
    dateRange: stats.date_range || null,
    bySource: stats.by_source || {},
    byLevel: stats.by_level || {},
    // Formatear rango de fechas (con validación)
    dateRangeText: stats.date_range?.first && stats.date_range?.last
      ? `${new Date(stats.date_range.first).toLocaleDateString('es-ES')} - ${new Date(stats.date_range.last).toLocaleDateString('es-ES')}`
      : 'Sin logs',
    // Calcular días desde el primer log
    daysSinceFirst: stats.date_range?.first
      ? Math.floor((Date.now() - new Date(stats.date_range.first).getTime()) / (1000 * 60 * 60 * 24))
      : 0
  } : null

  return {
    stats: formattedStats,
    isLoading
  }
}


