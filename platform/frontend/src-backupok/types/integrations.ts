/**
 * Integrations Types
 * ==================
 * 
 * Tipos relacionados con integraciones de herramientas externas.
 */

export interface MetasploitStatus {
  connected: boolean
  version?: string
  modules_loaded?: number
  error?: string
}

export interface MetasploitModules {
  exploits: string[]
  auxiliaries: string[]
  payloads: string[]
}

export interface MetasploitExploitResult {
  success: boolean
  session_id?: string
  output?: string
  error?: string
}

export interface MetasploitExploitOptions {
  exploit: string
  payload: string
  options: Record<string, any>
}

export interface BurpScanOptions {
  url: string
  scan_type: 'passive' | 'active' | 'full'
  scope?: string[]
}

export interface BurpStatus {
  running: boolean
  version?: string
  port?: number
  error?: string
}

export interface BurpScanResult {
  scan_id: string
  status: string
  issues_found?: number
  error?: string
}

export interface BurpScanStatus {
  scan_id: string
  status: string
  progress?: number
  issues_found?: number
  error?: string
}

export interface AdvancedNmapResult {
  target: string
  ports: any[]
  services: any[]
  os_detection?: any
  vulnerabilities?: any[]
}

export interface AdvancedSQLMapResult {
  target: string
  databases?: string[]
  tables?: any[]
  columns?: any[]
  data?: any[]
  vulnerabilities?: any[]
}

export interface DirectoryBustingResult {
  target: string
  directories_found: string[]
  files_found: string[]
  total_requests: number
  response_time: number
}

export interface NmapFinding {
  port: number
  state: string
  service: string
  version?: string
  vulnerability?: string
}

export interface DirectoryResult {
  path: string
  status: number
  size?: number
  type: 'directory' | 'file'
}

export interface IntegrationSession {
  id: number
  session_id: string
  target: string
  scan_type: string
  created_at: string
  status: string
}


