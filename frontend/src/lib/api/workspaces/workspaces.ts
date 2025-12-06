/**
 * Módulo de Workspaces
 * Maneja operaciones relacionadas con workspaces, sesiones y evidencia
 */

import { api } from '../shared/client'
import type {
  Workspace,
  Session,
  Evidence,
  CreateWorkspaceData,
  CreateSessionData,
  CreateEvidenceData,
  EvidenceFilters
} from './types'

/**
 * Obtiene todos los workspaces disponibles
 * @returns Array de workspaces
 */
export const getWorkspaces = async (): Promise<Workspace[]> => {
  const response = await api.get<Workspace[]>('workspaces/')
  return response.data
}

/**
 * Crea un nuevo workspace
 * @param data - Datos para crear el workspace
 * @returns Workspace creado
 */
export const createWorkspace = async (data: CreateWorkspaceData): Promise<Workspace> => {
  const response = await api.post<Workspace>('workspaces/', data)
  return response.data
}

/**
 * Actualiza un workspace existente
 * @param id - ID del workspace
 * @param data - Datos a actualizar
 * @returns Workspace actualizado
 */
export const updateWorkspace = async (id: number, data: Partial<Workspace>): Promise<Workspace> => {
  const response = await api.put<{ workspace: Workspace }>(`workspaces/${id}`, data)
  return response.data.workspace
}

/**
 * Elimina un workspace
 * @param id - ID del workspace a eliminar
 */
export const deleteWorkspace = async (id: number): Promise<void> => {
  await api.delete(`workspaces/${id}`)
}

/**
 * Obtiene las sesiones de un workspace específico
 * @param workspaceId - ID del workspace
 * @returns Array de sesiones
 */
export const getWorkspaceSessions = async (workspaceId: number): Promise<Session[]> => {
  const response = await api.get<Session[]>(`workspaces/${workspaceId}/sessions`)
  return response.data
}

/**
 * Crea una nueva sesión en un workspace
 * @param workspaceId - ID del workspace
 * @param data - Datos de la sesión
 * @returns Sesión creada
 */
export const createSession = async (workspaceId: number, data: CreateSessionData): Promise<Session> => {
  const response = await api.post<{ session: Session }>(`workspaces/${workspaceId}/sessions`, data)
  return response.data.session
}

/**
 * Obtiene la evidencia de un workspace
 * @param workspaceId - ID del workspace
 * @param filters - Filtros opcionales para la evidencia
 * @returns Array de evidencia
 */
export const getWorkspaceEvidence = async (
  workspaceId: number,
  filters?: EvidenceFilters
): Promise<Evidence[]> => {
  const params = new URLSearchParams()

  if (filters?.type) params.append('type', filters.type)
  if (filters?.session_id) params.append('session_id', filters.session_id.toString())
  if (filters?.tags?.length) {
    filters.tags.forEach(tag => params.append('tags', tag))
  }

  const queryString = params.toString()
  const url = queryString ? `workspaces/${workspaceId}/evidence?${queryString}` : `workspaces/${workspaceId}/evidence`

  const response = await api.get<Evidence[]>(url)
  return response.data
}

/**
 * Crea nueva evidencia en un workspace
 * @param workspaceId - ID del workspace
 * @param data - Datos de la evidencia
 * @returns Evidencia creada
 */
export const createEvidence = async (
  workspaceId: number,
  data: CreateEvidenceData
): Promise<Evidence> => {
  const response = await api.post<{ evidence: Evidence }>(`workspaces/${workspaceId}/evidence`, data)
  return response.data.evidence
}

/**
 * Actualiza evidencia existente
 * @param workspaceId - ID del workspace
 * @param evidenceId - ID de la evidencia
 * @param data - Datos a actualizar
 * @returns Evidencia actualizada
 */
export const updateEvidence = async (
  workspaceId: number,
  evidenceId: number,
  data: Partial<Evidence>
): Promise<Evidence> => {
  const response = await api.put<{ evidence: Evidence }>(
    `workspaces/${workspaceId}/evidence/${evidenceId}`,
    data
  )
  return response.data.evidence
}

/**
 * Elimina evidencia
 * @param workspaceId - ID del workspace
 * @param evidenceId - ID de la evidencia
 */
export const deleteEvidence = async (workspaceId: number, evidenceId: number): Promise<void> => {
  await api.delete(`workspaces/${workspaceId}/evidence/${evidenceId}`)
}

// ============================================
// WORKSPACE LOGS API
// ============================================

export interface WorkspaceLog {
  id: number
  workspace_id: number
  source: string
  level: string
  message: string
  timestamp: string
  task_id?: string
  metadata?: Record<string, any>
}

export interface WorkspaceLogsResponse {
  logs: WorkspaceLog[]
  pagination: {
    page: number
    per_page: number
    total: number
    pages: number
    has_next: boolean
    has_prev: boolean
  }
  workspace_id: number
}

export interface WorkspaceLogsStats {
  workspace_id: number
  total_logs: number
  size_mb: number
  date_range: {
    first: string | null
    last: string | null
  }
  by_source: Record<string, number>
  by_level: Record<string, number>
}

export interface WorkspaceLogsFilters {
  limit?: number
  since?: string
  source?: string
  level?: string
  page?: number
  per_page?: number
}

/**
 * Obtiene logs históricos de un workspace
 */
export const getWorkspaceLogs = async (
  workspaceId: number,
  filters?: WorkspaceLogsFilters
): Promise<WorkspaceLogsResponse> => {
  const params = new URLSearchParams()
  if (filters?.limit) params.append('limit', filters.limit.toString())
  if (filters?.since) params.append('since', filters.since)
  if (filters?.source) params.append('source', filters.source)
  if (filters?.level) params.append('level', filters.level)
  if (filters?.page) params.append('page', filters.page.toString())
  if (filters?.per_page) params.append('per_page', filters.per_page.toString())

  const queryString = params.toString()
  const url = queryString
    ? `workspaces/${workspaceId}/logs?${queryString}`
    : `workspaces/${workspaceId}/logs`

  const response = await api.get<WorkspaceLogsResponse>(url)
  return response.data
}

/**
 * Obtiene estadísticas de logs de un workspace
 */
export const getWorkspaceLogsStats = async (workspaceId: number): Promise<WorkspaceLogsStats> => {
  const response = await api.get<WorkspaceLogsStats>(`workspaces/${workspaceId}/logs/stats`)
  return response.data
}

/**
 * Exporta logs de un workspace
 */
export const exportWorkspaceLogs = async (
  workspaceId: number,
  format: 'json' | 'txt' = 'json'
): Promise<Blob> => {
  const response = await api.get(`workspaces/${workspaceId}/logs/export?format=${format}`, {
    responseType: 'blob'
  })
  return response.data
}

/**
 * Elimina logs de un workspace
 */
export const deleteWorkspaceLogs = async (
  workspaceId: number,
  exportBeforeDelete: boolean = false
): Promise<{ message: string; deleted_count: number; export_url?: string }> => {
  const params = new URLSearchParams()
  if (exportBeforeDelete) params.append('export', 'true')

  const queryString = params.toString()
  const url = queryString
    ? `workspaces/${workspaceId}/logs?${queryString}`
    : `workspaces/${workspaceId}/logs`

  const response = await api.delete<{ message: string; deleted_count: number; export_url?: string }>(url)
  return response.data
}

/**
 * Archiva un workspace
 */
export const archiveWorkspace = async (
  workspaceId: number,
  options: {
    export_logs?: boolean
    keep_findings?: boolean
    keep_reports?: boolean
  }
): Promise<{ message: string; workspace_id: number; status: string; export_url?: string }> => {
  const response = await api.post<{
    message: string
    workspace_id: number
    status: string
    export_url?: string
  }>(`workspaces/${workspaceId}/archive`, options)
  return response.data
}

// ============================================
// WORKSPACE FILES API
// ============================================

export interface WorkspaceFile {
  name: string
  category: string
  path: string
  size: number
  size_human: string
  modified: string
  extension: string
  type: 'file' | 'directory'
  file_count?: number  // Solo para directorios
}

export interface WorkspaceDirectory {
  name: string
  category: string
  path: string
  modified: string
  type: 'directory'
  file_count: number
}

export interface WorkspaceFilesResponse {
  workspace_id: number
  workspace_name: string
  total_files: number
  total_directories: number
  current_path: string
  items: (WorkspaceFile | WorkspaceDirectory)[]
  files: WorkspaceFile[]  // Compatibilidad hacia atrás
  directories: WorkspaceDirectory[]
}

export interface WorkspaceFileContent {
  workspace_id: number
  file_path: string
  file_name: string
  size: number
  content: string | null
  is_binary: boolean
  message?: string
}

/**
 * Lista archivos generados en un workspace
 * @param workspaceId - ID del workspace
 * @param category - Categoría opcional (recon, scans, enumeration, etc.)
 * @param path - Path relativo opcional para navegar subdirectorios (ej: 'alquilersura.com.uy')
 * @returns Lista de archivos y directorios con metadatos
 */
export const getWorkspaceFiles = async (
  workspaceId: number,
  category?: string,
  path?: string
): Promise<WorkspaceFilesResponse> => {
  const params = new URLSearchParams()
  if (category) params.append('category', category)
  if (path) params.append('path', path)

  const queryString = params.toString()
  const url = queryString
    ? `workspaces/${workspaceId}/files?${queryString}`
    : `workspaces/${workspaceId}/files`

  const response = await api.get<WorkspaceFilesResponse>(url)
  return response.data
}

/**
 * Obtiene el contenido de un archivo del workspace
 * @param workspaceId - ID del workspace
 * @param filePath - Ruta relativa del archivo (ej: 'recon/amass_442.txt')
 * @param download - Si es true, descarga el archivo en lugar de leer contenido
 * @returns Contenido del archivo o Blob para descarga
 */
export const getWorkspaceFileContent = async (
  workspaceId: number,
  filePath: string,
  download: boolean = false
): Promise<WorkspaceFileContent | Blob> => {
  const params = new URLSearchParams()
  if (download) params.append('download', 'true')

  const queryString = params.toString()
  const url = queryString
    ? `workspaces/${workspaceId}/files/${filePath}?${queryString}`
    : `workspaces/${workspaceId}/files/${filePath}`

  if (download) {
    const response = await api.get(url, { responseType: 'blob' })
    return response.data
  } else {
    const response = await api.get<WorkspaceFileContent>(url)
    return response.data
  }
}

/**
 * Elimina un archivo específico del workspace
 * @param workspaceId - ID del workspace
 * @param filePath - Ruta relativa del archivo (ej: 'recon/amass_442.txt')
 * @returns Mensaje de confirmación
 */
export const deleteWorkspaceFile = async (
  workspaceId: number,
  filePath: string
): Promise<{ message: string; file_path: string }> => {
  const response = await api.delete(`workspaces/${workspaceId}/files/${filePath}`)
  return response.data
}

/**
 * Elimina todos los archivos del workspace (o de una categoría específica)
 * @param workspaceId - ID del workspace
 * @param category - Categoría opcional (si se especifica, solo elimina archivos de esa categoría)
 * @returns Mensaje de confirmación con estadísticas
 */
export const deleteAllWorkspaceFiles = async (
  workspaceId: number,
  category?: string
): Promise<{ message: string; deleted_files: number; deleted_directories: number; category: string }> => {
  const params = new URLSearchParams()
  if (category) params.append('category', category)

  const queryString = params.toString()
  const url = queryString
    ? `workspaces/${workspaceId}/files?${queryString}`
    : `workspaces/${workspaceId}/files`

  const response = await api.delete(url)
  return response.data
}

/**
 * Objeto API de workspaces - compatible hacia atrás
 * Agrupa todas las funciones de workspaces
 */
// ═══════════════════════════════════════════════════════════════════════
// DASHBOARD API
// ═══════════════════════════════════════════════════════════════════════

/**
 * Obtiene métricas generales del dashboard para un workspace
 */
export const getDashboardStats = async (workspaceId: number) => {
  const response = await api.get(`workspaces/${workspaceId}/dashboard/stats`)
  return response.data
}

/**
 * Obtiene distribución de vulnerabilidades por severidad
 */
export const getDashboardVulnerabilities = async (workspaceId: number) => {
  const response = await api.get(`workspaces/${workspaceId}/dashboard/vulnerabilities`)
  return response.data
}

/**
 * Obtiene timeline de scans (últimos 30 días)
 */
export const getDashboardTimeline = async (workspaceId: number) => {
  const response = await api.get(`workspaces/${workspaceId}/dashboard/timeline`)
  return response.data
}

/**
 * Obtiene tendencia de seguridad (últimos 30 días)
 */
export const getDashboardTrends = async (workspaceId: number) => {
  const response = await api.get(`workspaces/${workspaceId}/dashboard/trends`)
  return response.data
}

/**
 * Obtiene top 10 vulnerabilidades más frecuentes
 */
export const getDashboardTopVulnerabilities = async (workspaceId: number) => {
  const response = await api.get(`workspaces/${workspaceId}/dashboard/top-vulnerabilities`)
  return response.data
}

/**
 * Obtiene datos para la matriz de riesgo
 */
export const getDashboardRiskMatrix = async (workspaceId: number) => {
  const response = await api.get(`workspaces/${workspaceId}/dashboard/risk-matrix`)
  return response.data
}

export const workspacesAPI = {
  getWorkspaces,
  createWorkspace,
  updateWorkspace,
  deleteWorkspace,
  getWorkspaceSessions,
  createSession,
  getWorkspaceEvidence,
  createEvidence,
  updateEvidence,
  deleteEvidence,
  // Dashboard
  getDashboardStats,
  getDashboardVulnerabilities,
  getDashboardTimeline,
  getDashboardTrends,
  getDashboardTopVulnerabilities,
  getDashboardRiskMatrix,
  // Logs API
  getWorkspaceLogs,
  getWorkspaceLogsStats,
  exportWorkspaceLogs,
  deleteWorkspaceLogs,
  archiveWorkspace,
  // Files API
  getWorkspaceFiles,
  getWorkspaceFileContent,
  deleteWorkspaceFile,
  deleteAllWorkspaceFiles
}

