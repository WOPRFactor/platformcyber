import React from 'react'
import { useConsole } from '../contexts/ConsoleContext'
import { Terminal, Eye, EyeOff } from 'lucide-react'
import { cn } from '../lib/utils'

interface ConsoleStatusProps {
  className?: string
}

const ConsoleStatus: React.FC<ConsoleStatusProps> = ({ className }) => {
  const { isConsoleOpen, tasks } = useConsole()

  const runningTasksCount = tasks.filter(t => t.status === 'running').length
  const hasActivity = runningTasksCount > 0

  if (!hasActivity) {
    return null // No mostrar nada si no hay actividad
  }

  return (
    <div className={cn(
      "fixed top-4 right-4 z-40 flex items-center space-x-2 px-3 py-2 rounded-lg border transition-all duration-300",
      isConsoleOpen
        ? "bg-cyan-500/10 border-cyan-500/50 text-cyan-300"
        : "bg-orange-500/10 border-orange-500/50 text-orange-300 animate-pulse"
    )}>
      <Terminal className="w-4 h-4" />
      <span className="text-sm font-medium">
        {isConsoleOpen ? (
          <>
            <Eye className="w-4 h-4 inline mr-1" />
            Consola Activa
          </>
        ) : (
          <>
            <EyeOff className="w-4 h-4 inline mr-1" />
            Consola Oculta
          </>
        )}
      </span>
      <span className="text-xs bg-current/20 px-2 py-0.5 rounded-full">
        {runningTasksCount} tarea{runningTasksCount !== 1 ? 's' : ''}
      </span>
    </div>
  )
}

export default ConsoleStatus



