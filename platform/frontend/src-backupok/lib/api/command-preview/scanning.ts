/**
 * Scanning Command Previews
 * ==========================
 * 
 * Previews de comandos de escaneo.
 */

import { api } from '../shared/client'
import { PreviewRequest, CommandPreviewResponse } from './types'

export const scanningPreviews = {
  previewNmapScan: async (params: PreviewRequest & {
    target: string
    scan_type?: string
    ports?: string
    scripts?: string[]
    os_detection?: boolean
    version_detection?: boolean
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/nmap/preview',
      params
    )
    return response.data
  },

  previewRustScan: async (params: PreviewRequest & {
    target: string
    batch_size?: number
    timeout?: number
    ulimit?: number
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/rustscan/preview',
      params
    )
    return response.data
  },

  previewRustscan: async (params: PreviewRequest & {
    target: string
    batch_size?: number
    timeout?: number
    ulimit?: number
  }): Promise<CommandPreviewResponse> => {
    // Alias para compatibilidad (camelCase)
    const response = await api.post<CommandPreviewResponse>(
      'scanning/rustscan/preview',
      params
    )
    return response.data
  },

  previewMasscan: async (params: PreviewRequest & {
    target: string
    ports?: string
    rate?: number
    environment?: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/masscan/preview',
      params
    )
    return response.data
  },

  previewNaabu: async (params: PreviewRequest & {
    target: string
    top_ports?: number
    rate?: number
    verify?: boolean
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/naabu/preview',
      params
    )
    return response.data
  },

  previewEnum4linux: async (params: PreviewRequest & {
    target: string
    use_ng?: boolean
    all?: boolean
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/smb/enum4linux/preview',
      params
    )
    return response.data
  },

  previewSmbmap: async (params: PreviewRequest & {
    target: string
    username?: string
    password?: string
    hash?: string
    recursive?: boolean
    share?: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/smb/smbmap/preview',
      params
    )
    return response.data
  },

  previewFtpEnum: async (params: PreviewRequest & {
    target: string
    port?: number
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/ftp/preview',
      params
    )
    return response.data
  },

  previewDnsEnum: async (params: PreviewRequest & {
    target: string
    domain?: string
    tool?: string
    port?: number
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/dns/preview',
      params
    )
    return response.data
  },

  previewRdpEnum: async (params: PreviewRequest & {
    target: string
    port?: number
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/rdp/preview',
      params
    )
    return response.data
  },

  previewSmbclient: async (params: PreviewRequest & {
    target: string
    share?: string
    username?: string
    password?: string
    port?: number
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/smb/smbclient/preview',
      params
    )
    return response.data
  },

  previewSshEnum: async (params: PreviewRequest & {
    target: string
    tool?: string
    port?: number
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/ssh/preview',
      params
    )
    return response.data
  },

  previewSmtpEnum: async (params: PreviewRequest & {
    target: string
    tool?: string
    port?: number
    userlist?: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/smtp/preview',
      params
    )
    return response.data
  },

  previewSnmpEnum: async (params: PreviewRequest & {
    target: string
    tool?: string
    port?: number
    community?: string
    community_file?: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/snmp/preview',
      params
    )
    return response.data
  },

  previewLdapEnum: async (params: PreviewRequest & {
    target: string
    tool?: string
    port?: number
    base_dn?: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/ldap/preview',
      params
    )
    return response.data
  },

  previewMysqlEnum: async (params: PreviewRequest & {
    target: string
    tool?: string
    port?: number
    username?: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/mysql/preview',
      params
    )
    return response.data
  },

  previewPostgresqlEnum: async (params: PreviewRequest & {
    target: string
    tool?: string
    port?: number
    username?: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/postgresql/preview',
      params
    )
    return response.data
  },

  previewRedisEnum: async (params: PreviewRequest & {
    target: string
    tool?: string
    port?: number
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/redis/preview',
      params
    )
    return response.data
  },

  previewMongodbEnum: async (params: PreviewRequest & {
    target: string
    port?: number
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/mongodb/preview',
      params
    )
    return response.data
  },

  previewSslscan: async (params: PreviewRequest & {
    target: string
    port?: number
    show_certificate?: boolean
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/ssl/sslscan/preview',
      params
    )
    return response.data
  },

  previewSslyze: async (params: PreviewRequest & {
    target: string
    port?: number
    regular?: boolean
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'scanning/enum/ssl/sslyze/preview',
      params
    )
    return response.data
  }
}

