/**
 * Command Preview API Client
 * ===========================
 * 
 * Cliente unificado para obtener previews de comandos antes de ejecutarlos.
 * 
 * Refactorizado: 2025-12-04
 * Dividido en módulos por categoría para mejor mantenibilidad.
 */

import { reconnaissancePreviews } from './reconnaissance'
import { scanningPreviews } from './scanning'
import { vulnerabilityPreviews } from './vulnerability'
import { exploitationPreviews } from './exploitation'
import { previewCloudAPI as cloudPreviews } from './cloud/cloud'
import { previewContainerAPI as containerPreviews } from './container/container'
import { previewActiveDirectoryAPI as activeDirectoryPreviews } from './activeDirectory/activeDirectory'
import { CommandPreview } from '../../../components/CommandPreviewModal'

export interface PreviewRequest {
  workspace_id: number
  [key: string]: any
}

// Exportar tipos
export type { CommandPreview }

// API unificada que combina todos los módulos
export const commandPreviewAPI = {
  // Reconnaissance
  ...reconnaissancePreviews,
  
  // Scanning
  ...scanningPreviews,
  
  // Vulnerability
  ...vulnerabilityPreviews,
  
  // Exploitation
  ...exploitationPreviews,
  
  // Cloud
  ...cloudPreviews,
  
  // Container
  ...containerPreviews,
  
  // Active Directory
  ...activeDirectoryPreviews
}

// Exportar módulos individuales para uso específico
export { 
  reconnaissancePreviews, 
  scanningPreviews, 
  vulnerabilityPreviews, 
  exploitationPreviews,
  cloudPreviews,
  containerPreviews,
  activeDirectoryPreviews
}


