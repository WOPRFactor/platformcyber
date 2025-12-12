/**
 * Process Graph Tabs Component
 * =============================
 * 
 * Componente para las pestañas de navegación del ProcessGraphConsole.
 */

import React from 'react'
import { Activity, BarChart3, Shield, Search } from 'lucide-react'
import { cn } from '../../../lib/utils'

interface Tab {
  id: 'overview' | 'progress' | 'vulnerabilities' | 'discovery'
  label: string
  icon: React.ComponentType<{ size?: number }>
}

interface ProcessGraphTabsProps {
  activeTab: 'overview' | 'progress' | 'vulnerabilities' | 'discovery'
  setActiveTab: (tab: 'overview' | 'progress' | 'vulnerabilities' | 'discovery') => void
}

const tabs: Tab[] = [
  { id: 'overview', label: 'Vista General', icon: Activity },
  { id: 'progress', label: 'Progreso', icon: BarChart3 },
  { id: 'vulnerabilities', label: 'Vulnerabilidades', icon: Shield },
  { id: 'discovery', label: 'Descubrimientos', icon: Search },
]

const ProcessGraphTabs: React.FC<ProcessGraphTabsProps> = ({ activeTab, setActiveTab }) => {
  return (
    <div className="flex border-b border-green-700">
      {tabs.map((tab) => {
        const Icon = tab.icon
        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'text-green-400 border-b-2 border-green-400 bg-green-500/10'
                : 'text-gray-400 hover:text-green-300 hover:bg-gray-800'
            )}
          >
            <Icon size={16} />
            {tab.label}
          </button>
        )
      })}
    </div>
  )
}

export default ProcessGraphTabs


