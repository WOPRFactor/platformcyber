/**
 * Reporting Types
 * ===============
 * 
 * Tipos relacionados con reportes y exportación.
 */

export interface Report {
  id: number
  report_id: string
  title: string
  report_type: string
  format: string
  file_path?: string
  client_name?: string
  project_name?: string
  created_by?: string
  created_at: string
  download_count: number
}

export interface ExecutiveSummaryData {
  target: string
  assessment_period: string
  scope: string[]
  methodology: string
  key_findings: string[]
  risk_level: 'low' | 'medium' | 'high' | 'critical'
  recommendations: string[]
}

export interface TechnicalReportData {
  target: string
  assessment_period: string
  scope: string[]
  methodology: string
  detailed_findings: any[]
  vulnerability_analysis: any[]
  exploitation_attempts: any[]
  recommendations: string[]
}

export interface ComplianceReportData {
  target: string
  standard: 'pci_dss' | 'hipaa' | 'iso_27001' | 'nist' | 'general'
  assessment_period: string
  compliance_score: number
  violations: any[]
  remediation_plan: string[]
}

export interface ReportExportResult {
  report_id: string
  download_url: string
  format: 'pdf' | 'html' | 'json'
  size: number
}

export interface ReportListItem {
  id: string
  title: string
  type: 'executive' | 'technical' | 'compliance'
  created_at: string
  created_by: string
  status: 'generating' | 'completed' | 'failed'
}


