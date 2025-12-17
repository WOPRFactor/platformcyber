/**
 * OWASP API Client
 */
import { api } from '../shared/client'
import type {
  OwaspCategory,
  OwaspAudit,
  CreateAuditData,
  UpdateProgressData,
  AddFindingData,
  ApiResponse
} from './types'

const BASE_URL = '/owasp'

export const owaspAPI = {
  /**
   * Get all OWASP Top 10 categories
   */
  getCategories: async (): Promise<Record<string, OwaspCategory>> => {
    const response = await api.get<{ categories: Record<string, OwaspCategory> }>(
      `${BASE_URL}/categories`
    )
    console.log('📦 Respuesta de categorías OWASP:', response.data)
    return response.data.categories || response.data
  },

  /**
   * Get specific category
   */
  getCategory: async (categoryId: string): Promise<OwaspCategory> => {
    const response = await api.get<{ category: OwaspCategory }>(
      `${BASE_URL}/categories/${categoryId}`
    )
    return response.data.category
  },

  /**
   * List audits
   */
  listAudits: async (filters?: {
    workspace_id?: number
    status?: string
  }): Promise<OwaspAudit[]> => {
    const params = new URLSearchParams()
    if (filters?.workspace_id) params.append('workspace_id', filters.workspace_id.toString())
    if (filters?.status) params.append('status', filters.status)

    const url = params.toString()
      ? `${BASE_URL}/audits?${params.toString()}`
      : `${BASE_URL}/audits`

    const response = await api.get<{ audits: OwaspAudit[]; total: number }>(url)
    return response.data.audits
  },

  /**
   * Create new audit
   */
  createAudit: async (auditData: CreateAuditData): Promise<ApiResponse> => {
    const response = await api.post<ApiResponse>(
      `${BASE_URL}/audits`,
      auditData
    )
    return response.data
  },

  /**
   * Get specific audit
   */
  getAudit: async (auditId: string): Promise<OwaspAudit> => {
    const response = await api.get<OwaspAudit>(
      `${BASE_URL}/audits/${auditId}`
    )
    return response.data
  },

  /**
   * Delete audit
   */
  deleteAudit: async (auditId: string): Promise<ApiResponse> => {
    const response = await api.delete<ApiResponse>(
      `${BASE_URL}/audits/${auditId}`
    )
    return response.data
  },

  /**
   * Update audit progress
   */
  updateProgress: async (
    auditId: string,
    progressData: UpdateProgressData
  ): Promise<ApiResponse> => {
    const response = await api.put<ApiResponse>(
      `${BASE_URL}/audits/${auditId}/progress`,
      progressData
    )
    return response.data
  },

  /**
   * Add finding to audit
   */
  addFinding: async (
    auditId: string,
    findingData: AddFindingData
  ): Promise<ApiResponse> => {
    const response = await api.post<ApiResponse>(
      `${BASE_URL}/audits/${auditId}/findings`,
      findingData
    )
    return response.data
  },

  /**
   * Simulate audit execution (for testing)
   */
  simulateAudit: async (auditId: string): Promise<ApiResponse> => {
    const response = await api.post<ApiResponse>(
      `${BASE_URL}/audits/${auditId}/simulate`
    )
    return response.data
  },

  /**
   * Start audit (compatibility method)
   */
  startAudit: async (target: string, workspaceId: number = 1): Promise<ApiResponse> => {
    return owaspAPI.createAudit({
      target,
      workspace_id: workspaceId
    })
  },

  /**
   * Preview audit (without executing)
   */
  previewAudit: async (auditData: CreateAuditData): Promise<any> => {
    const response = await api.post<any>(
      `${BASE_URL}/audits/preview`,
      auditData
    )
    return response.data
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string; service: string; version: string }> => {
    const response = await api.get(`${BASE_URL}/health`)
    return response.data
  }
}
