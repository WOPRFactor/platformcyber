/**
 * Tipos para el módulo de Whitebox Testing
 */

export interface CodeAnalysisResult {
  files_analyzed: number
  total_lines: number
  vulnerabilities_found: number
  critical_issues: number
  high_issues: number
  medium_issues: number
  low_issues: number
  info_issues: number
  findings: CodeFinding[]
}

export interface DependencyAnalysisResult {
  dependencies_analyzed: number
  vulnerable_dependencies: number
  critical_vulnerabilities: number
  high_vulnerabilities: number
  medium_vulnerabilities: number
  low_vulnerabilities: number
  findings: VulnerableDependency[]
}

export interface SecretsDetectionResult {
  files_scanned: number
  secrets_found: number
  high_risk_secrets: number
  medium_risk_secrets: number
  low_risk_secrets: number
  findings: SecretFinding[]
}

export interface ConfigAnalysisResult {
  configs_analyzed: number
  misconfigurations_found: number
  critical_misconfigs: number
  high_misconfigs: number
  medium_misconfigs: number
  low_misconfigs: number
  findings: ConfigIssue[]
}

export interface ComprehensiveWhiteboxResult {
  code_analysis: CodeAnalysisResult
  dependency_analysis: DependencyAnalysisResult
  secrets_detection: SecretsDetectionResult
  config_analysis: ConfigAnalysisResult
  summary: {
    total_findings: number
    risk_score: number
    recommendations: string[]
  }
}

export interface WhiteboxSession {
  id: string
  session_id: string
  target_path: string
  analysis_type: 'code' | 'dependencies' | 'secrets' | 'config' | 'comprehensive'
  status: 'running' | 'completed' | 'failed'
  created_at: string
  completed_at?: string
  progress: number
  results?: any
}

export interface CodeFinding {
  file: string
  line: number
  column?: number
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  rule_id: string
  rule_name: string
  description: string
  code_snippet?: string
  recommendation: string
  cwe_id?: string
  owasp_top_10?: string
}

export interface VulnerableDependency {
  name: string
  version: string
  ecosystem: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  cve_id?: string
  description: string
  fixed_version?: string
  references: string[]
}

export interface SecretFinding {
  file: string
  line: number
  secret_type: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  entropy_score?: number
  context?: string
  recommendation: string
  false_positive_probability?: number
}

export interface ConfigIssue {
  file: string
  line?: number
  config_type: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  issue_type: string
  description: string
  current_value?: string
  recommended_value?: string
  remediation: string
}

export interface CodeAnalysisRequest {
  target_path: string
  language?: 'javascript' | 'typescript' | 'python' | 'java' | 'csharp' | 'php' | 'ruby' | 'go' | 'rust' | 'auto'
  rules?: string[]
  exclude_patterns?: string[]
  include_patterns?: string[]
  max_file_size?: number
  timeout?: number
}

export interface DependencyAnalysisRequest {
  target_path: string
  package_manager?: 'npm' | 'yarn' | 'pip' | 'maven' | 'gradle' | 'nuget' | 'composer' | 'bundler' | 'go_modules' | 'cargo' | 'auto'
  include_dev_dependencies?: boolean
  severity_threshold?: 'critical' | 'high' | 'medium' | 'low' | 'info'
}

export interface SecretsAnalysisRequest {
  target_path: string
  scanners?: ('patterns' | 'entropy' | 'known_keys' | 'custom')[]
  exclude_patterns?: string[]
  include_patterns?: string[]
  entropy_threshold?: number
  custom_patterns?: Record<string, string>
}

export interface ConfigAnalysisRequest {
  target_path: string
  config_types?: ('web_servers' | 'databases' | 'permissions' | 'encryption' | 'authentication' | 'logging')[]
  custom_rules?: Record<string, any>
  severity_threshold?: 'critical' | 'high' | 'medium' | 'low' | 'info'
}

export interface ComprehensiveAnalysisRequest {
  target_path: string
  analysis_types?: ('code' | 'dependencies' | 'secrets' | 'config')[]
  options?: {
    code?: CodeAnalysisRequest
    dependencies?: DependencyAnalysisRequest
    secrets?: SecretsAnalysisRequest
    config?: ConfigAnalysisRequest
  }
}

export interface AnalysisResponse {
  session_id: string
  message: string
  estimated_time: number
  status: 'queued' | 'running'
}

export interface AnalysisResultResponse {
  session_id: string
  status: 'running' | 'completed' | 'failed'
  progress: number
  result?: CodeAnalysisResult | DependencyAnalysisResult | SecretsDetectionResult | ConfigAnalysisResult | ComprehensiveWhiteboxResult
  error?: string
  completed_at?: string
}

export interface WhiteboxSessionsResponse {
  sessions: WhiteboxSession[]
  total: number
  page: number
  limit: number
}

export interface SessionDeletionResponse {
  message: string
  session_id: string
}



