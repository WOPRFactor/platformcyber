/**
 * Command Preview Helpers
 * =======================
 * 
 * Helpers genéricos para manejar previews de comandos de manera uniforme.
 * Simplifica la integración del preview en todas las páginas.
 */

import { toast } from 'sonner'
import { commandPreviewAPI, CommandPreview } from '../lib/api/command-preview'

interface PreviewConfig {
  apiFunction: (params: any) => Promise<CommandPreview>
  params: Record<string, any>
  toolName: string
  executeFn: (params: Record<string, any>) => Promise<void>
}

/**
 * Helper genérico para mostrar preview antes de ejecutar
 */
export async function showCommandPreview(
  config: PreviewConfig,
  onPreviewReady: (preview: CommandPreview) => void,
  onError?: () => void
): Promise<void> {
  try {
    const preview = await config.apiFunction(config.params)
    onPreviewReady(preview)
  } catch (error: any) {
    console.error('Error obteniendo preview:', error)
    toast.error('Error al obtener preview del comando')
    if (onError) {
      onError()
    } else {
      // Fallback: ejecutar sin preview
      await config.executeFn(config.params)
    }
  }
}

/**
 * Mapeo de herramientas a funciones de preview API
 */
export const previewApiMap: Record<string, (params: any) => Promise<CommandPreview>> = {
  // Reconnaissance
  'subdomain_enum': commandPreviewAPI.previewSubdomainEnum,
  'whois': commandPreviewAPI.previewWhois,
  'dns_recon': commandPreviewAPI.previewDnsRecon,
  'findomain': commandPreviewAPI.previewFindomain,
  'crtsh': commandPreviewAPI.previewCrtsh,
  'email_harvest': commandPreviewAPI.previewEmailHarvest,
  'web_crawl': commandPreviewAPI.previewWebCrawl,
  'shodan': commandPreviewAPI.previewShodan,
  'censys': commandPreviewAPI.previewCensys,
  'wayback': commandPreviewAPI.previewWayback,
  'secrets': commandPreviewAPI.previewSecrets,
  'google_dorks': commandPreviewAPI.previewGoogleDorks,
  
  // Scanning
  'nmap': commandPreviewAPI.previewNmapScan,
  'rustscan': commandPreviewAPI.previewRustscan,
  'masscan': commandPreviewAPI.previewMasscan,
  'naabu': commandPreviewAPI.previewNaabu,
  
  // Vulnerability
  'nuclei': commandPreviewAPI.previewNucleiScan,
  'nikto': commandPreviewAPI.previewNiktoScan,
  'sqlmap': commandPreviewAPI.previewSqlmap,
  'zap': commandPreviewAPI.previewZap,
  'testssl': commandPreviewAPI.previewTestssl,
  'whatweb': commandPreviewAPI.previewWhatweb,
  'dalfox': commandPreviewAPI.previewDalfox,
  
  // Exploitation
  'hydra': commandPreviewAPI.previewHydra
}

/**
 * Helper para crear handler con preview automático
 */
export function createPreviewHandler(
  toolKey: string,
  params: Record<string, any>,
  executeFn: (params: Record<string, any>) => Promise<void>,
  onPreviewReady: (preview: CommandPreview) => void
) {
  return async () => {
    const previewFn = previewApiMap[toolKey]
    if (!previewFn) {
      // Si no hay preview disponible, ejecutar directamente
      await executeFn(params)
      return
    }
    
    await showCommandPreview(
      {
        apiFunction: previewFn,
        params,
        toolName: toolKey,
        executeFn
      },
      onPreviewReady,
      () => executeFn(params) // Fallback
    )
  }
}

