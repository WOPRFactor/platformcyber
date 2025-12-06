/**
 * Legacy Tab Component
 * ====================
 * 
 * Componente para la pestaña de funciones legacy de IA.
 */

import React, { useState } from 'react'
import { Brain, MessageSquare, Lightbulb, Send, CheckCircle, XCircle, Loader } from 'lucide-react'
import { UseMutationResult } from '@tanstack/react-query'

interface LegacyTabProps {
  analyzeMutation: UseMutationResult<any, any, any>
  commandMutation: UseMutationResult<any, any, any>
  predictiveMutation: UseMutationResult<any, any, any>
  isAnyLoading: boolean
}

const LegacyTab: React.FC<LegacyTabProps> = ({
  analyzeMutation,
  commandMutation,
  predictiveMutation,
  isAnyLoading
}) => {
  const [query, setQuery] = useState('')
  const [aiProvider, setAiProvider] = useState<'deepseek' | 'gemini' | 'ollama'>('deepseek')

  const handleAnalyze = () => {
    if (!query.trim()) return
    analyzeMutation.mutate({ query })
  }

  const handleCommandSuggestion = () => {
    if (!query.trim()) return
    commandMutation.mutate({ intent: query })
  }

  const handlePredictiveAnalysis = () => {
    predictiveMutation.mutate({ target: '192.168.1.100' })
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-green-400 mb-6 flex items-center space-x-2">
        <Brain size={20} />
        <span>Funciones de IA Legacy</span>
      </h2>

      {/* Formulario de consulta */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-green-400 mb-2">
            Describe tu consulta o análisis
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="input w-full h-32 resize-none"
            placeholder="Ej: Analiza vulnerabilidades en este resultado de escaneo, sugiere comandos para explotación, etc."
          />
        </div>

        {/* Mensajes de estado */}
        {analyzeMutation.isSuccess && (
          <div className="flex items-center space-x-2 text-green-400 bg-green-900/20 border border-green-500 rounded p-3">
            <CheckCircle size={16} />
            <span>Análisis completado exitosamente</span>
          </div>
        )}

        {analyzeMutation.isError && (
          <div className="flex items-center space-x-2 text-red-400 bg-red-900/20 border border-red-500 rounded p-3">
            <XCircle size={16} />
            <span>Error en el análisis IA</span>
          </div>
        )}

        <div className="flex space-x-4">
          <button
            onClick={handleAnalyze}
            disabled={!query.trim() || isAnyLoading}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50"
          >
            {analyzeMutation.isPending ? (
              <Loader size={18} className="animate-spin" />
            ) : (
              <Send size={18} />
            )}
            <span>{analyzeMutation.isPending ? 'Analizando...' : 'Analizar con IA'}</span>
          </button>

          <select
            value={aiProvider}
            onChange={(e) => setAiProvider(e.target.value as any)}
            className="input"
          >
            <option value="deepseek">DeepSeek (Recomendado)</option>
            <option value="gemini">Gemini</option>
            <option value="ollama">Ollama (Local)</option>
          </select>
        </div>
      </div>

      {/* Funciones disponibles */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <MessageSquare className="w-8 h-8 text-blue-400" />
            <h3 className="text-lg font-bold text-green-400">Análisis de Resultados</h3>
          </div>
          <p className="text-sm text-green-600 mb-4">
            Analiza automáticamente los resultados de escaneos y proporciona insights inteligentes.
          </p>
          <button
            onClick={handleAnalyze}
            disabled={!query.trim() || isAnyLoading}
            className="btn-secondary w-full flex items-center justify-center space-x-2"
          >
            {analyzeMutation.isPending ? (
              <Loader size={16} className="animate-spin" />
            ) : (
              <MessageSquare size={16} />
            )}
            <span>
              {analyzeMutation.isPending ? 'Analizando...' : 'Analizar Resultados'}
            </span>
          </button>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <Lightbulb className="w-8 h-8 text-yellow-400" />
            <h3 className="text-lg font-bold text-green-400">Sugerencias de Comando</h3>
          </div>
          <p className="text-sm text-green-600 mb-4">
            Obtén recomendaciones inteligentes para comandos y estrategias de pentesting.
          </p>
          <button
            onClick={handleCommandSuggestion}
            disabled={!query.trim() || isAnyLoading}
            className="btn-secondary w-full flex items-center justify-center space-x-2"
          >
            {commandMutation.isPending ? (
              <Loader size={16} className="animate-spin" />
            ) : (
              <Lightbulb size={16} />
            )}
            <span>
              {commandMutation.isPending ? 'Generando...' : 'Obtener Sugerencias'}
            </span>
          </button>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <Brain className="w-8 h-8 text-purple-400" />
            <h3 className="text-lg font-bold text-green-400">Análisis Predictivo</h3>
          </div>
          <p className="text-sm text-green-600 mb-4">
            Predice posibles vulnerabilidades y recomienda acciones preventivas.
          </p>
          <button
            onClick={handlePredictiveAnalysis}
            disabled={isAnyLoading}
            className="btn-secondary w-full flex items-center justify-center space-x-2"
          >
            {predictiveMutation.isPending ? (
              <Loader size={16} className="animate-spin" />
            ) : (
              <Brain size={16} />
            )}
            <span>
              {predictiveMutation.isPending ? 'Analizando...' : 'Análisis Predictivo'}
            </span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default LegacyTab


