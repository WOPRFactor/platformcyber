/**
 * System Monitor Types
 * ====================
 * 
 * Tipos e interfaces para la consola de logs en tiempo real.
 */

export type LogSource = 'BACKEND' | 'CELERY' | 'NIKTO' | 'NMAP' | 'NUCLEI' | 'SQLMAP' | 'ZAP' | 'TESTSSL' | 'WHATWEB' | 'DALFOX' | string

export type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR'

export type MonitorTab = 'unified' | 'backend' | 'celery' | 'tools'

/**
 * Log en tiempo real recibido vía WebSocket
 */
export interface RealTimeLog {
  id: string
  source: LogSource
  level: LogLevel
  message: string
  timestamp: Date
  raw?: string // Para comandos como "$ nikto -h ..."
  taskId?: string
  workspaceId?: number
}

/**
 * Filtros de fuente
 */
export interface SourceFilters {
  backend: boolean
  celery: boolean
  scanning: boolean  // Para logs de enumeración
  nikto: boolean
  nmap: boolean
  nuclei: boolean
  sqlmap: boolean
  zap: boolean
  testssl: boolean
  whatweb: boolean
  dalfox: boolean
}

/**
 * Filtros de nivel
 */
export interface LevelFilters {
  DEBUG: boolean
  INFO: boolean
  WARNING: boolean
  ERROR: boolean
}


