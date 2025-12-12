/**
 * Reconnaissance Types
 * ====================
 * 
 * Tipos relacionados con reconocimiento y recopilación de información.
 */

export interface ReconResult {
  success: boolean
  tool: string
  target: string
  output?: string
  error?: string
  subdomains?: string[]
  count?: number
}

export interface ReconCompleteResult {
  target: string
  timestamp: string
  phases: {
    [key: string]: ReconResult
  }
  summary: {
    total_phases: number
    successful_phases: number
    failed_phases: number
  }
}

export interface ReconSession {
  id: number
  session_id: string
  target: string
  created_at: string
  status: string
}


