/**
 * Types for Scheduler API
 */

export interface ScheduledScan {
  scan_id: string
  scan_type: string
  target: string
  schedule: string
  next_run: string | null
  created_at: string
  status: 'active' | 'cancelled' | 'completed'
  options?: Record<string, any>
}

export interface CreateScheduledScanData {
  scan_id: string
  scan_type: string
  target: string
  schedule: string
  options?: Record<string, any>
}

export interface ScheduledScansResponse {
  scheduled_scans: ScheduledScan[]
}

export interface ApiResponse<T = any> {
  message?: string
  error?: string
  [key: string]: any
}




