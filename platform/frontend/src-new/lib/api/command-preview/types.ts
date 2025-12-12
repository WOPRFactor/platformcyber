/**
 * Command Preview Types
 * ======================
 * 
 * Tipos compartidos para command preview API.
 */

import { CommandPreview } from '../../../components/CommandPreviewModal'

export interface PreviewRequest {
  workspace_id: number
  [key: string]: any
}

export type CommandPreviewResponse = CommandPreview


