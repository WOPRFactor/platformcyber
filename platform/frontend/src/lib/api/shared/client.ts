/**
 * Cliente HTTP configurado con Axios
 * Instancia centralizada con interceptores para autenticación y manejo de errores
 */

import axios from 'axios'

// Detectar si estamos en entorno de producción por variable de entorno
const isProductionEnv = import.meta.env.VITE_ENV === 'prod'
// DEV4-IMPROVEMENTS: Puerto 5001 para entorno de mejoras
// Usar IP de red para acceso desde LAN
const baseURL = isProductionEnv ? 'http://192.168.0.11:5002/api/v1' : 'http://192.168.0.11:5001/api/v1'

/**
 * Instancia configurada de Axios para toda la aplicación
 * Incluye configuración base, timeout y headers por defecto
 */
export const api = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Función para crear instancia de Axios con timeout personalizado
 * Útil para operaciones que requieren más tiempo (escaneos completos, etc.)
 */
export const createApiInstance = (customTimeout: number = 30000) => {
  return axios.create({
    baseURL,
    timeout: customTimeout,
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

/**
 * Interceptor de request para agregar token de autenticación
 * Agrega automáticamente el token Bearer si existe en localStorage
 */
api.interceptors.request.use(
  (config) => {
    // Endpoints públicos que no requieren autenticación
    const publicEndpoints = ['/system/health', '/api/auth/login']

    // Solo agregar token si no es un endpoint público
    const isPublicEndpoint = publicEndpoints.some(endpoint =>
      config.url?.includes(endpoint)
    )

    if (!isPublicEndpoint) {
      const token = localStorage.getItem('access_token')
      console.log('🔐 Interceptor - URL:', config.url)
      console.log('🔐 Interceptor - Token exists:', !!token)
      console.log('🔐 Interceptor - Token length:', token?.length)
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
        console.log('✅ Interceptor - Authorization header set')
      } else {
        console.warn('⚠️ Interceptor - No token found in localStorage')
      }
    } else {
      console.log('📢 Interceptor - Public endpoint, skipping auth:', config.url)
    }

    // Agregar workspace_id=1 si no existe (por defecto)
    // Excluir endpoints que no requieren workspace_id (crear workspace, etc.)
    // o que lo envían en el body (vulnerability/comprehensive, scanning/start, etc.)
    const endpointsWithoutWorkspaceId = ['workspaces/', 'auth/']
    const endpointsAlwaysExcluded = [
      'system/running-scans', 
      'system/health', 
      'system/info',
      'reconnaissance/scans'  // Endpoints de scans no necesitan workspace_id en query
    ]
    const endpointsWithWorkspaceIdInBody = ['vulnerability/comprehensive', 'scanning/start']
    
    const shouldExcludeWorkspaceId = (
      endpointsWithoutWorkspaceId.some(endpoint =>
        config.url?.includes(endpoint) && config.method?.toUpperCase() === 'POST'
      ) ||
      endpointsAlwaysExcluded.some(endpoint => config.url?.includes(endpoint))
    )
    
    const hasWorkspaceIdInBody = endpointsWithWorkspaceIdInBody.some(endpoint =>
      config.url?.includes(endpoint) && config.method?.toUpperCase() === 'POST'
    )
    
    // Verificar si workspace_id ya está en la URL, en params, o en el body
    const urlHasWorkspaceId = config.url?.includes('workspace_id=')
    const paramsHasWorkspaceId = config.params?.workspace_id !== undefined
    
    // Verificar si workspace_id está en el body (puede ser objeto o string JSON)
    let bodyHasWorkspaceId = false
    if (config.data) {
      if (typeof config.data === 'object' && !Array.isArray(config.data)) {
        bodyHasWorkspaceId = 'workspace_id' in config.data
      } else if (typeof config.data === 'string') {
        try {
          const parsed = JSON.parse(config.data)
          bodyHasWorkspaceId = typeof parsed === 'object' && parsed !== null && 'workspace_id' in parsed
        } catch (e) {
          // No es JSON válido, ignorar
        }
      }
    }
    
    // Debug logging para comprehensive scan
    if (config.url?.includes('vulnerability/comprehensive')) {
      console.log('🔍 [Interceptor] Comprehensive scan request:', {
        url: config.url,
        method: config.method,
        hasWorkspaceIdInBody: hasWorkspaceIdInBody,
        bodyHasWorkspaceId: bodyHasWorkspaceId,
        urlHasWorkspaceId: urlHasWorkspaceId,
        paramsHasWorkspaceId: paramsHasWorkspaceId,
        data: config.data,
        params: config.params
      })
    }
    
    // No agregar workspace_id a query params si:
    // 1. Está en la lista de exclusión
    // 2. El endpoint lo envía en el body (lista explícita) O está detectado en el body
    // 3. Ya está en la URL o en params
    const shouldSkipWorkspaceId = shouldExcludeWorkspaceId || 
                                   hasWorkspaceIdInBody || 
                                   bodyHasWorkspaceId || 
                                   urlHasWorkspaceId || 
                                   paramsHasWorkspaceId
    
    if (!shouldSkipWorkspaceId) {
      if (!config.params) {
        config.params = {}
      }
      config.params.workspace_id = 1
    }

    // Agregar X-Project-ID por defecto si no existe
    if (!config.headers['X-Project-ID']) {
      config.headers['X-Project-ID'] = '00000000-0000-0000-0000-000000000000'
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Interceptor de response para manejar errores de autenticación
 * Redirige al login si el token es inválido o expiró
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log detallado de errores para debugging
    const url = error.config?.url || ''
    
    if (url.includes('auth/login')) {
      console.error('🔴 Error en petición de login:', {
        message: error.message,
        code: error.code,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        headers: error.response?.headers,
        isNetworkError: !error.response,
        config: {
          url: error.config.url,
          method: error.config.method,
          baseURL: error.config.baseURL,
          headers: error.config.headers
        }
      })
    } else if (url.includes('reporting')) {
      // Log detallado para errores de reporting
      const errorData = error.response?.data
      console.error('🔴 Error en petición de reporting:', {
        message: error.message,
        code: error.code,
        status: error.response?.status,
        statusText: error.response?.statusText,
        isNetworkError: !error.response,
        isConnectionRefused: error.code === 'ERR_CONNECTION_REFUSED' || error.code === 'ERR_NETWORK',
        config: {
          url: error.config.url,
          method: error.config.method,
          baseURL: error.config.baseURL
        }
      })
      
      // Mostrar detalles del error del servidor
      if (errorData) {
        console.error('📋 Detalles del error del servidor:', errorData)
        if (errorData.details) {
          console.error('   Mensaje de error:', errorData.details)
        }
        if (errorData.traceback) {
          console.error('   Traceback:', errorData.traceback)
        }
        if (errorData.type) {
          console.error('   Tipo de error:', errorData.type)
        }
      }
      
      // Si es un error de conexión, mejorar el mensaje
      if (error.code === 'ERR_CONNECTION_REFUSED' || error.code === 'ERR_NETWORK') {
        error.message = 'No se pudo conectar con el servidor. Verifica que el backend esté funcionando.'
      }
    }
    
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)



