/**
 * API Principal - Punto de entrada unificado
 * Exporta todos los módulos de API organizados por dominio
 */

// Cliente HTTP configurado
export { api } from './shared/client'

// Importar funciones de cada módulo
import * as auth from './auth'
import * as system from './system'
import * as reconnaissance from './reconnaissance'
import * as scanning from './scanning'
import * as workspaces from './workspaces'
import * as owasp from './owasp'
import * as mitre from './mitre'
import * as vulnerability from './vulnerability'
import * as exploitation from './exploitation'
import * as postExploit from './postExploit'
import * as reporting from './reporting'
import * as whitebox from './whitebox'

// Crear objetos API compatibles hacia atrás
export const authAPI = auth
export const systemAPI = system
export const reconnaissanceAPI = reconnaissance
export const scanningAPI = scanning
export const workspacesAPI = workspaces
export const owaspAPI = owasp
export const mitreAPI = mitre
export const vulnerabilityAPI = vulnerability
export const exploitationAPI = exploitation
export const postExploitAPI = postExploit
export const reportingAPI = reporting
export const whiteboxAPI = whitebox

// Exportar tipos y funciones individuales
export * from './auth'
export * from './system'
export * from './reconnaissance'
export * from './scanning'
export * from './workspaces'
export * from './owasp'
export * from './mitre'
export * from './vulnerability'
export * from './exploitation'
export * from './postExploit'
export * from './reporting'
export * from './whitebox'
