/**
 * Tipos relacionados con el sistema
 * Define las interfaces para información del sistema y health checks
 */

export interface HealthCheck {
  status: 'healthy' | 'unhealthy'
  timestamp: string
  services: {
    database: 'up' | 'down'
    redis?: 'up' | 'down'
    filesystem: 'up' | 'down'
  }
  uptime: number
  version: string
}

export interface SystemInfo {
  platform: string
  node_version: string
  python_version: string
  database_type: string
  total_memory: number
  free_memory: number
  cpu_count: number
  hostname: string
  uptime: number
}



