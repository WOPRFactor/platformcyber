/**
 * Módulo de Whitebox Testing
 * Maneja análisis estáticos de código, dependencias, secretos y configuraciones
 */

import { api } from '../shared/client'
import type {
  CodeAnalysisResult,
  DependencyAnalysisResult,
  SecretsDetectionResult,
  ConfigAnalysisResult,
  ComprehensiveWhiteboxResult,
  WhiteboxSession,
  CodeFinding,
  VulnerableDependency,
  SecretFinding,
  ConfigIssue,
  CodeAnalysisRequest,
  DependencyAnalysisRequest,
  SecretsAnalysisRequest,
  ConfigAnalysisRequest,
  ComprehensiveAnalysisRequest,
  AnalysisResponse,
  AnalysisResultResponse,
  WhiteboxSessionsResponse,
  SessionDeletionResponse
} from './types'

/**
 * Lista todas las sesiones de whitebox testing
 * @param page - Página de resultados (default: 1)
 * @param limit - Número de sesiones por página (default: 20)
 * @returns Lista de sesiones con paginación
 */
export const getWhiteboxSessions = async (page: number = 1, limit: number = 20): Promise<WhiteboxSession[]> => {
  const response = await api.get<WhiteboxSessionsResponse>('whitebox/sessions', {
    params: { page, limit }
  })
  return response.data.sessions
}

/**
 * Obtiene el estado y resultados de una sesión específica
 * @param sessionId - ID de la sesión
 * @returns Estado y resultados de la sesión
 */
export const getSessionStatus = async (sessionId: string): Promise<AnalysisResultResponse> => {
  const response = await api.get<AnalysisResultResponse>(`whitebox/sessions/${sessionId}/status`)
  return response.data
}

/**
 * Obtiene los resultados completos de una sesión
 * @param sessionId - ID de la sesión
 * @returns Resultados completos del análisis
 */
export const getSessionResults = async (sessionId: string): Promise<AnalysisResultResponse> => {
  const response = await api.get<AnalysisResultResponse>(`whitebox/sessions/${sessionId}/results`)
  return response.data
}

/**
 * Inicia análisis de código estático
 * @param request - Configuración del análisis de código
 * @returns Respuesta de inicio del análisis
 */
export const codeAnalysis = async (request: CodeAnalysisRequest): Promise<AnalysisResponse> => {
  const response = await api.post<AnalysisResponse>('whitebox/code/analysis', request)
  return response.data
}

/**
 * Inicia análisis de dependencias
 * @param request - Configuración del análisis de dependencias
 * @returns Respuesta de inicio del análisis
 */
export const dependencyAnalysis = async (request: DependencyAnalysisRequest): Promise<AnalysisResponse> => {
  const response = await api.post<AnalysisResponse>('whitebox/dependencies/analysis', request)
  return response.data
}

/**
 * Inicia detección de secretos
 * @param request - Configuración de la detección de secretos
 * @returns Respuesta de inicio del análisis
 */
export const secretsAnalysis = async (request: SecretsAnalysisRequest): Promise<AnalysisResponse> => {
  const response = await api.post<AnalysisResponse>('whitebox/secrets/analysis', request)
  return response.data
}

/**
 * Inicia análisis de configuraciones
 * @param request - Configuración del análisis de configuraciones
 * @returns Respuesta de inicio del análisis
 */
export const configAnalysis = async (request: ConfigAnalysisRequest): Promise<AnalysisResponse> => {
  const response = await api.post<AnalysisResponse>('whitebox/config/analysis', request)
  return response.data
}

/**
 * Inicia análisis completo de whitebox testing
 * @param request - Configuración del análisis completo
 * @returns Respuesta de inicio del análisis
 */
export const comprehensiveAnalysis = async (request: ComprehensiveAnalysisRequest): Promise<AnalysisResponse> => {
  const response = await api.post<AnalysisResponse>('whitebox/comprehensive/analysis', request)
  return response.data
}

/**
 * Ejecuta análisis rápido de código (subset de reglas)
 * @param targetPath - Ruta del código a analizar
 * @param language - Lenguaje de programación
 * @returns Resultado del análisis rápido
 */
export const quickCodeAnalysis = async (targetPath: string, language?: string): Promise<CodeAnalysisResult> => {
  const response = await api.post<CodeAnalysisResult>('whitebox/code/quick', { target_path: targetPath, language })
  return response.data
}

/**
 * Escanea dependencias por vulnerabilidades conocidas (usando bases de datos locales)
 * @param targetPath - Ruta del proyecto
 * @param packageManager - Gestor de paquetes
 * @returns Resultado del escaneo de dependencias
 */
export const quickDependencyScan = async (targetPath: string, packageManager?: string): Promise<DependencyAnalysisResult> => {
  const response = await api.post<DependencyAnalysisResult>('whitebox/dependencies/quick', { target_path: targetPath, package_manager: packageManager })
  return response.data
}

/**
 * Escaneo rápido de secretos usando patrones comunes
 * @param targetPath - Ruta a escanear
 * @returns Resultado del escaneo de secretos
 */
export const quickSecretsScan = async (targetPath: string): Promise<SecretsDetectionResult> => {
  const response = await api.post<SecretsDetectionResult>('whitebox/secrets/quick', { target_path: targetPath })
  return response.data
}

/**
 * Verificación rápida de configuraciones de seguridad comunes
 * @param targetPath - Ruta a verificar
 * @returns Resultado del análisis de configuraciones
 */
export const quickConfigCheck = async (targetPath: string): Promise<ConfigAnalysisResult> => {
  const response = await api.post<ConfigAnalysisResult>('whitebox/config/quick', { target_path: targetPath })
  return response.data
}

/**
 * Análisis completo rápido (todas las verificaciones básicas)
 * @param targetPath - Ruta del proyecto
 * @returns Resultado completo del análisis rápido
 */
export const quickComprehensiveAnalysis = async (targetPath: string): Promise<ComprehensiveWhiteboxResult> => {
  const response = await api.post<ComprehensiveWhiteboxResult>('whitebox/quick/comprehensive', { target_path: targetPath })
  return response.data
}

/**
 * Obtiene estadísticas generales de análisis whitebox
 * @returns Estadísticas agregadas
 */
export const getAnalysisStatistics = async (): Promise<{
  total_sessions: number
  completed_sessions: number
  failed_sessions: number
  total_findings: number
  critical_findings: number
  high_findings: number
  medium_findings: number
  low_findings: number
  most_common_issues: Array<{ issue: string; count: number }>
  analysis_types_usage: Record<string, number>
}> => {
  const response = await api.get<{
    total_sessions: number
    completed_sessions: number
    failed_sessions: number
    total_findings: number
    critical_findings: number
    high_findings: number
    medium_findings: number
    low_findings: number
    most_common_issues: Array<{ issue: string; count: number }>
    analysis_types_usage: Record<string, number>
  }>('whitebox/statistics')
  return response.data
}

/**
 * Exporta resultados de análisis en diferentes formatos
 * @param sessionId - ID de la sesión
 * @param format - Formato de exportación ('json' | 'html' | 'pdf' | 'sarif')
 * @returns URL de descarga del archivo exportado
 */
export const exportAnalysisResults = async (sessionId: string, format: 'json' | 'html' | 'pdf' | 'sarif' = 'json'): Promise<{ download_url: string }> => {
  const response = await api.post<{ download_url: string }>(`whitebox/sessions/${sessionId}/export`, { format })
  return response.data
}

/**
 * Detiene un análisis en ejecución
 * @param sessionId - ID de la sesión a detener
 * @returns Confirmación de detención
 */
export const stopAnalysis = async (sessionId: string): Promise<{ message: string }> => {
  const response = await api.post<{ message: string }>(`whitebox/sessions/${sessionId}/stop`)
  return response.data
}

/**
 * Elimina una sesión de análisis
 * @param sessionId - ID de la sesión a eliminar
 * @returns Confirmación de eliminación
 */
export const deleteAnalysisSession = async (sessionId: string): Promise<SessionDeletionResponse> => {
  const response = await api.delete<SessionDeletionResponse>(`whitebox/sessions/${sessionId}`)
  return response.data
}

/**
 * Obtiene recomendaciones de seguridad basadas en resultados de análisis
 * @param sessionId - ID de la sesión
 * @returns Lista de recomendaciones priorizadas
 */
export const getSecurityRecommendations = async (sessionId: string): Promise<{
  recommendations: Array<{
    priority: 'critical' | 'high' | 'medium' | 'low'
    category: string
    title: string
    description: string
    remediation_steps: string[]
    references: string[]
    effort: 'low' | 'medium' | 'high'
    impact: 'low' | 'medium' | 'high'
  }>
  summary: {
    total_recommendations: number
    critical_count: number
    high_count: number
    medium_count: number
    low_count: number
  }
}> => {
  const response = await api.get<{
    recommendations: Array<{
      priority: 'critical' | 'high' | 'medium' | 'low'
      category: string
      title: string
      description: string
      remediation_steps: string[]
      references: string[]
      effort: 'low' | 'medium' | 'high'
      impact: 'low' | 'medium' | 'high'
    }>
    summary: {
      total_recommendations: number
      critical_count: number
      high_count: number
      medium_count: number
      low_count: number
    }
  }>(`whitebox/sessions/${sessionId}/recommendations`)
  return response.data
}

/**
 * Objeto API de whitebox testing - compatible hacia atrás
 * Agrupa todas las funciones de análisis whitebox
 */
export const whiteboxAPI = {
  getWhiteboxSessions,
  getSessionStatus,
  getSessionResults,
  codeAnalysis,
  dependencyAnalysis,
  secretsAnalysis,
  configAnalysis,
  comprehensiveAnalysis,
  quickCodeAnalysis,
  quickDependencyScan,
  quickSecretsScan,
  quickConfigCheck,
  quickComprehensiveAnalysis,
  getAnalysisStatistics,
  exportAnalysisResults,
  stopAnalysis,
  deleteAnalysisSession,
  getSecurityRecommendations
}



