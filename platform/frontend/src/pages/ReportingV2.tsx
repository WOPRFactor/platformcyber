/**
 * Reporting V2 Page
 * =================
 * 
 * Página dedicada al nuevo módulo de reportería V2
 */

import React from 'react'
import { FileText } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { reportingAPI } from '../lib/api/reporting'
import { useWorkspace } from '../contexts/WorkspaceContext'
import ReportGeneratorV2 from './Reporting/components/ReportGeneratorV2'
import ReportsHistory from './Reporting/components/ReportsHistory'

const ReportingV2: React.FC = () => {
  const { currentWorkspace, isLoadingWorkspaces } = useWorkspace()

  const { data: reports, isLoading: reportsLoading, refetch: refetchReports } = useQuery({
    queryKey: ['reports', currentWorkspace?.id],
    queryFn: () => reportingAPI.listReports(currentWorkspace?.id),
    enabled: !!currentWorkspace?.id,
    staleTime: 0,
    cacheTime: 0,
  })

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Reporting V2</h1>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <FileText className="w-4 h-4" />
          Nuevo módulo de reportes profesionales
        </div>
      </div>

      {isLoadingWorkspaces ? (
        <div className="bg-gray-800 border border-blue-500 rounded-lg p-6 text-center">
          <p className="text-blue-400">Cargando workspaces...</p>
        </div>
      ) : !currentWorkspace ? (
        <div className="bg-gray-800 border border-yellow-500 rounded-lg p-6 text-center">
          <p className="text-yellow-400">Por favor selecciona un workspace para generar reportes</p>
        </div>
      ) : (
        <>
          {/* Nuevo módulo V2 */}
          <div className="bg-gray-800 border border-blue-500 rounded-lg p-6">
            <ReportGeneratorV2
              onReportGenerated={(result) => {
                console.log('📊 Reporte V2 generado:', result)
                // Recargar historial de reportes
                refetchReports()
              }}
            />
          </div>

          {/* Historial de reportes */}
          <ReportsHistory
            workspaceId={currentWorkspace?.id}
            reports={reports?.reports || []}
            reportsLoading={reportsLoading}
            onRefresh={() => refetchReports()}
          />
        </>
      )}
    </div>
  )
}

export default ReportingV2

