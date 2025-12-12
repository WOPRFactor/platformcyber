/**
 * Integrations API
 * ===============
 * 
 * API client para integraciones avanzadas:
 * - Metasploit Framework
 * - Burp Suite Professional
 * - Nmap Advanced
 * - SQLMap
 * - Gobuster
 */

import { api } from '../shared/client'

export const integrationsAPI = {
  // Metasploit
  checkMetasploitStatus: () => api.get('/integrations/metasploit/status').then(r => r.data),
  listMetasploitModules: (moduleType?: string) => 
    api.get('/integrations/metasploit/modules', { params: { type: moduleType } }).then(r => r.data),
  executeMetasploitExploit: (data: any) => 
    api.post('/integrations/metasploit/exploit', data).then(r => r.data),
  getMetasploitSessions: () => 
    api.get('/integrations/metasploit/sessions').then(r => r.data),
  interactMetasploitSession: (sessionId: string, command: string) => 
    api.post(`/integrations/metasploit/sessions/${sessionId}/interact`, { command }).then(r => r.data),

  // Burp Suite
  checkBurpStatus: () => api.get('/integrations/burp/status').then(r => r.data),
  startBurpScan: (url: string, workspaceId: number) => 
    api.post('/integrations/burp/scan', { url, workspace_id: workspaceId }).then(r => r.data),
  getBurpScanStatus: (scanId: string) => 
    api.get(`/integrations/burp/scan/${scanId}/status`).then(r => r.data),
  getBurpScanResults: (scanId: string) => 
    api.get(`/integrations/burp/scan/${scanId}/results`).then(r => r.data),

  // Nmap Advanced
  advancedNmapScan: (target: string, scanType: string, workspaceId: number, options?: any) => 
    api.post('/integrations/nmap/advanced', { 
      target, 
      options: { scan_type: scanType, ...options },
      workspace_id: workspaceId 
    }).then(r => r.data),
  getNmapResults: (sessionId: string) => 
    api.get(`/integrations/nmap/results/${sessionId}`).then(r => r.data),

  // SQLMap
  advancedSQLMapScan: (url: string, workspaceId: number, options?: any) => 
    api.post('/integrations/sqlmap/scan', { url, workspace_id: workspaceId, options: options || {} }).then(r => r.data),
  getSQLMapResults: (sessionId: string) => 
    api.get(`/integrations/sqlmap/results/${sessionId}`).then(r => r.data),

  // Gobuster
  directoryBusting: (url: string, wordlist: string, workspaceId: number, options?: any) => 
    api.post('/integrations/gobuster/directory', { url, wordlist, workspace_id: workspaceId, options: options || {} }).then(r => r.data),
  getGobusterResults: (sessionId: string) => 
    api.get(`/integrations/gobuster/results/${sessionId}`).then(r => r.data),

  // Historial de sesiones
  getIntegrationSessions: () => 
    api.get('/integrations/sessions').then(r => r.data),
  getSessionDetails: (sessionId: string) => 
    api.get(`/integrations/sessions/${sessionId}`).then(r => r.data),

  // Previews
  previewMetasploitExploit: (exploit: string, options: any, workspaceId: number) =>
    api.post('/integrations/metasploit/exploit/preview', { exploit, options, workspace_id: workspaceId }).then(r => r.data),
  previewBurpScan: (url: string, workspaceId: number) =>
    api.post('/integrations/burp/scan/preview', { url, workspace_id: workspaceId }).then(r => r.data),
  previewNmapScan: (target: string, scanType: string, workspaceId: number, options?: any) =>
    api.post('/integrations/nmap/advanced/preview', { target, options: { scan_type: scanType, ...options }, workspace_id: workspaceId }).then(r => r.data),
  previewSQLMapScan: (url: string, workspaceId: number, options?: any) =>
    api.post('/integrations/sqlmap/scan/preview', { url, options: options || {}, workspace_id: workspaceId }).then(r => r.data),
  previewGobusterDirectory: (url: string, wordlist: string, workspaceId: number, options?: any) =>
    api.post('/integrations/gobuster/directory/preview', { url, wordlist, options: options || {}, workspace_id: workspaceId }).then(r => r.data)
}

