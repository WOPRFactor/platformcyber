/**
 * Types for MITRE ATT&CK API
 */

export interface MitreTactic {
  id: string
  name: string
  description: string
  techniques_count: number
}

export interface MitreTechnique {
  id: string
  name: string
  tactic: string
  description: string
  detection: string
  platforms: string[]
  data_sources: string[]
}

export interface MitreExecution {
  id: string
  technique_id: string
  technique_name: string
  target: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  detected: boolean
  logs: string[]
  timestamp: string
}

export interface MitreCampaign {
  id: string
  name: string
  workspace_id: number
  description: string
  techniques: string[]
  status: 'pending' | 'running' | 'completed' | 'cancelled'
  executions: MitreExecution[]
  created_at: string
  created_by: string
}

export interface CreateCampaignData {
  name: string
  workspace_id: number
  techniques: string[]
  description?: string
}

export interface ExecuteTechniqueData {
  technique_id: string
  target?: string
}

export interface CoverageByTactic {
  name: string
  total: number
  covered: number
  coverage_percent: number
}

export interface CoverageGap {
  technique_id: string
  name: string
  severity: 'low' | 'medium' | 'high' | 'critical'
}

export interface CoverageMatrix {
  total_techniques: number
  covered_techniques: number
  coverage_percent: number
  by_tactic: Record<string, CoverageByTactic>
  gaps: CoverageGap[]
}

export interface KillChain {
  name: string
  description: string
  techniques: string[]
  severity: 'low' | 'medium' | 'high' | 'critical'
  target: string
}

export interface MitreStats {
  total_tactics: number
  total_techniques: number
  total_kill_chains: number
  tactics: string[]
  framework_version: string
}

export interface ApiResponse<T = any> {
  success?: boolean
  message?: string
  error?: string
  [key: string]: any
}
