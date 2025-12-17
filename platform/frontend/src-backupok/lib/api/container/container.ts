import { api } from '../shared/client'

export interface ContainerScanResponse {
  scan_id: number
  status: string
  tool: string
  target?: string
  message?: string
}

export interface ContainerScanStatus {
  scan_id: number
  status: string
  progress: number
  target: string
  tool?: string
  started_at?: string
  completed_at?: string
}

export interface ContainerScanResults {
  scan_id: number
  status: string
  tool: string
  results: any
  scan_info: {
    target: string
    started_at?: string
    completed_at?: string
  }
}

const containerAPI = {
  // Trivy
  scanImageTrivy: async (
    image: string,
    workspaceId: number,
    severity?: string[]
  ): Promise<ContainerScanResponse> => {
    const response = await api.post('/container/trivy/image', {
      image,
      workspace_id: workspaceId,
      severity
    })
    return response.data
  },

  // Grype
  scanImageGrype: async (
    image: string,
    workspaceId: number,
    scope?: string
  ): Promise<ContainerScanResponse> => {
    const response = await api.post('/container/grype/image', {
      image,
      workspace_id: workspaceId,
      scope
    })
    return response.data
  },

  // Syft
  generateSBOM: async (
    image: string,
    workspaceId: number,
    outputFormat?: string
  ): Promise<ContainerScanResponse> => {
    const response = await api.post('/container/syft/sbom', {
      image,
      workspace_id: workspaceId,
      output_format: outputFormat
    })
    return response.data
  },

  // Kube-hunter
  runKubeHunter: async (
    workspaceId: number,
    mode?: string,
    remoteHost?: string
  ): Promise<ContainerScanResponse> => {
    const response = await api.post('/container/kube-hunter/scan', {
      workspace_id: workspaceId,
      mode,
      remote_host: remoteHost
    })
    return response.data
  },

  // Kube-bench
  runKubeBench: async (
    workspaceId: number,
    targets?: string[]
  ): Promise<ContainerScanResponse> => {
    const response = await api.post('/container/kube-bench/run', {
      workspace_id: workspaceId,
      targets
    })
    return response.data
  },

  // Kubescape
  runKubescape: async (
    workspaceId: number,
    framework?: string,
    namespace?: string
  ): Promise<ContainerScanResponse> => {
    const response = await api.post('/container/kubescape/scan', {
      workspace_id: workspaceId,
      framework,
      namespace
    })
    return response.data
  },

  // Obtener resultados
  getScanResults: async (scanId: number): Promise<ContainerScanResults> => {
    const response = await api.get(`/container/scan/${scanId}/results`)
    return response.data
  },

  // Obtener estado
  getScanStatus: async (scanId: number): Promise<ContainerScanStatus> => {
    const response = await api.get(`/container/scan/${scanId}`)
    return response.data
  },

  // Listar scans
  getScans: async (workspaceId: number): Promise<{ scans: ContainerScanStatus[], total: number }> => {
    const response = await api.get('/container/scans', {
      params: { workspace_id: workspaceId }
    })
    return response.data
  },

  // Listar herramientas
  getTools: async (): Promise<any> => {
    const response = await api.get('/container/tools')
    return response.data
  }
}

export default containerAPI

