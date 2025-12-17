import { api } from '../shared/client'

export interface ADScanResponse {
  scan_id: number
  status: string
  tool: string
  action?: string
  domain?: string
  message?: string
}

export interface ADScanStatus {
  scan_id: number
  status: string
  progress: number
  target: string
  tool?: string
  action?: string
  started_at?: string
  completed_at?: string
}

export interface ADScanResults {
  scan_id: number
  status: string
  tool: string
  action?: string
  results: any
  scan_info?: {
    target: string
    started_at?: string
    completed_at?: string
  }
}

const activeDirectoryAPI = {
  // Kerbrute - User Enumeration
  startKerbruteUserEnum: async (
    domain: string,
    dcIp: string,
    userlist: string,
    workspaceId: number
  ): Promise<ADScanResponse> => {
    const response = await api.post('/active-directory/kerbrute/userenum', {
      domain,
      dc_ip: dcIp,
      userlist,
      workspace_id: workspaceId
    })
    return response.data
  },

  // Kerbrute - Password Spraying
  startKerbrutePasswordSpray: async (
    domain: string,
    dcIp: string,
    userlist: string,
    password: string,
    workspaceId: number
  ): Promise<ADScanResponse> => {
    const response = await api.post('/active-directory/kerbrute/passwordspray', {
      domain,
      dc_ip: dcIp,
      userlist,
      password,
      workspace_id: workspaceId
    })
    return response.data
  },

  // GetNPUsers (AS-REP Roasting)
  startGetNPUsers: async (
    domain: string,
    workspaceId: number,
    username?: string,
    password?: string,
    dcIp?: string,
    usersfile?: string,
    noPass?: boolean
  ): Promise<ADScanResponse> => {
    const response = await api.post('/active-directory/asreproast', {
      domain,
      workspace_id: workspaceId,
      username,
      password,
      dc_ip: dcIp,
      usersfile,
      no_pass: noPass
    })
    return response.data
  },

  // LDAP Domain Dump
  startLDAPDomainDump: async (
    dcIp: string,
    username: string,
    password: string,
    domain: string,
    workspaceId: number
  ): Promise<ADScanResponse> => {
    const response = await api.post('/active-directory/ldap/dump', {
      dc_ip: dcIp,
      username,
      password,
      domain,
      workspace_id: workspaceId
    })
    return response.data
  },

  // ADIDNS Dump
  startADIDNSDump: async (
    dcIp: string,
    username: string,
    password: string,
    domain: string,
    workspaceId: number
  ): Promise<ADScanResponse> => {
    const response = await api.post('/active-directory/dns/dump', {
      dc_ip: dcIp,
      username,
      password,
      domain,
      workspace_id: workspaceId
    })
    return response.data
  },

  // CrackMapExec - Enum Users
  startCMEEnumUsers: async (
    dcIp: string,
    username: string,
    password: string,
    domain: string,
    workspaceId: number
  ): Promise<ADScanResponse> => {
    const response = await api.post('/active-directory/cme/enum/users', {
      dc_ip: dcIp,
      username,
      password,
      domain,
      workspace_id: workspaceId
    })
    return response.data
  },

  // CrackMapExec - Enum Groups
  startCMEEnumGroups: async (
    dcIp: string,
    username: string,
    password: string,
    domain: string,
    workspaceId: number
  ): Promise<ADScanResponse> => {
    const response = await api.post('/active-directory/cme/enum/groups', {
      dc_ip: dcIp,
      username,
      password,
      domain,
      workspace_id: workspaceId
    })
    return response.data
  },

  // Obtener resultados
  getScanResults: async (scanId: number): Promise<ADScanResults> => {
    const response = await api.get(`/active-directory/scan/${scanId}/results`)
    return response.data
  },

  // Obtener estado
  getScanStatus: async (scanId: number): Promise<ADScanStatus> => {
    const response = await api.get(`/active-directory/scan/${scanId}`)
    return response.data
  },

  // Listar scans
  getScans: async (workspaceId: number): Promise<{ scans: ADScanStatus[], total: number }> => {
    const response = await api.get('/active-directory/scans', {
      params: { workspace_id: workspaceId }
    })
    return response.data
  }
}

export default activeDirectoryAPI

