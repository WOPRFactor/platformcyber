/**
 * Chatbot Tab Component
 * =====================
 * 
 * Componente para la pestaña de chatbot contextual.
 */

import React, { useState } from 'react'
import { Bot, Send, Loader } from 'lucide-react'
import { UseMutationResult } from '@tanstack/react-query'

interface ChatbotTabProps {
  chatHistory: any[]
  onSendMessage: (message: string) => void
  chatbotMutation: UseMutationResult<any, any, any>
}

const ChatbotTab: React.FC<ChatbotTabProps> = ({ chatHistory, onSendMessage, chatbotMutation }) => {
  const [chatMessage, setChatMessage] = useState('')

  const handleSend = () => {
    if (!chatMessage.trim() || chatbotMutation.isPending) return
    onSendMessage(chatMessage)
    setChatMessage('')
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center space-x-2">
        <Bot size={20} />
        <span>Chatbot Contextual IA</span>
      </h2>

      {/* Historial de chat */}
      <div className="bg-gray-50 border border-gray-200/20 rounded-xl p-4 mb-4 max-h-96 overflow-y-auto">
        {chatHistory.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Bot size={48} className="mx-auto mb-4 opacity-50" />
            <p>¡Hola! Soy tu asistente de IA especializado en pentesting.</p>
            <p className="text-sm">Pregúntame sobre vulnerabilidades, comandos, estrategias o cualquier tema de ciberseguridad.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {chatHistory.map((msg, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-start space-x-2">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">👤</span>
                  </div>
                  <div className="bg-blue-900/50 p-3 rounded-xl flex-1">
                    <p className="text-blue-200">{msg.user}</p>
                  </div>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-8 h-8 bg-red-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">🤖</span>
                  </div>
                  <div className="bg-white border border-gray-200 p-3 rounded-xl flex-1">
                    <p className="text-gray-700 whitespace-pre-wrap">{msg.assistant}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Input de mensaje */}
      <div className="flex space-x-2">
        <input
          type="text"
          value={chatMessage}
          onChange={(e) => setChatMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          className="input flex-1"
          placeholder="Escribe tu consulta sobre pentesting..."
        />
        <button
          onClick={handleSend}
          disabled={!chatMessage.trim() || chatbotMutation.isPending}
          className="btn-primary flex items-center space-x-2 disabled:opacity-50"
        >
          {chatbotMutation.isPending ? (
            <Loader size={18} className="animate-spin" />
          ) : (
            <Send size={18} />
          )}
          <span>Enviar</span>
        </button>
      </div>
    </div>
  )
}

export default ChatbotTab


