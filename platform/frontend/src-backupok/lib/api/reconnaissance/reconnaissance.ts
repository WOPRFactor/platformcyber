/**
 * Módulo de Reconocimiento (Reconnaissance)
 * Maneja operaciones de reconocimiento de objetivos y enumeración
 * 
 * Actualizado: 2025-11-26
 * - Todos los endpoints ahora usan POST con workspace_id
 * - Agregados nuevos métodos para todas las herramientas disponibles
 */

import { api } from '../shared/client'
import type { ReconResult, ReconCompleteResult, ReconSession, ReconLastResult } from './types'

/**
 * Realiza una consulta WHOIS del objetivo
 * @param target - Dominio o IP objetivo
 * @param workspaceId - ID del workspace
 * @returns Información del escaneo iniciado
 */
export const whois = async (target: string, workspaceId: number) => {
  const response = await api.post('reconnaissance/whois', {
    target,
    workspace_id: workspaceId
  })
  return response.data
}

/**
 * Realiza enumeración DNS del objetivo usando DNSRecon
 * @param domain - Dominio objetivo
 * @param workspaceId - ID del workspace
 * @param recordTypes - Tipos de registros a consultar (opcional)
 * @returns Información del escaneo iniciado
 */
export const dnsEnum = async (domain: string, workspaceId: number, recordTypes?: string[]) => {
  const response = await api.post('reconnaissance/dns', {
    domain,
    workspace_id: workspaceId,
    record_types: recordTypes
  })
  return response.data
}

/**
 * Descubre subdominios del objetivo
 * @param domain - Dominio objetivo
 * @param workspaceId - ID del workspace
 * @param tool - Herramienta a usar: 'subfinder' | 'amass' | 'assetfinder' | 'sublist3r' (default: 'subfinder')
 * @returns Información del escaneo iniciado
 */
export const subdomains = async (domain: string, workspaceId: number, tool: string = 'subfinder') => {
  const response = await api.post('reconnaissance/subdomains', {
    domain,
    workspace_id: workspaceId,
    tool
  })
  return response.data
}

/**
 * Busca emails asociados al dominio usando theHarvester
 * @param domain - Dominio objetivo
 * @param workspaceId - ID del workspace
 * @param sources - Fuentes de búsqueda (opcional, default: 'all')
 * @returns Información del escaneo iniciado
 */
export const emails = async (domain: string, workspaceId: number, sources: string = 'all') => {
  const response = await api.post('reconnaissance/emails', {
    domain,
    workspace_id: workspaceId,
    sources
  })
  return response.data
}

/**
 * Realiza web crawling del objetivo
 * @param url - URL objetivo
 * @param workspaceId - ID del workspace
 * @param tool - Herramienta: 'katana' | 'gospider' | 'hakrawler' (default: 'katana')
 * @param depth - Profundidad del crawl (default: 3)
 * @returns Información del escaneo iniciado
 */
export const crawl = async (url: string, workspaceId: number, tool: string = 'katana', depth: number = 3) => {
  const response = await api.post('reconnaissance/crawl', {
    url,
    workspace_id: workspaceId,
    tool,
    depth
  })
  return response.data
}

/**
 * Obtiene URLs históricas de Wayback Machine
 * @param domain - Dominio objetivo
 * @param workspaceId - ID del workspace
 * @returns Información del escaneo iniciado
 */
export const wayback = async (domain: string, workspaceId: number) => {
  const response = await api.post('reconnaissance/wayback', {
    domain,
    workspace_id: workspaceId
  })
  return response.data
}

/**
 * Busca secrets/credentials en repositorios
 * @param repoUrl - URL del repositorio
 * @param workspaceId - ID del workspace
 * @param tool - Herramienta: 'gitleaks' | 'trufflehog' (default: 'gitleaks')
 * @returns Información del escaneo iniciado
 */
export const secrets = async (repoUrl: string, workspaceId: number, tool: string = 'gitleaks') => {
  const response = await api.post('reconnaissance/secrets', {
    repo_url: repoUrl,
    workspace_id: workspaceId,
    tool
  })
  return response.data
}

/**
 * Busca información en Shodan
 * @param query - Query de búsqueda Shodan
 * @param workspaceId - ID del workspace
 * @param apiKey - API key de Shodan (opcional)
 * @returns Información del escaneo iniciado
 */
export const shodan = async (query: string, workspaceId: number, apiKey?: string) => {
  const response = await api.post('reconnaissance/shodan', {
    query,
    workspace_id: workspaceId,
    api_key: apiKey
  })
  return response.data
}

/**
 * Ejecuta reconocimiento completo del objetivo
 * @param target - Objetivo a reconocer completamente
 * @param workspaceId - ID del workspace
 * @param includeAdvanced - Incluir herramientas avanzadas (default: false)
 * @returns Información de todos los escaneos iniciados
 */
export const complete = async (target: string, workspaceId: number, includeAdvanced: boolean = false) => {
  const response = await api.post('reconnaissance/complete', {
    target,
    workspace_id: workspaceId,
    include_advanced: includeAdvanced
  })
  return response.data
}

/**
 * Obtiene el estado de un escaneo
 * @param scanId - ID del escaneo
 * @returns Estado del escaneo
 */
export const getScanStatus = async (scanId: number) => {
  const response = await api.get(`reconnaissance/scans/${scanId}`)
  return response.data
}

/**
 * Obtiene resultados parseados de un escaneo
 * @param scanId - ID del escaneo
 * @returns Resultados del escaneo
 */
export const getScanResults = async (scanId: number) => {
  const response = await api.get(`reconnaissance/scans/${scanId}/results`)
  return response.data
}

/**
 * Obtiene el último resultado de reconocimiento (compatibilidad hacia atrás)
 * @returns Último resultado encontrado o mensaje si no existe
 */
export const ultimo = async (): Promise<ReconLastResult> => {
  const response = await api.get<ReconLastResult>('reconnaissance/ultimo')
  return response.data
}

/**
 * Lista todas las sesiones de reconocimiento (compatibilidad hacia atrás)
 * @returns Array de sesiones de reconocimiento
 */
export const sessions = async (): Promise<ReconSession[]> => {
  const response = await api.get<{ sessions: ReconSession[] }>('reconnaissance/sessions')
  return response.data.sessions
}

/**
 * Busca subdominios usando Certificate Transparency (crt.sh)
 * @param domain - Dominio objetivo
 * @param workspaceId - ID del workspace
 * @returns Información del escaneo iniciado
 */
export const crtsh = async (domain: string, workspaceId: number) => {
  const response = await api.post('reconnaissance/crtsh', {
    domain,
    workspace_id: workspaceId
  })
  return response.data
}

/**
 * Enumeración de subdominios con Findomain
 * @param domain - Dominio objetivo
 * @param workspaceId - ID del workspace
 * @param resolversFile - Archivo de resolvers DNS (opcional)
 * @returns Información del escaneo iniciado
 */
export const findomain = async (domain: string, workspaceId: number, resolversFile?: string) => {
  const response = await api.post('reconnaissance/findomain', {
    domain,
    workspace_id: workspaceId,
    resolvers_file: resolversFile
  })
  return response.data
}

/**
 * Busca información en Censys
 * @param query - Query de búsqueda
 * @param workspaceId - ID del workspace
 * @param indexType - Tipo de índice ('hosts' o 'certificates', default: 'hosts')
 * @param apiId - API ID de Censys (opcional)
 * @param apiSecret - API Secret de Censys (opcional)
 * @returns Información del escaneo iniciado
 */
export const censys = async (
  query: string,
  workspaceId: number,
  indexType: string = 'hosts',
  apiId?: string,
  apiSecret?: string
) => {
  const response = await api.post('reconnaissance/censys', {
    query,
    workspace_id: workspaceId,
    index_type: indexType,
    api_id: apiId,
    api_secret: apiSecret
  })
  return response.data
}

/**
 * Consultas DNS simples con host o nslookup
 * @param domain - Dominio objetivo
 * @param workspaceId - ID del workspace
 * @param tool - Herramienta: 'host' | 'nslookup' (default: 'host')
 * @param recordType - Tipo de registro (A, MX, NS, TXT, SOA, etc.)
 * @param dnsServer - Servidor DNS específico (opcional)
 * @returns Información del escaneo iniciado
 */
export const dnsLookup = async (
  domain: string,
  workspaceId: number,
  tool: string = 'host',
  recordType?: string,
  dnsServer?: string
) => {
  const response = await api.post('reconnaissance/dns-lookup', {
    domain,
    workspace_id: workspaceId,
    tool,
    record_type: recordType,
    dns_server: dnsServer
  })
  return response.data
}

/**
 * Mapeo de ruta de red con traceroute
 * @param target - IP o dominio objetivo
 * @param workspaceId - ID del workspace
 * @param protocol - Protocolo: 'icmp' | 'tcp' | 'udp' (default: 'icmp')
 * @param maxHops - Número máximo de saltos (default: 30)
 * @returns Información del escaneo iniciado
 */
export const traceroute = async (
  target: string,
  workspaceId: number,
  protocol: string = 'icmp',
  maxHops: number = 30
) => {
  const response = await api.post('reconnaissance/traceroute', {
    target,
    workspace_id: workspaceId,
    protocol,
    max_hops: maxHops
  })
  return response.data
}

/**
 * Google Dorks - búsquedas avanzadas en Google
 * @param domain - Dominio objetivo
 * @param workspaceId - ID del workspace
 * @param dorkQuery - Query de dork personalizado (opcional, para modo manual)
 * @param tool - Herramienta: 'manual' | 'goofuzz' | 'pagodo' | 'dorkscanner' (default: 'manual')
 * @returns Información del escaneo iniciado
 */
export const googleDorks = async (
  domain: string,
  workspaceId: number,
  dorkQuery?: string,
  tool: string = 'manual'
) => {
  const response = await api.post('reconnaissance/google-dorks', {
    domain,
    workspace_id: workspaceId,
    dork_query: dorkQuery,
    tool
  })
  return response.data
}

/**
 * Hunter.io - búsqueda de emails corporativos
 * @param domain - Dominio objetivo
 * @param workspaceId - ID del workspace
 * @param apiKey - API key de Hunter.io (opcional, puede estar en env)
 * @returns Información del escaneo iniciado
 */
export const hunterIo = async (
  domain: string,
  workspaceId: number,
  apiKey?: string
) => {
  const response = await api.post('reconnaissance/hunter-io', {
    domain,
    workspace_id: workspaceId,
    api_key: apiKey
  })
  return response.data
}

/**
 * LinkedIn Enumeration - enumeración de empleados
 * @param domain - Dominio objetivo
 * @param workspaceId - ID del workspace
 * @param companyName - Nombre de la compañía (opcional)
 * @param tool - Herramienta: 'crosslinked' | 'linkedin2username' (default: 'crosslinked')
 * @returns Información del escaneo iniciado
 */
export const linkedinEnum = async (
  domain: string,
  workspaceId: number,
  companyName?: string,
  tool: string = 'crosslinked'
) => {
  const response = await api.post('reconnaissance/linkedin-enum', {
    domain,
    workspace_id: workspaceId,
    company_name: companyName,
    tool
  })
  return response.data
}

/**
 * Enumeración DNS con dnsenum o fierce
 * @param domain - Dominio objetivo
 * @param workspaceId - ID del workspace
 * @param tool - Herramienta: 'dnsenum' | 'fierce' (default: 'dnsenum')
 * @param wordlist - Archivo wordlist para bruteforce (opcional)
 * @returns Información del escaneo iniciado
 */
export const dnsEnumAlt = async (
  domain: string,
  workspaceId: number,
  tool: string = 'dnsenum',
  wordlist?: string
) => {
  const response = await api.post('reconnaissance/dns-enum-alt', {
    domain,
    workspace_id: workspaceId,
    tool,
    wordlist
  })
  return response.data
}

/**
 * Objeto API de reconocimiento
 * Agrupa todas las funciones de reconocimiento
 */
export const reconnaissanceAPI = {
  whois,
  dnsEnum,
  subdomains,
  subdomainEnum: subdomains, // Alias para compatibilidad
  emails,
  crawl,
  wayback,
  secrets,
  shodan,
  complete,
  getScanStatus,
  getScanResults,
  ultimo,
  sessions,
  crtsh,
  findomain,
  censys,
  dnsLookup,
  traceroute,
  dnsEnumAlt,
  googleDorks,
  hunterIo,
  linkedinEnum
}


