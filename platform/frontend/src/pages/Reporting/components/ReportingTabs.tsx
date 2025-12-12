/**
 * Reporting Tabs Component
 * =========================
 * 
 * Componente para tabs de tipos de reporte.
 */

import React from 'react'
import { BarChart3, Target, Shield } from 'lucide-react'

interface ReportingTabsProps {
  activeTab: string
  setActiveTab: (tab: string) => void
}

const ReportingTabs: React.FC<ReportingTabsProps> = ({ activeTab, setActiveTab }) => {
  return (
    <div className="flex border-b border-green-500 mb-4 overflow-x-auto">
      <button
        onClick={() => setActiveTab('executive')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTab === 'executive'
            ? 'border-red-400 text-red-400'
            : 'border-transparent text-gray-400 hover:text-red-400'
        }`}
      >
        <BarChart3 className="w-4 h-4" />
        Ejecutivo
      </button>
      <button
        onClick={() => setActiveTab('technical')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTab === 'technical'
            ? 'border-red-400 text-red-400'
            : 'border-transparent text-gray-400 hover:text-red-400'
        }`}
      >
        <Target className="w-4 h-4" />
        Técnico
      </button>
      <button
        onClick={() => setActiveTab('compliance')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTab === 'compliance'
            ? 'border-red-400 text-red-400'
            : 'border-transparent text-gray-400 hover:text-red-400'
        }`}
      >
        <Shield className="w-4 h-4" />
        Cumplimiento
      </button>
    </div>
  )
}

export default ReportingTabs

