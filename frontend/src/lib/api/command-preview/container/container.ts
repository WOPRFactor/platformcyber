import { api } from '../../shared/client'
import { CommandPreview } from '../../../../components/CommandPreviewModal'

export const previewContainerAPI = {
  previewTrivyScan: async (data: {
    image: string
    workspace_id: number
    severity?: string[]
  }): Promise<CommandPreview> => {
    const response = await api.post('/container/trivy/image/preview', data)
    return response.data
  },

  previewGrypeScan: async (data: {
    image: string
    workspace_id: number
    scope?: string
  }): Promise<CommandPreview> => {
    const response = await api.post('/container/grype/image/preview', data)
    return response.data
  },

  previewSyftSBOM: async (data: {
    image: string
    workspace_id: number
    output_format?: string
  }): Promise<CommandPreview> => {
    const response = await api.post('/container/syft/sbom/preview', data)
    return response.data
  },

  previewKubeHunter: async (data: {
    workspace_id: number
    mode?: string
    remote_host?: string
  }): Promise<CommandPreview> => {
    const response = await api.post('/container/kube-hunter/scan/preview', data)
    return response.data
  },

  previewKubeBench: async (data: {
    workspace_id: number
    targets?: string[]
  }): Promise<CommandPreview> => {
    const response = await api.post('/container/kube-bench/run/preview', data)
    return response.data
  },

  previewKubescape: async (data: {
    workspace_id: number
    framework?: string
    namespace?: string
  }): Promise<CommandPreview> => {
    const response = await api.post('/container/kubescape/scan/preview', data)
    return response.data
  }
}

