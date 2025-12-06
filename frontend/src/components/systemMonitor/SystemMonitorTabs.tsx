/**
 * SystemMonitorTabs Component
 * ============================
 * 
 * Tabs horizontales para filtrar logs por categoría.
 * Tabs: Unified, Backend, Celery, Tools
 */

import React from 'react'
import { MonitorTab } from '../../types/systemMonitor'

interface SystemMonitorTabsProps {
  activeTab: MonitorTab
  onTabChange: (tab: MonitorTab) => void
}

const tabs: { id: MonitorTab; label: string }[] = [
  { id: 'unified', label: 'Unified' },
  { id: 'backend', label: 'Backend' },
  { id: 'celery', label: 'Celery' },
  { id: 'tools', label: 'Tools' }
]

export const SystemMonitorTabs: React.FC<SystemMonitorTabsProps> = ({
  activeTab,
  onTabChange
}) => {
  return (
    <div className="flex items-center space-x-1 p-2 border-b border-green-500 bg-gray-800">
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`px-4 py-2 text-xs font-medium rounded-t transition-colors ${
            activeTab === tab.id
              ? 'bg-gray-900 text-cyan-400 border-t border-l border-r border-green-500'
              : 'text-gray-400 hover:text-cyan-400 hover:bg-gray-700/50'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}


