/**
 * Whitebox Testing Types
 * ======================
 * 
 * Tipos relacionados con pruebas de caja blanca.
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
  findings: any[]
}

export interface DependencyAnalysisResult {
  dependencies_analyzed: number
  vulnerable_dependencies: number
  critical_vulnerabilities: number
  high_vulnerabilities: number
  medium_vulnerabilities: number
  low_vulnerabilities: number
  findings: any[]
}

export interface SecretsDetectionResult {
  files_scanned: number
  secrets_found: number
  high_risk_secrets: number
  medium_risk_secrets: number
  low_risk_secrets: number
  findings: any[]
}

export interface ConfigAnalysisResult {
  configs_analyzed: number
  misconfigurations_found: number
  critical_misconfigs: number
  high_misconfigs: number
  medium_misconfigs: number
  low_misconfigs: number
  findings: any[]
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


