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
    <div className="flex border-b border-green-500 mb-4 overflow-x-auto">
      <button
        onClick={() => {
          setActiveTool('nmap')
          setActiveTab('quick')
        }}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTool === 'nmap'
            ? 'border-green-400 text-green-400'
            : 'border-transparent text-gray-400 hover:text-green-400'
        }`}
      >
        <Search className="w-4 h-4" />
        Nmap
      </button>
      <button
        onClick={() => setActiveTool('rustscan')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTool === 'rustscan'
            ? 'border-green-400 text-green-400'
            : 'border-transparent text-gray-400 hover:text-green-400'
        }`}
      >
        <Rocket className="w-4 h-4" />
        RustScan
      </button>
      <button
        onClick={() => setActiveTool('masscan')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTool === 'masscan'
            ? 'border-green-400 text-green-400'
            : 'border-transparent text-gray-400 hover:text-green-400'
        }`}
      >
        <Gauge className="w-4 h-4" />
        Masscan
      </button>
      <button
        onClick={() => setActiveTool('naabu')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTool === 'naabu'
            ? 'border-green-400 text-green-400'
            : 'border-transparent text-gray-400 hover:text-green-400'
        }`}
      >
        <Zap className="w-4 h-4" />
        Naabu
      </button>
      <button
        onClick={() => setActiveTool('enumeration')}
        className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
          activeTool === 'enumeration'
            ? 'border-green-400 text-green-400'
            : 'border-transparent text-gray-400 hover:text-green-400'
        }`}
      >
        <Server className="w-4 h-4" />
        Enumeración
      </button>
    </div>
  )
}

export default ScanningToolTabs

