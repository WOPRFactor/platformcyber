/**
 * IA Tabs Component
 * ==================
 * 
 * Componente para las pestañas de navegación de IA.
 */

import React from 'react'
import { Bot, TrendingUp, Code, FileText, Brain } from 'lucide-react'

interface IATabsProps {
  activeTab: 'chatbot' | 'predictive' | 'payloads' | 'reports' | 'legacy'
  setActiveTab: (tab: 'chatbot' | 'predictive' | 'payloads' | 'reports' | 'legacy') => void
}

const IATabs: React.FC<IATabsProps> = ({ activeTab, setActiveTab }) => {
  return (
    <div className="flex border-b border-green-500 mb-6 overflow-x-auto">
      <button
        onClick={() => setActiveTab('chatbot')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTab === 'chatbot'
            ? 'border-red-400 text-red-400'
            : 'border-transparent text-gray-400 hover:text-red-400'
        }`}
      >
        <Bot size={16} />
        Chatbot IA
      </button>
      <button
        onClick={() => setActiveTab('predictive')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTab === 'predictive'
            ? 'border-red-400 text-red-400'
            : 'border-transparent text-gray-400 hover:text-red-400'
        }`}
      >
        <TrendingUp size={16} />
        Análisis Predictivo
      </button>
      <button
        onClick={() => setActiveTab('payloads')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTab === 'payloads'
            ? 'border-red-400 text-red-400'
            : 'border-transparent text-gray-400 hover:text-red-400'
        }`}
      >
        <Code size={16} />
        Payloads IA
      </button>
      <button
        onClick={() => setActiveTab('reports')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTab === 'reports'
            ? 'border-red-400 text-red-400'
            : 'border-transparent text-gray-400 hover:text-red-400'
        }`}
      >
        <FileText size={16} />
        Análisis de Reportes
      </button>
      <button
        onClick={() => setActiveTab('legacy')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTab === 'legacy'
            ? 'border-red-400 text-red-400'
            : 'border-transparent text-gray-400 hover:text-red-400'
        }`}
      >
        <Brain size={16} />
        Funciones Legacy
      </button>
    </div>
  )
}

export default IATabs


