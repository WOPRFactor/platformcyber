/**
 * WorkspaceLogsIndicator Component
 * =================================
 * 
 * Muestra indicador de logs para un workspace.
 * Formato: "🟢 Workspace Name [Activo] 2.4K logs" o "⚪ Workspace Old [Archivado] Sin logs"
 */

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { workspacesAPI } from '../lib/api/workspaces/workspaces'
import { Workspace } from '../lib/api/workspaces/types'

interface WorkspaceLogsIndicatorProps {
  workspace: Workspace
}

export const WorkspaceLogsIndicator: React.FC<WorkspaceLogsIndicatorProps> = ({ workspace }) => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['workspace-logs-stats', workspace.id],
    queryFn: () => workspacesAPI.getWorkspaceLogsStats(workspace.id),
    enabled: !!workspace.id,
    staleTime: 5 * 60 * 1000, // 5 minutos
    refetchOnWindowFocus: false
  })

  // Determinar estado y emoji
  const status = workspace.status || (workspace.is_active ? 'active' : 'archived')
  const statusEmoji = status === 'active' ? '🟢' : status === 'archived' ? '⚪' : '🟡'
  const statusText = status === 'active' ? 'Activo' : status === 'archived' ? 'Archivado' : 'Pausado'

  // Formatear número de logs
  const formatLogCount = (count: number) => {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K`
    }
    return count.toString()
  }

  // Determinar si mostrar warning por tamaño
  const showSizeWarning = stats && stats.size_mb > 10

  if (isLoading) {
    return (
      <div className="text-xs text-gray-500">
        {statusEmoji} {workspace.name} [{statusText}] Cargando...
      </div>
    )
  }

  if (!stats || stats.total_logs === 0) {
    return (
      <div className="text-xs text-gray-500">
        {statusEmoji} {workspace.name} [{statusText}] Sin logs
      </div>
    )
  }

  return (
    <div className="text-xs text-gray-600 flex items-center gap-2">
      <span>
        {statusEmoji} {workspace.name} [{statusText}] {formatLogCount(stats.total_logs)} logs
      </span>
      {showSizeWarning && (
        <span className="px-1.5 py-0.5 bg-red-500/20 text-red-400 rounded text-[10px] font-semibold">
          ⚠️ {stats.size_mb.toFixed(1)}MB
        </span>
      )}
    </div>
  )
}


