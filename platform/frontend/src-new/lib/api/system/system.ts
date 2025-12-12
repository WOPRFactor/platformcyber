/**
 * Módulo de Sistema
 * Maneja operaciones relacionadas con el estado del sistema y monitoreo
 */

import { api } from '../shared/client'
import type { HealthCheck, SystemInfo } from './types'

/**
 * Realiza un health check del sistema
 * @returns Estado de salud de todos los servicios del sistema
 */
export const healthCheck = async (): Promise<HealthCheck> => {
  const response = await api.get<HealthCheck>('system/health')
  return response.data
}

/**
 * Obtiene información detallada del sistema
 * @returns Información del sistema incluyendo memoria, CPU, versiones, etc.
 */
export const systemInfo = async (): Promise<SystemInfo> => {
  const response = await api.get<SystemInfo>('system/info')
  return response.data
}

/**
 * Obtiene métricas del sistema
 * @returns Métricas del sistema: scans, sistema, estadísticas
 */
export const getSystemMetrics = async (): Promise<any> => {
  const response = await api.get('system/metrics')
  return response.data
}

/**
 * Objeto API de sistema - compatible hacia atrás
 * Agrupa todas las funciones del sistema
 */
export const systemAPI = {
  healthCheck,
  systemInfo,
  getSystemMetrics
}


