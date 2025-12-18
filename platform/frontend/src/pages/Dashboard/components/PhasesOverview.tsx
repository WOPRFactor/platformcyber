import React from 'react'
import { Search, Activity, Shield, Zap, Target, FileText } from 'lucide-react'
import { PhaseCard } from './PhaseCard'

interface Phase {
  id: string
  name: string
  route: string
  completed: number
  total: number
  totalExecutions?: number
  icon: React.ComponentType<{ className?: string }>
  color: string
  bgColor: string
}

interface PhasesOverviewProps {
  phases: Phase[]
}

export const PhasesOverview: React.FC<PhasesOverviewProps> = ({ phases }) => {
  if (!phases || phases.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Fases del Pentesting
          </h2>
          <p className="text-sm text-gray-500">
            No hay fases disponibles
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Fases del Pentesting
        </h2>
        <p className="text-sm text-gray-500">
          Progreso de cada fase del proceso de pentesting
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {phases.map((phase) => (
          <PhaseCard key={phase.id} phase={phase} />
        ))}
      </div>
    </div>
  )
}
