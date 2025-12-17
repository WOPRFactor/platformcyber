/**
 * Tipos para el módulo de reportes
 */

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

export interface ReportGenerationRequest {
  type: 'executive' | 'technical' | 'compliance'
  target: string
  startDate?: string
  endDate?: string
  complianceStandard?: 'pci_dss' | 'hipaa' | 'iso_27001' | 'nist' | 'general'
  options?: Record<string, any>
}

export interface ReportExportRequest {
  report_id: string
  format: 'pdf' | 'html' | 'json'
  options?: Record<string, any>
}

export interface ReportGenerationResponse {
  report_id: string
  message: string
  estimated_time: number
  status: 'queued' | 'generating'
}

export interface ReportStatusResponse {
  report_id: string
  status: 'generating' | 'completed' | 'failed'
  progress?: number
  error?: string
  result?: ExecutiveSummaryData | TechnicalReportData | ComplianceReportData
}

export interface ReportsListResponse {
  reports: ReportListItem[]
  total: number
  page: number
  limit: number
}

export interface ReportDeletionResponse {
  message: string
  report_id: string
}



