/**
 * Módulo de Reportes
 * Maneja la generación, gestión y exportación de reportes ejecutivos, técnicos y de cumplimiento
 */

import { api } from '../shared/client'
import type {
  ExecutiveSummaryData,
  TechnicalReportData,
  ComplianceReportData,
  ReportExportResult,
  ReportListItem,
  ReportGenerationRequest,
  ReportExportRequest,
  ReportGenerationResponse,
  ReportStatusResponse,
  ReportsListResponse,
  ReportDeletionResponse
} from './types'

/**
 * Genera un reporte comprehensivo
 * @param workspaceId - ID del workspace
 * @param reportType - Tipo de reporte: 'full', 'executive', 'technical', 'compliance'
 * @param includeScans - IDs de scans a incluir (opcional)
 * @param includeVulns - IDs de vulnerabilidades a incluir (opcional)
 * @param dateFrom - Fecha inicio (opcional, ISO string)
 * @param dateTo - Fecha fin (opcional, ISO string)
 * @returns Datos del reporte generado
 */
export const generateReport = async (
  workspaceId: number,
  reportType: 'full' | 'executive' | 'technical' | 'compliance' = 'full',
  includeScans?: number[],
  includeVulns?: number[],
  dateFrom?: string,
  dateTo?: string
): Promise<{ status: string; report: any }> => {
  // Convertir fechas de formato yyyy-MM-dd a ISO completo si están presentes
  let dateFromISO = dateFrom
  let dateToISO = dateTo
  
  if (dateFrom && dateFrom.match(/^\d{4}-\d{2}-\d{2}$/)) {
    // Si es formato yyyy-MM-dd, convertir a ISO completo
    dateFromISO = `${dateFrom}T00:00:00Z`
  }
  
  if (dateTo && dateTo.match(/^\d{4}-\d{2}-\d{2}$/)) {
    // Si es formato yyyy-MM-dd, convertir a ISO completo (fin del día)
    dateToISO = `${dateTo}T23:59:59Z`
  }
  
  const response = await api.post<{ status: string; report: any }>('reporting/generate', {
    workspace_id: workspaceId,
    report_type: reportType,
    include_scans: includeScans,
    include_vulns: includeVulns,
    date_from: dateFromISO,
    date_to: dateToISO
  })
  return response.data
}

/**
 * Genera un reporte ejecutivo
 * @param workspaceId - ID del workspace
 * @param dateFrom - Fecha inicio (opcional)
 * @param dateTo - Fecha fin (opcional)
 * @returns Datos del reporte ejecutivo
 */
export const generateExecutiveSummary = async (
  workspaceId: number,
  dateFrom?: string,
  dateTo?: string
): Promise<{ success: boolean; data: any }> => {
  try {
    console.log('📊 Generando resumen ejecutivo:', { workspaceId, dateFrom, dateTo })
    const result = await generateReport(workspaceId, 'executive', undefined, undefined, dateFrom, dateTo)
    console.log('✅ Resultado del reporte (raw):', result)
    console.log('✅ Resultado del reporte (JSON):', JSON.stringify(result, null, 2))
    return {
      success: result.status === 'success',
      data: result.report
    }
  } catch (error: any) {
    console.error('❌ Error generando resumen ejecutivo:', error)
    console.error('❌ Error detallado:', JSON.stringify(error, null, 2))
    return {
      success: false,
      data: { error: error.message || 'Error desconocido' }
    }
  }
}

/**
 * Genera un reporte técnico detallado
 * @param workspaceId - ID del workspace
 * @param dateFrom - Fecha inicio (opcional)
 * @param dateTo - Fecha fin (opcional)
 * @returns Datos del reporte técnico
 */
export const generateTechnicalReport = async (
  workspaceId: number,
  dateFrom?: string,
  dateTo?: string
): Promise<{ success: boolean; data: any }> => {
  try {
    console.log('📊 Generando reporte técnico:', { workspaceId, dateFrom, dateTo })
    const result = await generateReport(workspaceId, 'technical', undefined, undefined, dateFrom, dateTo)
    console.log('✅ Resultado del reporte:', result)
    return {
      success: result.status === 'success',
      data: result.report
    }
  } catch (error: any) {
    console.error('❌ Error generando reporte técnico:', error)
    return {
      success: false,
      data: { error: error.message || 'Error desconocido' }
    }
  }
}

/**
 * Genera un reporte de cumplimiento
 * @param workspaceId - ID del workspace
 * @param standard - Estándar de cumplimiento (opcional)
 * @param dateFrom - Fecha inicio (opcional)
 * @param dateTo - Fecha fin (opcional)
 * @returns Datos del reporte de cumplimiento
 */
export const generateComplianceReport = async (
  workspaceId: number,
  standard: string = 'general',
  dateFrom?: string,
  dateTo?: string
): Promise<{ success: boolean; data: any }> => {
  try {
    console.log('📊 Generando reporte de cumplimiento:', { workspaceId, standard, dateFrom, dateTo })
    const result = await generateReport(workspaceId, 'compliance', undefined, undefined, dateFrom, dateTo)
    console.log('✅ Resultado del reporte:', result)
    return {
      success: result.status === 'success',
      data: { ...result.report, standard }
    }
  } catch (error: any) {
    console.error('❌ Error generando reporte de cumplimiento:', error)
    return {
      success: false,
      data: { error: error.message || 'Error desconocido' }
    }
  }
}

/**
 * Exporta un reporte a JSON
 * @param workspaceId - ID del workspace
 * @param reportType - Tipo de reporte
 * @param dateFrom - Fecha inicio (opcional)
 * @param dateTo - Fecha fin (opcional)
 * @returns Blob del archivo JSON
 */
export const exportToJSON = async (
  workspaceId: number,
  reportType: 'full' | 'executive' | 'technical' | 'compliance' = 'full',
  dateFrom?: string,
  dateTo?: string
): Promise<Blob> => {
  const response = await api.post(
    'reporting/export/json',
    {
      workspace_id: workspaceId,
      report_type: reportType,
      date_from: dateFrom,
      date_to: dateTo
    },
    { responseType: 'blob' }
  )
  return response.data
}

/**
 * Exporta un reporte a HTML
 * @param workspaceId - ID del workspace
 * @param reportType - Tipo de reporte
 * @param dateFrom - Fecha inicio (opcional)
 * @param dateTo - Fecha fin (opcional)
 * @returns Blob del archivo HTML
 */
export const exportToHTML = async (
  workspaceId: number,
  reportType: 'full' | 'executive' | 'technical' | 'compliance' = 'full',
  dateFrom?: string,
  dateTo?: string
): Promise<Blob> => {
  const response = await api.post(
    'reporting/export/html',
    {
      workspace_id: workspaceId,
      report_type: reportType,
      date_from: dateFrom,
      date_to: dateTo
    },
    { responseType: 'blob' }
  )
  return response.data
}

/**
 * Exporta un reporte en el formato especificado
 * @param reportData - Datos del reporte a exportar
 * @param format - Formato: 'json' | 'html'
 * @returns Resultado de la exportación
 */
export const exportReport = async (
  reportData: any,
  format: 'json' | 'html'
): Promise<{ success: boolean; content?: string; filename?: string; format?: string }> => {
  try {
    // Extraer workspace_id del reporte
    const workspaceId = reportData.metadata?.workspace_id
    if (!workspaceId) {
      throw new Error('Workspace ID no encontrado en el reporte')
    }

    const reportType = reportData.metadata?.report_type || 'full'
    const dateFrom = reportData.metadata?.date_from
    const dateTo = reportData.metadata?.date_to

    if (format === 'json') {
      const blob = await exportToJSON(workspaceId, reportType, dateFrom, dateTo)
      const reader = new FileReader()
      return new Promise((resolve) => {
        reader.onloadend = () => {
          const base64 = (reader.result as string).split(',')[1]
          resolve({
            success: true,
            content: base64,
            filename: `report-${workspaceId}-${Date.now()}.json`,
            format: 'json'
          })
        }
        reader.readAsDataURL(blob)
      })
    } else if (format === 'html') {
      const blob = await exportToHTML(workspaceId, reportType, dateFrom, dateTo)
      const reader = new FileReader()
      return new Promise((resolve) => {
        reader.onloadend = () => {
          const base64 = (reader.result as string).split(',')[1]
          resolve({
            success: true,
            content: base64,
            filename: `report-${workspaceId}-${Date.now()}.html`,
            format: 'html'
          })
        }
        reader.readAsDataURL(blob)
      })
    } else {
      throw new Error(`Formato no soportado: ${format}`)
    }
  } catch (error: any) {
    return {
      success: false
    }
  }
}

/**
 * Lista todos los reportes disponibles
 */
export const listReports = async (workspaceId?: number, limit: number = 20, offset: number = 0): Promise<{
  status: string
  reports: ReportListItem[]
  total: number
  limit: number
  offset: number
}> => {
  const params: any = { limit, offset }
  if (workspaceId) {
    params.workspace_id = workspaceId
  }
  
  const response = await api.get<{
    status: string
    reports: ReportListItem[]
    total: number
    limit: number
    offset: number
  }>('reporting/history', { params })
  return response.data
}

/**
 * Obtiene un reporte específico por ID
 */
export const getReport = async (reportId: number): Promise<{
  status: string
  report: any
}> => {
  const response = await api.get<{ status: string; report: any }>(`reporting/history/${reportId}`)
  return response.data
}

/**
 * Genera un reporte usando el nuevo módulo V2 (asíncrono)
 * @param workspaceId - ID del workspace
 * @param reportType - Tipo de reporte: 'technical', 'executive', 'compliance'
 * @param format - Formato: 'pdf'
 * @returns Datos de la tarea iniciada (task_id, status, etc.)
 */
export const generateReportV2 = async (
  workspaceId: number,
  reportType: 'technical' | 'executive' | 'compliance' = 'technical',
  format: 'pdf' = 'pdf'
): Promise<{
  task_id: string
  status: string
  message: string
  workspace_id: number
  report_type: string
  format: string
}> => {
  const response = await api.post<{
    task_id: string
    status: string
    message: string
    workspace_id: number
    report_type: string
    format: string
  }>('reporting/generate-v2', {
    workspace_id: workspaceId,
    report_type: reportType,
    format: format
  })
  return response.data
}

/**
 * Obtiene el estado de una tarea de generación de reporte V2
 * @param taskId - ID de la tarea Celery
 * @returns Estado de la tarea con progreso y resultado si está completo
 */
export const getReportStatus = async (taskId: string): Promise<{
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress?: number
  current?: number
  total?: number
  message?: string
  step?: string
  result?: {
    report_id: number
    report_path: string
    file_size: number
    statistics: any
    risk_metrics: any
    metadata: any
    files_processed: number
    findings_count: number
  }
  error?: string
}> => {
  const response = await api.get<{
    task_id: string
    status: 'pending' | 'processing' | 'completed' | 'failed'
    progress?: number
    current?: number
    total?: number
    message?: string
    step?: string
    result?: any
    error?: string
  }>(`reporting/status/${taskId}`)
  return response.data
}

/**
 * Objeto API de reportes
 * Agrupa todas las funciones de gestión de reportes
 */
export const reportingAPI = {
  listReports,
  generateReport,
  generateExecutiveSummary,
  generateTechnicalReport,
  generateComplianceReport,
  exportReport,
  exportToJSON,
  exportToHTML,
  // Nuevo módulo V2
  generateReportV2,
  getReportStatus
}



