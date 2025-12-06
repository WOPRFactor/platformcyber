/**
 * Report Configuration Component
 * ===============================
 * 
 * Componente para configuración de parámetros del reporte.
 */

import React from 'react'

interface ReportConfigProps {
  target: string
  setTarget: (target: string) => void
  startDate: string
  setStartDate: (date: string) => void
  endDate: string
  setEndDate: (date: string) => void
  complianceStandard: string
  setComplianceStandard: (standard: string) => void
}

const ReportConfig: React.FC<ReportConfigProps> = ({
  target,
  setTarget,
  startDate,
  setStartDate,
  endDate,
  setEndDate,
  complianceStandard,
  setComplianceStandard
}) => {
  return (
    <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-green-400">Configuración del Reporte</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-green-400 mb-2">Target</label>
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="192.168.1.1 o dominio.com"
            className="w-full bg-gray-900 border border-green-500 rounded px-3 py-2 text-green-400 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-green-400 mb-2">Fecha Inicio</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full bg-gray-900 border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-green-400 mb-2">Fecha Fin</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="w-full bg-gray-900 border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-green-400 mb-2">Estándar Cumplimiento</label>
          <select
            value={complianceStandard}
            onChange={(e) => setComplianceStandard(e.target.value)}
            className="w-full bg-gray-900 border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="general">General</option>
            <option value="pci-dss">PCI-DSS</option>
            <option value="hipaa">HIPAA</option>
          </select>
        </div>
      </div>
    </div>
  )
}

export default ReportConfig

