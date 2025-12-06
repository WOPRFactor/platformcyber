import React from 'react'
import { Terminal, Shield, Activity, Database, FolderOpen } from 'lucide-react'

interface IntegrationTabsProps {
  activeTab: string
  setActiveTab: (tab: string) => void
}

const tabs = [
  { id: 'metasploit', label: 'Metasploit', icon: Terminal },
  { id: 'burp', label: 'Burp Suite', icon: Shield },
  { id: 'nmap', label: 'Nmap Avanzado', icon: Activity },
  { id: 'sqlmap', label: 'SQLMap', icon: Database },
  { id: 'gobuster', label: 'Directory Busting', icon: FolderOpen },
]

export const IntegrationTabs: React.FC<IntegrationTabsProps> = ({
  activeTab,
  setActiveTab
}) => {
  return (
    <div className="flex border-b border-green-500 mb-4 overflow-x-auto">
      {tabs.map((tab) => {
        const Icon = tab.icon
        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-red-400 text-red-400'
                : 'border-transparent text-gray-400 hover:text-red-400'
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


