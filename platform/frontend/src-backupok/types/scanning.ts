/**
 * Scanning Types
 * ==============
 * 
 * Tipos relacionados con escaneos y sesiones de escaneo.
 */

export interface ScanSession {
  id: number
  session_id: string
  target: string
  scan_type: string
  status: 'pending' | 'running' | 'completed' | 'error'
  start_time?: string
  end_time?: string
  progress: number
  stealth_mode: boolean
  aggressive_mode: boolean
  full_scan: boolean
  ports_found: number
  services_detected: number
  vulnerabilities: number
}

export interface ScanResult {
  id: number
  session_id: number
  result_type: string
  tool_name: string
  output_file?: string
  parsed_data?: any
  created_at: string
}

export interface SystemInfo {
  cpu_count: number
  memory: {
    available: number
    percent: number
    total: number
  }
  disk: {
    free: number
    percent: number
    total: number
  }
  platform: string
  python_version: string
}

export interface HealthCheck {
  status: 'healthy' | 'unhealthy'
  timestamp: string
  system_info: SystemInfo
}

export interface IAnalysis {
  id: number
  session_id: number
  analysis_type: string
  ai_provider: string
  summary?: string
  confidence_score: number
  processing_time?: number
  status: string
  created_at: string
  completed_at?: string
}


