import { api } from '../../shared/client'
import { CommandPreview } from '../../../../components/CommandPreviewModal'

export const previewActiveDirectoryAPI = {
  previewKerbruteUserEnum: async (data: {
    domain: string
    dc_ip: string
    userlist: string
    workspace_id: number
  }): Promise<CommandPreview> => {
    const response = await api.post('/active-directory/kerbrute/userenum/preview', data)
    return response.data
  },

  previewKerbrutePasswordSpray: async (data: {
    domain: string
    dc_ip: string
    userlist: string
    password: string
    workspace_id: number
  }): Promise<CommandPreview> => {
    const response = await api.post('/active-directory/kerbrute/passwordspray/preview', data)
    return response.data
  },

  previewGetNPUsers: async (data: {
    domain: string
    workspace_id: number
    username?: string
    password?: string
    dc_ip?: string
    usersfile?: string
    no_pass?: boolean
  }): Promise<CommandPreview> => {
    const response = await api.post('/active-directory/asreproast/preview', data)
    return response.data
  },

  previewLDAPDomainDump: async (data: {
    dc_ip: string
    username: string
    password: string
    domain: string
    workspace_id: number
  }): Promise<CommandPreview> => {
    const response = await api.post('/active-directory/ldap/dump/preview', data)
    return response.data
  },

  previewADIDNSDump: async (data: {
    dc_ip: string
    username: string
    password: string
    domain: string
    workspace_id: number
  }): Promise<CommandPreview> => {
    const response = await api.post('/active-directory/dns/dump/preview', data)
    return response.data
  },

  previewCMEEnumUsers: async (data: {
    dc_ip: string
    username: string
    password: string
    domain: string
    workspace_id: number
  }): Promise<CommandPreview> => {
    const response = await api.post('/active-directory/cme/enum/users/preview', data)
    return response.data
  },

  previewCMEEnumGroups: async (data: {
    dc_ip: string
    username: string
    password: string
    domain: string
    workspace_id: number
  }): Promise<CommandPreview> => {
    const response = await api.post('/active-directory/cme/enum/groups/preview', data)
    return response.data
  }
}

