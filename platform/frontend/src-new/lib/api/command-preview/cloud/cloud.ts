import { api } from '../../shared/client'
import { CommandPreview } from '../../../../components/CommandPreviewModal'

export const previewCloudAPI = {
  previewPacuModule: async (data: {
    module_name: string
    workspace_id: number
    aws_profile?: string
    module_args?: Record<string, any>
  }): Promise<CommandPreview> => {
    const response = await api.post('/cloud/pacu/module/preview', data)
    return response.data
  },

  previewScoutSuiteScan: async (data: {
    provider: string
    workspace_id: number
    profile?: string
    regions?: string[]
    services?: string[]
  }): Promise<CommandPreview> => {
    const response = await api.post('/cloud/scoutsuite/scan/preview', data)
    return response.data
  },

  previewProwlerScan: async (data: {
    provider: string
    workspace_id: number
    profile?: string
    severity?: string[]
    compliance?: string
    services?: string[]
  }): Promise<CommandPreview> => {
    const response = await api.post('/cloud/prowler/scan/preview', data)
    return response.data
  },

  previewAzureHoundCollection: async (data: {
    tenant_id: string
    workspace_id: number
    username?: string
    password?: string
    access_token?: string
  }): Promise<CommandPreview> => {
    const response = await api.post('/cloud/azurehound/collect/preview', data)
    return response.data
  },

  previewROADtoolsGather: async (data: {
    workspace_id: number
    username?: string
    password?: string
    access_token?: string
    tenant_id?: string
  }): Promise<CommandPreview> => {
    const response = await api.post('/cloud/roadtools/gather/preview', data)
    return response.data
  }
}

