import React from 'react'
import { Globe, Shield, Search, Key, Activity } from 'lucide-react'

interface ReconnaissanceTabsProps {
  activeTab: string
  setActiveTab: (tab: string) => void
}

const tabs = [
  { id: 'basic', label: 'Básico', icon: Globe },
  { id: 'osint', label: 'OSINT', icon: Shield },
  { id: 'web', label: 'Web Crawling', icon: Search },
  { id: 'secrets', label: 'Secrets', icon: Key },
  { id: 'complete', label: 'Completo', icon: Activity },
]

export const ReconnaissanceTabs: React.FC<ReconnaissanceTabsProps> = ({
  activeTab,
  setActiveTab
}) => {
  return (
    <div className="flex border-b border-gray-200 mb-4 overflow-x-auto">
      {tabs.map((tab) => {
        const Icon = tab.icon
        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-gray-200 text-gray-900'
                : 'border-transparent text-gray-500 hover:text-gray-900'
            }`}
          >
            <Icon className="w-4 h-4" />
            {tab.label}
          </button>
        )
      })}
    </div>
  )
}


