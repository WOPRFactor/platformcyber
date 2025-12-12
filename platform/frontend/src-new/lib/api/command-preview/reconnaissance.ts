/**
 * Reconnaissance Command Previews
 * ================================
 * 
 * Previews de comandos de reconocimiento.
 */

import { api } from '../shared/client'
import { PreviewRequest, CommandPreviewResponse } from './types'

export const reconnaissancePreviews = {
  previewSubdomainEnum: async (params: PreviewRequest & {
    domain: string
    tool?: string
    passive_only?: boolean
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/subdomains/preview',
      params
    )
    return response.data
  },

  previewWhois: async (params: PreviewRequest & {
    target: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/whois/preview',
      params
    )
    return response.data
  },

  previewDnsRecon: async (params: PreviewRequest & {
    domain: string
    record_types?: string[]
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/dns/preview',
      params
    )
    return response.data
  },

  previewShodan: async (params: PreviewRequest & {
    query: string
    facets?: string[]
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/shodan/preview',
      params
    )
    return response.data
  },

  previewCensys: async (params: PreviewRequest & {
    query: string
    index?: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/censys/preview',
      params
    )
    return response.data
  },

  previewTheHarvester: async (params: PreviewRequest & {
    domain: string
    sources?: string[]
    limit?: number
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/theharvester/preview',
      params
    )
    return response.data
  },

  previewGobuster: async (params: PreviewRequest & {
    target: string
    wordlist?: string
    extensions?: string[]
    statusCodes?: string[]
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/gobuster/preview',
      params
    )
    return response.data
  },

  previewDirb: async (params: PreviewRequest & {
    target: string
    wordlist?: string
    extensions?: string[]
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/dirb/preview',
      params
    )
    return response.data
  },

  previewWfuzz: async (params: PreviewRequest & {
    target: string
    wordlist?: string
    payloads?: string[]
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/wfuzz/preview',
      params
    )
    return response.data
  },

  previewGitLeaks: async (params: PreviewRequest & {
    target: string
    repo?: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/gitleaks/preview',
      params
    )
    return response.data
  },

  previewTruffleHog: async (params: PreviewRequest & {
    target: string
    repo?: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/trufflehog/preview',
      params
    )
    return response.data
  },

  previewCrtsh: async (params: PreviewRequest & {
    domain: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/crtsh/preview',
      params
    )
    return response.data
  },

  previewFindomain: async (params: PreviewRequest & {
    domain: string
    resolvers_file?: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/findomain/preview',
      params
    )
    return response.data
  },

  previewDnsLookup: async (params: PreviewRequest & {
    domain: string
    tool?: string
    record_type?: string
    dns_server?: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/dns-lookup/preview',
      params
    )
    return response.data
  },

  previewDnsEnumAlt: async (params: PreviewRequest & {
    domain: string
    tool?: string
    wordlist?: string
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/dns-enum-alt/preview',
      params
    )
    return response.data
  },

  previewTraceroute: async (params: PreviewRequest & {
    target: string
    protocol?: string
    max_hops?: number
  }): Promise<CommandPreviewResponse> => {
    const response = await api.post<CommandPreviewResponse>(
      'reconnaissance/traceroute/preview',
      params
    )
    return response.data
  }
}

