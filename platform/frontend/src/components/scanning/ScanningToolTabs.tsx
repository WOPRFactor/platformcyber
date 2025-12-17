/**
 * ScanningToolTabs Component
 * ===========================
 * 
 * Barra de pestañas para seleccionar herramientas de escaneo.
 */

import React from 'react'
import { Search, Rocket, Gauge, Zap, Server } from 'lucide-react'

interface ScanningToolTabsProps {
  activeTool: string
  setActiveTool: (tool: string) => void
  setActiveTab: (tab: string) => void
}

const ScanningToolTabs: React.FC<ScanningToolTabsProps> = ({
  activeTool,
  setActiveTool,
  setActiveTab
}) => {
  return (
    <div className="flex border-b border-gray-200 mb-4 overflow-x-auto">
      <button
        onClick={() => {
          setActiveTool('nmap')
          setActiveTab('quick')
        }}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTool === 'nmap'
            ? 'border-gray-200 text-gray-900'
            : 'border-transparent text-gray-500 hover:text-gray-900'
        }`}
      >
        <Search className="w-4 h-4" />
        Nmap
      </button>
      <button
        onClick={() => setActiveTool('rustscan')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTool === 'rustscan'
            ? 'border-gray-200 text-gray-900'
            : 'border-transparent text-gray-500 hover:text-gray-900'
        }`}
      >
        <Rocket className="w-4 h-4" />
        RustScan
      </button>
      <button
        onClick={() => setActiveTool('masscan')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTool === 'masscan'
            ? 'border-gray-200 text-gray-900'
            : 'border-transparent text-gray-500 hover:text-gray-900'
        }`}
      >
        <Gauge className="w-4 h-4" />
        Masscan
      </button>
      <button
        onClick={() => setActiveTool('naabu')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTool === 'naabu'
            ? 'border-gray-200 text-gray-900'
            : 'border-transparent text-gray-500 hover:text-gray-900'
        }`}
      >
        <Zap className="w-4 h-4" />
        Naabu
      </button>
      <button
        onClick={() => setActiveTool('enumeration')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTool === 'enumeration'
            ? 'border-gray-200 text-gray-900'
            : 'border-transparent text-gray-500 hover:text-gray-900'
        }`}
      >
        <Server className="w-4 h-4" />
        Enumeración
      </button>
    </div>
  )
}

export default ScanningToolTabs

