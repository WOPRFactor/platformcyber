/**
 * Punto de entrada del módulo de autenticación
 * Exporta todas las funciones y tipos relacionados con auth
 */

export * from './types'
export * from './auth'

// Exportar objeto API compatible hacia atrás
export { authAPI } from './auth'
