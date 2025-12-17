/**
 * Types for OWASP API
 */

export interface OwaspCategory {
  name: string
  description: string
  tests: string[]
}

export interface OwaspVulnerabilities {
  a01_access_control: number
  a02_crypto_failures: number
  a03_injection: number
  a04_insecure_design: number
  a05_misconfig: number
  a06_vuln_components: number
  a07_auth_failures: number
  a08_integrity_failures: number
  a09_logging_failures: number
  a10_ssrf: number
}

export interface OwaspFinding {
  id: string
  category: string
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical'
  title: string
  description: string
  evidence: string
  remediation: string
  cve?: string
  cvss?: number
  found_at: string
}

export interface OwaspAudit {
  id: string
  target: string
  workspace_id: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  categories: string[]
  vulnerabilities: Partial<OwaspVulnerabilities>
  findings: OwaspFinding[]
  started_at: string
  completed_at?: string
  options?: Record<string, any>
  created_by: string
}

export interface CreateAuditData {
  target: string
  workspace_id: number
  categories?: string[]
  options?: Record<string, any>
}

export interface UpdateProgressData {
  progress: number
  status?: 'pending' | 'running' | 'completed' | 'failed'
}

export interface AddFindingData {
  category: string
  severity?: 'info' | 'low' | 'medium' | 'high' | 'critical'
  title?: string
  description?: string
  evidence?: string
  remediation?: string
  cve?: string
  cvss?: number
}

export interface ApiResponse<T = any> {
  success?: boolean
  message?: string
  error?: string
  [key: string]: any
}
