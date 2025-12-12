/**
 * Reporting Page
 * ==============
 * 
 * Página principal de reporting refactorizada.
 */

import React, { useState } from 'react'
import { FileText } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { reportingAPI } from '../../lib/api/reporting'
import { toast } from 'sonner'
import { useReportingMutations } from './hooks/useReportingMutations'
import { useWorkspace } from '../../contexts/WorkspaceContext'
import {
  ReportConfig,
  ReportingTabs,
  ReportGenerator,
  GeneratedReport,
  ReportsHistory,
  ExecutiveReportModal
} from './components'

const Reporting: React.FC = () => {
  const { currentWorkspace, isLoadingWorkspaces } = useWorkspace()
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [complianceStandard, setComplianceStandard] = useState('general')
  const [exportFormat, setExportFormat] = useState<'json' | 'html' | 'pdf'>('html')
  const [activeTab, setActiveTab] = useState('executive')
  const [generatedReport, setGeneratedReport] = useState<any>(null)
  const [isReportModalOpen, setIsReportModalOpen] = useState(false)

  // Primero definir las funciones de descarga (sin dependencias circulares)
  
  // Primero definir generateReportHTML (no tiene dependencias de otras funciones)
  const generateReportHTML = React.useCallback((report: any): string => {
    const reportType = report.metadata?.report_type || 'full'
    const workspaceName = currentWorkspace?.name || 'Unknown'
    const generatedAt = report.metadata?.generated_at 
      ? new Date(report.metadata.generated_at).toLocaleString('es-AR')
      : new Date().toLocaleString('es-AR')
    
    let html = `<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Pentesting - ${workspaceName}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #e0e0e0; }
        .container { max-width: 1200px; margin: 0 auto; background: #2a2a2a; padding: 30px; border-radius: 8px; }
        h1 { color: #4ade80; border-bottom: 2px solid #4ade80; padding-bottom: 10px; }
        h2 { color: #60a5fa; margin-top: 30px; }
        h3 { color: #a78bfa; }
        .metadata { background: #1a1a1a; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .stat { display: inline-block; margin: 10px 20px 10px 0; padding: 10px 20px; background: #3a3a3a; border-radius: 5px; }
        .stat-value { font-size: 24px; font-weight: bold; color: #4ade80; }
        .stat-label { font-size: 12px; color: #9ca3af; }
        .finding { background: #2a2a2a; padding: 15px; margin: 10px 0; border-left: 4px solid #4ade80; border-radius: 4px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #3a3a3a; }
        th { background: #1a1a1a; color: #4ade80; }
        .severity-critical { color: #ef4444; }
        .severity-high { color: #f97316; }
        .severity-medium { color: #eab308; }
        .severity-low { color: #3b82f6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Reporte de Pentesting</h1>
        <div class="metadata">
            <p><strong>Workspace:</strong> ${workspaceName}</p>
            <p><strong>Tipo de Reporte:</strong> ${reportType.toUpperCase()}</p>
            <p><strong>Generado:</strong> ${generatedAt}</p>
        </div>`
    
    // Agregar resumen ejecutivo si existe
    if (report.executive_summary) {
      const es = report.executive_summary
      html += `
        <h2>📈 Resumen Ejecutivo</h2>
        <div class="stat">
            <div class="stat-value">${es.total_scans || 0}</div>
            <div class="stat-label">Scans Totales</div>
        </div>
        <div class="stat">
            <div class="stat-value">${es.total_vulnerabilities || 0}</div>
            <div class="stat-label">Vulnerabilidades</div>
        </div>
        <div class="stat">
            <div class="stat-value">${es.risk_score || 0}</div>
            <div class="stat-label">Puntuación de Riesgo</div>
        </div>
        <div class="stat">
            <div class="stat-value">${es.risk_level || 'N/A'}</div>
            <div class="stat-label">Nivel de Riesgo</div>
        </div>`
      
      if (es.severity_distribution) {
        html += `<h3>Distribución por Severidad</h3><table><tr><th>Severidad</th><th>Cantidad</th></tr>`
        Object.entries(es.severity_distribution).forEach(([severity, count]) => {
          html += `<tr><td class="severity-${severity}">${severity.toUpperCase()}</td><td>${count}</td></tr>`
        })
        html += `</table>`
      }
      
      if (es.key_findings && Array.isArray(es.key_findings)) {
        html += `<h3>Hallazgos Clave</h3>`
        es.key_findings.forEach((finding: string) => {
          html += `<div class="finding">${finding}</div>`
        })
      }
    }
    
    html += `
    </div>
</body>
</html>`
    
    return html
  }, [currentWorkspace])
  
  const downloadReportAsHTML = React.useCallback((report: any) => {
    try {
      // Generar HTML del reporte
      const htmlContent = generateReportHTML(report)
      
      // Crear blob y descargar
      const blob = new Blob([htmlContent], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `reporte-${report.metadata?.report_type || 'full'}-${currentWorkspace?.id || 'unknown'}-${Date.now()}.html`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
      toast.success('Reporte descargado exitosamente')
    } catch (error) {
      console.error('❌ Error descargando reporte como HTML:', error)
      toast.error('Error al descargar el reporte')
    }
  }, [currentWorkspace, generateReportHTML])
  
  // Definir handleReportGenerated después de las funciones de descarga
  const handleReportGenerated = React.useCallback((report: any) => {
    console.log('🔄 handleReportGenerated llamado con:', report)
    console.log('🔄 handleReportGenerated (JSON):', JSON.stringify(report, null, 2))
    
    if (!currentWorkspace || !currentWorkspace.id) {
      console.error('❌ No hay workspace al recibir reporte')
      return
    }
    
    const reportWithMetadata = {
      ...report,
      metadata: {
        ...report.metadata,
        workspace_id: currentWorkspace.id,
        date_from: startDate || undefined,
        date_to: endDate || undefined
      }
    }
    
    console.log('📊 Setting generatedReport:', JSON.stringify(reportWithMetadata, null, 2))
    setGeneratedReport(reportWithMetadata)
    
    // Abrir modal para mostrar el reporte
    console.log('🚪 Abriendo modal con datos:', reportWithMetadata)
    setIsReportModalOpen(true)
    console.log('✅ Estado isReportModalOpen seteado a true')
    
    // Descargar automáticamente el reporte según el tipo de contenido
    downloadReportAutomatically(reportWithMetadata)
  }, [currentWorkspace, startDate, endDate, downloadReportAutomatically])

  const {
    executiveMutation: baseExecutiveMutation,
    technicalMutation,
    complianceMutation,
    exportMutation
  } = useReportingMutations()
  
  // Crear una versión de executiveMutation que actualice el estado directamente
  const executiveMutation = React.useMemo(() => ({
    ...baseExecutiveMutation,
    mutate: (params: any, options?: any) => {
      console.log('📥 Wrapper mutate llamado con:', params, options)
      baseExecutiveMutation.mutate(params, {
        ...options,
        onSuccess: (data: any, variables: any, context: any) => {
          console.log('📥 Wrapper onSuccess ejecutado (raw):', data)
          console.log('📥 Wrapper onSuccess ejecutado (JSON):', JSON.stringify(data, null, 2))
          if (data.success && data.data) {
            console.log('📥 Reporte recibido directamente en Reporting.tsx (raw):', data.data)
            console.log('📥 Reporte recibido directamente en Reporting.tsx (JSON):', JSON.stringify(data.data, null, 2))
            console.log('🚪 Llamando handleReportGenerated para abrir modal...')
            handleReportGenerated(data.data)
          } else {
            console.warn('⚠️ data.success o data.data no están presentes:', { success: data.success, hasData: !!data.data })
          }
          // Llamar al onSuccess original si existe
          if (options?.onSuccess) {
            console.log('📥 Llamando onSuccess original de options')
            options.onSuccess(data, variables, context)
          }
        }
      })
    }
  }), [baseExecutiveMutation, handleReportGenerated])

  const { data: reports, isLoading: reportsLoading, refetch: refetchReports } = useQuery({
    queryKey: ['reports', currentWorkspace?.id],
    queryFn: () => reportingAPI.listReports(currentWorkspace?.id),
    enabled: !!currentWorkspace?.id,
    staleTime: 0,
    cacheTime: 0,
  })

  // Refetch reports cuando se genera uno nuevo
  React.useEffect(() => {
    if (isReportModalOpen && generatedReport) {
      console.log('🔄 Refrescando historial de reportes después de generar uno nuevo')
      refetchReports()
    }
  }, [isReportModalOpen, generatedReport, refetchReports])

  const handleGenerateReport = React.useCallback((reportType: string) => {
    if (!currentWorkspace) {
      toast.error('Por favor selecciona un workspace')
      return
    }

    const params = {
      workspaceId: currentWorkspace.id,
      startDate: startDate || undefined,
      endDate: endDate || undefined
    }

    switch (reportType) {
      case 'executive':
        executiveMutation.mutate(params, {
          onSuccess: (data) => {
            if (data.success) {
              const report = {
                ...data.data,
                metadata: {
                  ...data.data.metadata,
                  workspace_id: currentWorkspace.id,
                  report_type: 'executive',
                  date_from: startDate || undefined,
                  date_to: endDate || undefined
                }
              }
              setGeneratedReport(report)
            }
          }
        })
        break
      case 'technical':
        technicalMutation.mutate(params, {
          onSuccess: (data) => {
            if (data.success) {
              const report = {
                ...data.data,
                metadata: {
                  ...data.data.metadata,
                  workspace_id: currentWorkspace.id,
                  report_type: 'technical',
                  date_from: startDate || undefined,
                  date_to: endDate || undefined
                }
              }
              setGeneratedReport(report)
            }
          }
        })
        break
      case 'compliance':
        complianceMutation.mutate({ ...params, standard: complianceStandard }, {
          onSuccess: (data) => {
            if (data.success) {
              const report = {
                ...data.data,
                metadata: {
                  ...data.data.metadata,
                  workspace_id: currentWorkspace.id,
                  report_type: 'compliance',
                  date_from: startDate || undefined,
                  date_to: endDate || undefined
                }
              }
              setGeneratedReport(report)
            }
          }
        })
        break
      default:
        toast.error(`Tipo de reporte desconocido: ${reportType}`)
    }
  }, [currentWorkspace, startDate, endDate, complianceStandard, executiveMutation, technicalMutation, complianceMutation])

  const handleExportReport = () => {
    if (!generatedReport) {
      toast.error('Primero genere un reporte')
      return
    }

    exportMutation.mutate({
      reportData: generatedReport,
      format: exportFormat
    })
  }

  // LOGS BÁSICOS - DEBEN APARECER SIEMPRE

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Reporting</h1>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <FileText className="w-4 h-4" />
          Sistema de reportes profesionales de pentesting
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
          <ReportConfig
            startDate={startDate}
            setStartDate={setStartDate}
            endDate={endDate}
            setEndDate={setEndDate}
            complianceStandard={complianceStandard}
            setComplianceStandard={setComplianceStandard}
          />

          {/* Módulo anterior */}
          <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
            <div className="w-full">
              <ReportingTabs activeTab={activeTab} setActiveTab={setActiveTab} />
              <ReportGenerator
                activeTab={activeTab}
                complianceStandard={complianceStandard}
                executiveMutation={executiveMutation}
                technicalMutation={technicalMutation}
                complianceMutation={complianceMutation}
                startDate={startDate}
                endDate={endDate}
              />
            </div>
          </div>

        </>
      )}

      {generatedReport && (
        <GeneratedReport
          generatedReport={generatedReport}
          exportFormat={exportFormat}
          setExportFormat={setExportFormat}
          exportMutation={exportMutation}
          handleExportReport={handleExportReport}
        />
      )}

      <ReportsHistory
        workspaceId={currentWorkspace?.id}
        reports={reports}
        reportsLoading={reportsLoading}
        onRefresh={() => refetchReports()}
      />

      {/* Modal de Reporte Ejecutivo */}
      <ExecutiveReportModal
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
        reportData={generatedReport}
        workspaceName={currentWorkspace?.name}
      />
    </div>
  )
}

export default Reporting


