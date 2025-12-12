/**
 * useCommandPreview Hook
 * =======================
 * 
 * Hook reutilizable para manejar preview de comandos antes de ejecutarlos.
 * Simplifica la integración del preview en todas las páginas.
 */

import { useState } from 'react'
import { toast } from 'sonner'
import { CommandPreview } from '../components/CommandPreviewModal'

interface UseCommandPreviewOptions {
  onExecute: (parameters: Record<string, any>) => Promise<void>
  toolName: string
  category: string
}

export function useCommandPreview({ onExecute, toolName, category }: UseCommandPreviewOptions) {
  const [showPreview, setShowPreview] = useState(false)
  const [previewData, setPreviewData] = useState<CommandPreview | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const showPreviewModal = async (previewFn: () => Promise<CommandPreview>) => {
    try {
      setIsLoading(true)
      const preview = await previewFn()
      setPreviewData(preview)
      setShowPreview(true)
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
      // NO ejecutar el comando automáticamente - el usuario debe confirmar desde el preview
    } finally {
      setIsLoading(false)
    }
  }

  const handleExecuteFromPreview = async (parameters: Record<string, any>) => {
    setShowPreview(false)
    try {
      await onExecute(parameters)
    } catch (error: any) {
      toast.error('Error al ejecutar comando')
    }
  }

  const closePreview = () => {
    setShowPreview(false)
    setPreviewData(null)
  }

  return {
    showPreview,
    previewData,
    isLoading,
    showPreviewModal,
    handleExecuteFromPreview,
    closePreview,
    toolName,
    category
  }
}




