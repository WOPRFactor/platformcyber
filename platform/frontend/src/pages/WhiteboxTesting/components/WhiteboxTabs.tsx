import React from 'react'
import { Code, Package, Shield, Settings, Search } from 'lucide-react'

interface WhiteboxTabsProps {
  activeTab: string
  setActiveTab: (tab: string) => void
}

export const WhiteboxTabs: React.FC<WhiteboxTabsProps> = ({ activeTab, setActiveTab }) => {
  return (
    <div className="flex border-b border-green-500 mb-4 overflow-x-auto">
      <button
        onClick={() => setActiveTab('code_analysis')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTab === 'code_analysis'
            ? 'border-red-400 text-red-400'
            : 'border-transparent text-gray-400 hover:text-red-400'
        }`}
      >
        <Code className="w-4 h-4" />
        Análisis de Código
      </button>
      <button
        onClick={() => setActiveTab('dependency_analysis')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTab === 'dependency_analysis'
            ? 'border-red-400 text-red-400'
            : 'border-transparent text-gray-400 hover:text-red-400'
        }`}
      >
        <Package className="w-4 h-4" />
        Dependencias
      </button>
      <button
        onClick={() => setActiveTab('secrets_detection')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTab === 'secrets_detection'
            ? 'border-red-400 text-red-400'
            : 'border-transparent text-gray-400 hover:text-red-400'
        }`}
      >
        <Shield className="w-4 h-4" />
        Secrets
      </button>
      <button
        onClick={() => setActiveTab('config_analysis')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTab === 'config_analysis'
            ? 'border-red-400 text-red-400'
            : 'border-transparent text-gray-400 hover:text-red-400'
        }`}
      >
        <Settings className="w-4 h-4" />
        Configuración
      </button>
      <button
        onClick={() => setActiveTab('comprehensive')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTab === 'comprehensive'
            ? 'border-red-400 text-red-400'
            : 'border-transparent text-gray-400 hover:text-red-400'
        }`}
      >
        <Search className="w-4 h-4" />
        Completo
      </button>
    </div>
  )
}


