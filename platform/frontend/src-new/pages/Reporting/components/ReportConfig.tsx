/**
 * Report Configuration Component
 * ===============================
 * 
 * Componente para configuración de parámetros del reporte.
 */

import React from 'react'
import { useWorkspace } from '../../../contexts/WorkspaceContext'
import DatePicker from '../../../components/DatePicker'

interface ReportConfigProps {
  startDate: string
  setStartDate: (date: string) => void
  endDate: string
  setEndDate: (date: string) => void
  complianceStandard: string
  setComplianceStandard: (standard: string) => void
}

const ReportConfig: React.FC<ReportConfigProps> = ({
  startDate,
  setStartDate,
  endDate,
  setEndDate,
  complianceStandard,
  setComplianceStandard
}) => {
  const { currentWorkspace } = useWorkspace()
  
  const displayName = currentWorkspace 
    ? (currentWorkspace.name || `Workspace #${currentWorkspace.id}`)
    : 'No hay workspace seleccionado'

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Configuración del Reporte</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-2">Workspace</label>
          <div className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 min-h-[42px] flex items-center">
            <span className={currentWorkspace ? 'text-gray-900' : 'text-gray-500 italic'}>
              {displayName}
            </span>
          </div>
        </div>
        <div>
          <DatePicker
            label="Fecha Inicio"
            value={startDate}
            onChange={setStartDate}
            placeholder="dd/mm/yyyy"
            maxDate={endDate || undefined}
          />
        </div>
        <div>
          <DatePicker
            label="Fecha Fin"
            value={endDate}
            onChange={setEndDate}
            placeholder="dd/mm/yyyy"
            minDate={startDate || undefined}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-2">Estándar Cumplimiento</label>
          <select
            value={complianceStandard}
            onChange={(e) => setComplianceStandard(e.target.value)}
            className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500"
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
