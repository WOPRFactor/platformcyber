import { api } from '../shared/client'

export interface CloudScanResponse {
  scan_id: number
  status: string
  tool: string
  provider?: string
  module?: string
  message?: string
}

export interface CloudScanStatus {
  scan_id: number
  status: string
  progress: number
  target: string
  tool?: string
  provider?: string
  started_at?: string
  completed_at?: string
}

export interface CloudScanResults {
  scan_id: number
  status: string
  tool: string
  provider?: string
  results: any
  scan_info: {
    target: string
    started_at?: string
    completed_at?: string
  }
}

const cloudAPI = {
  // Pacu
  startPacuModule: async (
    moduleName: string,
    workspaceId: number,
    awsProfile?: string,
    moduleArgs?: Record<string, any>
  ): Promise<CloudScanResponse> => {
    const response = await api.post('/cloud/pacu/module', {
      module_name: moduleName,
      workspace_id: workspaceId,
      aws_profile: awsProfile,
      module_args: moduleArgs
    })
    return response.data
  },

  // ScoutSuite
  startScoutSuiteScan: async (
    provider: string,
    workspaceId: number,
    profile?: string,
    regions?: string[],
    services?: string[]
  ): Promise<CloudScanResponse> => {
    const response = await apiClient.post('/cloud/scoutsuite/scan', {
      provider,
      workspace_id: workspaceId,
      profile,
      regions,
      services
    })
    return response.data
  },

  // Prowler
  startProwlerScan: async (
    provider: string,
    workspaceId: number,
    profile?: string,
    severity?: string[],
    compliance?: string,
    services?: string[]
  ): Promise<CloudScanResponse> => {
    const response = await apiClient.post('/cloud/prowler/scan', {
      provider,
      workspace_id: workspaceId,
      profile,
      severity,
      compliance,
      services
    })
    return response.data
  },

  // AzureHound
  startAzureHoundCollection: async (
    tenantId: string,
    workspaceId: number,
    username?: string,
    password?: string,
    accessToken?: string
  ): Promise<CloudScanResponse> => {
    const response = await apiClient.post('/cloud/azurehound/collect', {
      tenant_id: tenantId,
      workspace_id: workspaceId,
      username,
      password,
      access_token: accessToken
    })
    return response.data
  },

  // ROADtools
  startROADtoolsGather: async (
    workspaceId: number,
    username?: string,
    password?: string,
    accessToken?: string,
    tenantId?: string
  ): Promise<CloudScanResponse> => {
    const response = await apiClient.post('/cloud/roadtools/gather', {
      workspace_id: workspaceId,
      username,
      password,
      access_token: accessToken,
      tenant_id: tenantId
    })
    return response.data
  },

  // Obtener resultados
  getScanResults: async (scanId: number): Promise<CloudScanResults> => {
    const response = await api.get(`/cloud/scan/${scanId}/results`)
    return response.data
  },

  // Obtener estado
  getScanStatus: async (scanId: number): Promise<CloudScanStatus> => {
    const response = await api.get(`/cloud/scan/${scanId}`)
    return response.data
  },

  // Listar scans
  getScans: async (workspaceId: number, provider?: string): Promise<{ scans: CloudScanStatus[], total: number }> => {
    const response = await api.get('/cloud/scans', {
      params: { workspace_id: workspaceId, provider }
    })
    return response.data
  },

  // Listar proveedores
  getProviders: async (): Promise<any> => {
    const response = await api.get('/cloud/providers')
    return response.data
  },

  // Listar módulos Pacu
  getPacuModules: async (): Promise<any> => {
    const response = await api.get('/cloud/pacu/modules')
    return response.data
  }
}

export default cloudAPI

