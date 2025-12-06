/**
 * MITRE ATT&CK API Client
 */
import { api } from '../shared/client'
import type {
  MitreTactic,
  MitreTechnique,
  MitreCampaign,
  CreateCampaignData,
  ExecuteTechniqueData,
  CoverageMatrix,
  KillChain,
  MitreStats,
  ApiResponse
} from './types'

const BASE_URL = '/mitre'

export const mitreAPI = {
  /**
   * Get all MITRE ATT&CK tactics
   */
  getTactics: async (): Promise<Record<string, MitreTactic>> => {
    const response = await api.get<{ tactics: Record<string, MitreTactic> }>(
      `${BASE_URL}/tactics`
    )
    return response.data.tactics
  },

  /**
   * Get specific tactic
   */
  getTactic: async (tacticId: string): Promise<MitreTactic> => {
    const response = await api.get<{ tactic: MitreTactic }>(
      `${BASE_URL}/tactics/${tacticId}`
    )
    return response.data.tactic
  },

  /**
   * Get techniques (optionally filtered by tactic)
   */
  getTechniques: async (tacticFilter?: string): Promise<Record<string, MitreTechnique>> => {
    const params = tacticFilter ? `?tactic=${tacticFilter}` : ''
    const response = await api.get<{ techniques: Record<string, MitreTechnique>; total: number }>(
      `${BASE_URL}/techniques${params}`
    )
    return response.data.techniques
  },

  /**
   * Get specific technique
   */
  getTechnique: async (techniqueId: string): Promise<MitreTechnique> => {
    const response = await api.get<{ technique: MitreTechnique }>(
      `${BASE_URL}/techniques/${techniqueId}`
    )
    return response.data.technique
  },

  /**
   * Create simulation campaign
   */
  createCampaign: async (campaignData: CreateCampaignData): Promise<ApiResponse> => {
    const response = await api.post<ApiResponse>(
      `${BASE_URL}/campaigns`,
      campaignData
    )
    return response.data
  },

  /**
   * List campaigns
   */
  listCampaigns: async (workspaceId?: number): Promise<MitreCampaign[]> => {
    const params = workspaceId ? `?workspace_id=${workspaceId}` : ''
    const response = await api.get<{ campaigns: MitreCampaign[]; total: number }>(
      `${BASE_URL}/campaigns${params}`
    )
    return response.data.campaigns
  },

  /**
   * Get campaign details
   */
  getCampaign: async (campaignId: string): Promise<MitreCampaign> => {
    const response = await api.get<MitreCampaign>(
      `${BASE_URL}/campaigns/${campaignId}`
    )
    return response.data
  },

  /**
   * Execute technique in campaign
   */
  executeTechnique: async (
    campaignId: string,
    executeData: ExecuteTechniqueData
  ): Promise<ApiResponse> => {
    const response = await api.post<ApiResponse>(
      `${BASE_URL}/campaigns/${campaignId}/execute`,
      executeData
    )
    return response.data
  },

  /**
   * Get detection coverage matrix
   */
  getCoverage: async (): Promise<CoverageMatrix> => {
    const response = await api.get<CoverageMatrix>(
      `${BASE_URL}/coverage`
    )
    return response.data
  },

  /**
   * Get kill chains
   */
  getKillChains: async (): Promise<Record<string, KillChain>> => {
    const response = await api.get<{ kill_chains: Record<string, KillChain> }>(
      `${BASE_URL}/kill-chains`
    )
    return response.data.kill_chains
  },

  /**
   * Get specific kill chain
   */
  getKillChain: async (chainId: string): Promise<KillChain> => {
    const response = await api.get<{ kill_chain: KillChain }>(
      `${BASE_URL}/kill-chains/${chainId}`
    )
    return response.data.kill_chain
  },

  /**
   * Get MITRE stats
   */
  getStats: async (): Promise<MitreStats> => {
    const response = await api.get<MitreStats>(
      `${BASE_URL}/stats`
    )
    return response.data
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{
    status: string
    service: string
    version: string
    framework: string
  }> => {
    const response = await api.get(`${BASE_URL}/health`)
    return response.data
  }
}
