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
 * Lista todos los reportes disponibles
 * @param page - Página de resultados (default: 1)
 * @param limit - Número de reportes por página (default: 20)
 * @returns Lista de reportes con paginación
 */
export const listReports = async (page: number = 1, limit: number = 20): Promise<ReportListItem[]> => {
  const response = await api.get<ReportsListResponse>('reports', {
    params: { page, limit }
  })
  return response.data.reports
}

/**
 * Obtiene el estado de un reporte específico
 * @param reportId - ID del reporte
 * @returns Estado actual del reporte
 */
export const getReportStatus = async (reportId: string): Promise<ReportStatusResponse> => {
  const response = await api.get<ReportStatusResponse>(`reports/${reportId}/status`)
  return response.data
}

/**
 * Obtiene el contenido completo de un reporte
 * @param reportId - ID del reporte
 * @returns Datos completos del reporte
 */
export const getReportContent = async (reportId: string): Promise<ExecutiveSummaryData | TechnicalReportData | ComplianceReportData> => {
  const response = await api.get<{ report: ExecutiveSummaryData | TechnicalReportData | ComplianceReportData }>(`reports/${reportId}`)
  return response.data.report
}

/**
 * Genera un reporte ejecutivo
 * @param request - Datos para generar el reporte ejecutivo
 * @returns Respuesta de la generación iniciada
 */
export const generateExecutiveReport = async (request: Omit<ReportGenerationRequest, 'type'>): Promise<ReportGenerationResponse> => {
  const response = await api.post<ReportGenerationResponse>('reports/executive/generate', {
    ...request,
    type: 'executive'
  })
  return response.data
}

/**
 * Genera un reporte técnico detallado
 * @param request - Datos para generar el reporte técnico
 * @returns Respuesta de la generación iniciada
 */
export const generateTechnicalReport = async (request: Omit<ReportGenerationRequest, 'type'>): Promise<ReportGenerationResponse> => {
  const response = await api.post<ReportGenerationResponse>('reports/technical/generate', {
    ...request,
    type: 'technical'
  })
  return response.data
}

/**
 * Genera un reporte de cumplimiento
 * @param request - Datos para generar el reporte de cumplimiento
 * @returns Respuesta de la generación iniciada
 */
export const generateComplianceReport = async (request: ReportGenerationRequest): Promise<ReportGenerationResponse> => {
  const response = await api.post<ReportGenerationResponse>('reports/compliance/generate', request)
  return response.data
}

/**
 * Genera un reporte completo (ejecutivo + técnico + cumplimiento)
 * @param request - Datos para generar el reporte completo
 * @returns Respuesta de la generación iniciada
 */
export const generateCompleteReport = async (request: Omit<ReportGenerationRequest, 'type'>): Promise<ReportGenerationResponse> => {
  const response = await api.post<ReportGenerationResponse>('reports/complete/generate', {
    ...request,
    type: 'complete'
  })
  return response.data
}

/**
 * Exporta un reporte en el formato especificado
 * @param request - Datos para la exportación del reporte
 * @returns Resultado de la exportación con URL de descarga
 */
export const exportReport = async (request: ReportExportRequest): Promise<ReportExportResult> => {
  const response = await api.post<ReportExportResult>('reports/export', request)
  return response.data
}

/**
 * Elimina un reporte
 * @param reportId - ID del reporte a eliminar
 * @returns Confirmación de eliminación
 */
export const deleteReport = async (reportId: string): Promise<ReportDeletionResponse> => {
  const response = await api.delete<ReportDeletionResponse>(`reports/${reportId}`)
  return response.data
}

/**
 * Obtiene estadísticas de reportes
 * @returns Estadísticas generales de reportes generados
 */
export const getReportStatistics = async (): Promise<{
  total_reports: number
  reports_by_type: Record<string, number>
  reports_by_status: Record<string, number>
  recent_reports: ReportListItem[]
}> => {
  const response = await api.get<{
    total_reports: number
    reports_by_type: Record<string, number>
    reports_by_status: Record<string, number>
    recent_reports: ReportListItem[]
  }>('reports/statistics')
  return response.data
}

/**
 * Comparte un reporte con otros usuarios
 * @param reportId - ID del reporte a compartir
 * @param userIds - IDs de los usuarios con quienes compartir
 * @param permissions - Permisos de acceso ('read' | 'write' | 'admin')
 * @returns Confirmación de compartición
 */
export const shareReport = async (reportId: string, userIds: string[], permissions: string = 'read'): Promise<{ message: string }> => {
  const response = await api.post<{ message: string }>(`reports/${reportId}/share`, {
    user_ids: userIds,
    permissions
  })
  return response.data
}

/**
 * Archiva un reporte
 * @param reportId - ID del reporte a archivar
 * @returns Confirmación de archivamiento
 */
export const archiveReport = async (reportId: string): Promise<{ message: string }> => {
  const response = await api.post<{ message: string }>(`reports/${reportId}/archive`)
  return response.data
}

/**
 * Restaura un reporte archivado
 * @param reportId - ID del reporte a restaurar
 * @returns Confirmación de restauración
 */
export const restoreReport = async (reportId: string): Promise<{ message: string }> => {
  const response = await api.post<{ message: string }>(`reports/${reportId}/restore`)
  return response.data
}

/**
 * Objeto API de reportes - compatible hacia atrás
 * Agrupa todas las funciones de gestión de reportes
 */
export const reportingAPI = {
  listReports,
  getReportStatus,
  getReportContent,
  generateExecutiveReport,
  generateTechnicalReport,
  generateComplianceReport,
  generateCompleteReport,
  exportReport,
  deleteReport,
  getReportStatistics,
  shareReport,
  archiveReport,
  restoreReport
}



