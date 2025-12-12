/**
 * Tipos relacionados con escaneo (scanning)
 * Define las interfaces para resultados de escaneo y sesiones
 */

export interface ScanStartData {
  target: string
  scan_type?: string
  options?: Record<string, unknown>
}

export interface ScanPortResult {
  port: number
  protocol: string
  state: string
  service: string
}

export interface ScanServiceResult {
  port: string
  protocol: string
  state: string
  service: string
  version: string
}

export interface ScanVulnResult {
  description: string
  severity: string
}

export interface ScanOSResult {
  os_details?: string
  os_cpe?: string
  device_type?: string
}

export interface ScanHostResult {
  ip: string
  hostname: string
  status: string
}

export interface QuickScanResult {
  success: boolean
  target: string
  scan_type: string
  open_ports: ScanPortResult[]
  output: string
  error: string
  command: string
}

export interface ServiceScanResult {
  success: boolean
  target: string
  scan_type: string
  services: ScanServiceResult[]
  os_info: ScanOSResult
  output: string
  error: string
  command: string
}

export interface VulnScanResult {
  success: boolean
  target: string
  scan_type: string
  vulnerabilities: ScanVulnResult[]
  output: string
  error: string
  command: string
}

export interface OSDetectResult {
  success: boolean
  target: string
  scan_type: string
  os_info: ScanOSResult
  output: string
  error: string
  command: string
}

export interface NetworkDiscoveryResult {
  success: boolean
  target: string
  scan_type: string
  hosts: ScanHostResult[]
  output: string
  error: string
  command: string
}

export interface ComprehensiveScanResult {
  target: string
  timestamp: string
  phases: {
    quick_ports: QuickScanResult
    services: ServiceScanResult
    os_detection: OSDetectResult
    vulnerabilities: VulnScanResult
  }
  summary: {
    total_phases: number
    successful_phases: number
    failed_phases: number
    total_findings: number
    open_ports: number
    services_detected: number
    vulnerabilities_found: number
  }
}

export interface ScanSession {
  id: number
  session_id: string
  target: string
  status: string
  progress?: number
  scan_type?: string
  tool?: string
  started_at?: string | null
  completed_at?: string | null
  created_at: string
  ports_found?: number
  services_detected?: number
  os_detected?: boolean
  error?: string | null
}

export interface ScanResult {
  id: number
  session_id: string
  result_type: string
  data: unknown
  created_at: string
}

export interface ScanStartResponse {
  success?: boolean
  scan_id: number
  session_id?: string
  task_id?: string
  status: string
  tool: string
  scan_type?: string
  target: string
  message?: string
}

export interface ScanStopResponse {
  success: boolean
  message: string
}


