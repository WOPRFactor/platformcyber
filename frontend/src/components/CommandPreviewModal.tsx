/**
 * Command Preview Modal
 * =====================
 * 
 * Componente modal para mostrar y editar comandos antes de ejecutarlos.
 * Permite al usuario:
 * - Ver el comando completo que se ejecutará
 * - Editar parámetros antes de ejecutar
 * - Ejecutar o cancelar
 */

import React, { useState, useEffect } from 'react'
import { X, Play, Edit2, AlertTriangle, Info } from 'lucide-react'
import { toast } from 'react-hot-toast'

export interface CommandPreview {
  command: string[]
  command_string: string
  parameters: Record<string, any>
  estimated_timeout: number
  output_file: string
  warnings?: string[]
  suggestions?: string[]
}

interface CommandPreviewModalProps {
  isOpen: boolean
  onClose: () => void
  onExecute: (parameters: Record<string, any>) => void
  previewData: CommandPreview | null
  isLoading?: boolean
  toolName: string
  category: string
}

const CommandPreviewModal: React.FC<CommandPreviewModalProps> = ({
  isOpen,
  onClose,
  onExecute,
  previewData,
  isLoading = false,
  toolName,
  category
}) => {
  const [editedParameters, setEditedParameters] = useState<Record<string, any>>({})
  const [isEditing, setIsEditing] = useState(false)

  // Inicializar editedParameters cuando cambia previewData
  useEffect(() => {
    if (previewData) {
      setEditedParameters(previewData.parameters)
      setIsEditing(false)
    }
  }, [previewData])

  // Debug: Log cuando el modal debería mostrarse
  React.useEffect(() => {
    if (isOpen && previewData) {
      console.log('🔍 CommandPreviewModal: Abriendo modal', {
        toolName,
        category,
        command: previewData.command_string,
        hasData: !!previewData
      })
    } else if (isOpen && !previewData) {
      console.warn('⚠️ CommandPreviewModal: isOpen=true pero previewData es null')
    }
  }, [isOpen, previewData, toolName, category])

  if (!isOpen || !previewData) {
    if (isOpen && !previewData) {
      console.warn('⚠️ CommandPreviewModal: No se renderiza porque previewData es null')
    }
    return null
  }

  const handleParameterChange = (key: string, value: any) => {
    setEditedParameters(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const handleExecute = () => {
    onExecute(editedParameters)
  }

  const formatTimeout = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
  }

  return (
    <div className="fixed inset-0 z-[10000] flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-gray-900 border border-gray-700 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700 bg-gray-800/50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600/20 rounded-lg">
              <Info className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Preview de Comando</h2>
              <p className="text-sm text-gray-400">{toolName} - {category}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            disabled={isLoading}
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Command String */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Comando que se ejecutará:
            </label>
            <div className="bg-gray-950 border border-gray-700 rounded-lg p-4 font-mono text-sm">
              <code className="text-green-400 break-all">
                {previewData.command_string}
              </code>
            </div>
          </div>

          {/* Parameters */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-medium text-gray-300">
                Parámetros:
              </label>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded-lg transition-colors"
              >
                <Edit2 className="w-4 h-4" />
                {isEditing ? 'Ver Solo' : 'Editar'}
              </button>
            </div>
            <div className="bg-gray-950 border border-gray-700 rounded-lg p-4 space-y-3">
              {Object.entries(previewData.parameters).map(([key, value]) => (
                <div key={key} className="flex items-center gap-3">
                  <label className="text-sm font-medium text-gray-400 w-32 flex-shrink-0">
                    {key}:
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editedParameters[key] || ''}
                      onChange={(e) => handleParameterChange(key, e.target.value)}
                      className="flex-1 px-3 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    <span className="flex-1 text-sm text-gray-300 font-mono">
                      {String(value)}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-950 border border-gray-700 rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">Timeout Estimado</div>
              <div className="text-sm font-medium text-gray-300">
                {formatTimeout(previewData.estimated_timeout)}
              </div>
            </div>
            <div className="bg-gray-950 border border-gray-700 rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-1">Archivo de Salida</div>
              <div className="text-sm font-mono text-gray-300 truncate">
                {previewData.output_file}
              </div>
            </div>
          </div>

          {/* Warnings */}
          {previewData.warnings && previewData.warnings.length > 0 && (
            <div className="bg-yellow-900/20 border border-yellow-700/50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-5 h-5 text-yellow-400" />
                <h3 className="text-sm font-medium text-yellow-400">Advertencias</h3>
              </div>
              <ul className="space-y-1">
                {previewData.warnings.map((warning, idx) => (
                  <li key={idx} className="text-sm text-yellow-300">• {warning}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Suggestions */}
          {previewData.suggestions && previewData.suggestions.length > 0 && (
            <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-5 h-5 text-blue-400" />
                <h3 className="text-sm font-medium text-blue-400">Sugerencias</h3>
              </div>
              <ul className="space-y-1">
                {previewData.suggestions.map((suggestion, idx) => (
                  <li key={idx} className="text-sm text-blue-300">• {suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-700 bg-gray-800/50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
            disabled={isLoading}
          >
            Cancelar
          </button>
          <button
            onClick={handleExecute}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="w-4 h-4" />
            {isLoading ? 'Ejecutando...' : 'Ejecutar Comando'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default CommandPreviewModal




