/**
 * Módulo de Escaneo (Scanning)
 * Maneja operaciones de escaneo de vulnerabilidades y servicios
 */

import { api } from '../shared/client'
import type {
  ScanStartData,
  ScanSession,
  ScanResult,
  QuickScanResult,
  ServiceScanResult,
  VulnScanResult,
  OSDetectResult,
  NetworkDiscoveryResult,
  ComprehensiveScanResult,
  ScanStartResponse,
  ScanStopResponse
} from './types'

/**
 * Inicia un nuevo escaneo
 * @param data - Datos para iniciar el escaneo
 * @returns Respuesta con ID de sesión y mensaje de confirmación
 */
export const startScan = async (data: ScanStartData): Promise<ScanStartResponse> => {
  const response = await api.post<ScanStartResponse>('scanning/start', data)
  return response.data
}

/**
 * Obtiene el estado de un escaneo específico
 * @param sessionId - ID de la sesión de escaneo
 * @returns Estado actual del escaneo
 */
export const getScanStatus = async (scanId: string | number): Promise<{ session: ScanSession }> => {
  const response = await api.get<{ scan_id: number; status: string; progress: number; target: string; scan_type: string; tool: string; started_at: string | null; completed_at: string | null; error: string | null }>(`scanning/scans/${scanId}`)
  // Convertir respuesta del backend al formato esperado por el frontend
  return {
    session: {
      id: response.data.scan_id,
      session_id: String(response.data.scan_id),
      status: response.data.status,
      progress: response.data.progress || 0,
      target: response.data.target,
      scan_type: response.data.scan_type || 'basic',
      tool: response.data.tool || 'nmap',
      started_at: response.data.started_at,
      completed_at: response.data.completed_at,
      error: response.data.error || null,  // Incluir el campo error
      ports_found: 0,
      services_detected: 0
    }
  }
}

/**
 * Obtiene los resultados de un escaneo específico
 * @param sessionId - ID de la sesión de escaneo
 * @returns Array de resultados del escaneo
 */
export const getScanResults = async (sessionId: string): Promise<ScanResult[]> => {
  const response = await api.get<ScanResult[]>(`scanning/${sessionId}/results`)
  return response.data
}

/**
 * Lista todas las sesiones de escaneo del workspace
 * @param workspaceId - ID del workspace (requerido)
 * @returns Array de sesiones de escaneo
 */
export const getScanSessions = async (workspaceId: number): Promise<ScanSession[]> => {
  const response = await api.get<{ scans: ScanSession[] }>('scanning/sessions', {
    params: { workspace_id: workspaceId }
  })
  return response.data.scans ?? []
}

/**
 * Detiene un escaneo en ejecución
 * @param sessionId - ID de la sesión a detener
 * @returns Respuesta de confirmación
 */
export const stopScan = async (sessionId: string): Promise<ScanStopResponse> => {
  const response = await api.post<ScanStopResponse>(`scanning/${sessionId}/stop`)
  return response.data
}

/**
 * Realiza un escaneo rápido de puertos
 * @param target - Objetivo a escanear
 * @returns Resultado del escaneo rápido
 */
export const quickScan = async (target: string): Promise<QuickScanResult> => {
  const response = await api.get<QuickScanResult>(`scanning/quick/${target}`)
  return response.data
}

/**
 * Escanea servicios en el objetivo
 * @param target - Objetivo a escanear
 * @returns Resultado del escaneo de servicios
 */
export const serviceScan = async (target: string): Promise<ServiceScanResult> => {
  const response = await api.get<ServiceScanResult>(`scanning/service/${target}`)
  return response.data
}

/**
 * Escanea vulnerabilidades en el objetivo
 * @param target - Objetivo a escanear
 * @returns Resultado del escaneo de vulnerabilidades
 */
export const vulnerabilityScan = async (target: string): Promise<VulnScanResult> => {
  const response = await api.get<VulnScanResult>(`scanning/vulnerability/${target}`)
  return response.data
}

/**
 * Detecta el sistema operativo del objetivo
 * @param target - Objetivo a analizar
 * @returns Resultado de la detección de OS
 */
export const osDetection = async (target: string): Promise<OSDetectResult> => {
  const response = await api.get<OSDetectResult>(`scanning/os/${target}`)
  return response.data
}

/**
 * Realiza descubrimiento de red
 * @param target - Red o rango a escanear
 * @returns Resultado del descubrimiento de red
 */
export const networkDiscovery = async (target: string): Promise<NetworkDiscoveryResult> => {
  const response = await api.get<NetworkDiscoveryResult>(`scanning/network/${target}`)
  return response.data
}

/**
 * Ejecuta un escaneo completo y comprehensivo
 * @param target - Objetivo del escaneo completo
 * @returns Resultado comprehensivo de todas las fases
 */
export const comprehensiveScan = async (target: string): Promise<ComprehensiveScanResult> => {
  const response = await api.post<ComprehensiveScanResult>(`scanning/comprehensive/${target}`)
  return response.data
}

/**
 * Inicia un escaneo RustScan (ultra-rápido)
 * @param target - Objetivo a escanear
 * @param workspaceId - ID del workspace
 * @param options - Opciones de RustScan (batch_size, timeout, ulimit)
 * @returns Respuesta con ID de escaneo
 */
export const rustscan = async (
  target: string,
  workspaceId: number,
  options?: { batch_size?: number; timeout?: number; ulimit?: number }
) => {
  const response = await api.post('scanning/rustscan', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

/**
 * Inicia un escaneo Masscan (masivo)
 * @param target - Objetivo a escanear
 * @param workspaceId - ID del workspace
 * @param ports - Puertos a escanear (ej: "1-65535" o "80,443,8080")
 * @param options - Opciones de Masscan (rate, environment)
 * @returns Respuesta con ID de escaneo
 */
export const masscan = async (
  target: string,
  workspaceId: number,
  ports: string = '1-65535',
  options?: { rate?: number; environment?: 'internal' | 'external' | 'stealth' }
) => {
  // Construir body solo con campos válidos
  const body: {
    target: string
    workspace_id: number
    ports: string
    rate?: number
    environment?: 'internal' | 'external' | 'stealth'
  } = {
    target,
    workspace_id: workspaceId,
    ports
  }
  
  // Agregar solo campos válidos de options
  if (options) {
    if (options.rate !== undefined) {
      body.rate = options.rate
    }
    if (options.environment !== undefined) {
      body.environment = options.environment
    }
  }
  
  const response = await api.post('scanning/masscan', body)
  return response.data
}

/**
 * Inicia un escaneo Naabu (port discovery rápido)
 * @param target - Objetivo a escanear
 * @param workspaceId - ID del workspace
 * @param options - Opciones de Naabu (top_ports, rate, verify)
 * @returns Respuesta con ID de escaneo
 */
export const naabu = async (
  target: string,
  workspaceId: number,
  options?: { top_ports?: number; rate?: number; verify?: boolean }
) => {
  const response = await api.post('scanning/naabu', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

// ============================================
// ENUMERACIÓN SMB/CIFS
// ============================================

export const enum4linux = async (
  target: string,
  workspaceId: number,
  options?: { use_ng?: boolean; all?: boolean }
) => {
  const response = await api.post('scanning/enum/smb/enum4linux', {
    target,
    workspace_id: workspaceId,
    use_ng: options?.use_ng ?? true,
    all: options?.all ?? false
  })
  return response.data
}

export const smbmap = async (
  target: string,
  workspaceId: number,
  options?: { username?: string; password?: string; share?: string }
) => {
  const response = await api.post('scanning/enum/smb/smbmap', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

export const smbclient = async (
  target: string,
  workspaceId: number,
  options?: { share?: string; username?: string; password?: string }
) => {
  const response = await api.post('scanning/enum/smb/smbclient', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

// ============================================
// ENUMERACIÓN SERVICIOS DE RED
// ============================================

export const sshEnum = async (
  target: string,
  workspaceId: number,
  options?: { port?: number; tool?: 'nmap' | 'ssh-audit' }
) => {
  const response = await api.post('scanning/enum/ssh', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

export const ftpEnum = async (
  target: string,
  workspaceId: number,
  options?: { port?: number; tool?: 'nmap' | 'ftp' }
) => {
  const response = await api.post('scanning/enum/ftp', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

export const smtpEnum = async (
  target: string,
  workspaceId: number,
  options?: { port?: number; tool?: 'nmap' | 'smtp-user-enum' }
) => {
  const response = await api.post('scanning/enum/smtp', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

export const dnsEnum = async (
  target: string,
  workspaceId: number,
  options?: { port?: number; tool?: 'nmap' | 'dig' }
) => {
  const response = await api.post('scanning/enum/dns', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

export const snmpEnum = async (
  target: string,
  workspaceId: number,
  options?: { port?: number; community?: string }
) => {
  const response = await api.post('scanning/enum/snmp', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

export const ldapEnum = async (
  target: string,
  workspaceId: number,
  options?: { port?: number; tool?: 'nmap' | 'ldapsearch' }
) => {
  const response = await api.post('scanning/enum/ldap', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

export const rdpEnum = async (
  target: string,
  workspaceId: number,
  options?: { port?: number; tool?: 'nmap' }
) => {
  const response = await api.post('scanning/enum/rdp', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

// ============================================
// ENUMERACIÓN BASES DE DATOS
// ============================================

export const mysqlEnum = async (
  target: string,
  workspaceId: number,
  options?: { port?: number; tool?: 'nmap' | 'mysql'; username?: string }
) => {
  const response = await api.post('scanning/enum/mysql', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

export const postgresqlEnum = async (
  target: string,
  workspaceId: number,
  options?: { port?: number; tool?: 'nmap' | 'psql'; username?: string }
) => {
  const response = await api.post('scanning/enum/postgresql', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

export const redisEnum = async (
  target: string,
  workspaceId: number,
  options?: { port?: number; tool?: 'nmap' | 'redis-cli' }
) => {
  const response = await api.post('scanning/enum/redis', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

export const mongodbEnum = async (
  target: string,
  workspaceId: number,
  options?: { port?: number }
) => {
  const response = await api.post('scanning/enum/mongodb', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

// ============================================
// ANÁLISIS SSL/TLS
// ============================================

export const sslscan = async (
  target: string,
  workspaceId: number,
  options?: { port?: number; show_certificate?: boolean }
) => {
  const response = await api.post('scanning/enum/ssl/sslscan', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

export const sslyze = async (
  target: string,
  workspaceId: number,
  options?: { port?: number; regular?: boolean }
) => {
  const response = await api.post('scanning/enum/ssl/sslyze', {
    target,
    workspace_id: workspaceId,
    ...options
  })
  return response.data
}

/**
 * Objeto API de escaneo - compatible hacia atrás
 * Agrupa todas las funciones de escaneo
 */
export const scanningAPI = {
  startScan,
  getScanStatus,
  getScanResults,
  getScanSessions,
  stopScan,
  quickScan,
  serviceScan,
  vulnerabilityScan,
  osDetection,
  networkDiscovery,
  comprehensiveScan,
  rustscan,
  masscan,
  naabu,
  // Enumeración SMB
  enum4linux,
  smbmap,
  smbclient,
  // Enumeración servicios de red
  sshEnum,
  ftpEnum,
  smtpEnum,
  dnsEnum,
  snmpEnum,
  ldapEnum,
  rdpEnum,
  // Enumeración bases de datos
  mysqlEnum,
  postgresqlEnum,
  redisEnum,
  mongodbEnum,
  // Análisis SSL/TLS
  sslscan,
  sslyze
}

