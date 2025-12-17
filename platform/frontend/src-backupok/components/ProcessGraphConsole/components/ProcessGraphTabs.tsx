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
    <div className="flex border-b border-gray-200">
      {tabs.map((tab) => {
        const Icon = tab.icon
        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'text-gray-900 border-b-2 border-gray-200 bg-red-600/10'
                : 'text-gray-500 hover:text-gray-700 hover:bg-white'
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


