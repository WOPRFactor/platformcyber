import React, { useState } from 'react'
import { Brain, Bot, TrendingUp, Code, FileText } from 'lucide-react'
import { useIAMutations } from './IA/hooks/useIAMutations'
import IATabs from './IA/components/IATabs'
import ChatbotTab from './IA/components/ChatbotTab'
import PredictiveTab from './IA/components/PredictiveTab'
import PayloadsTab from './IA/components/PayloadsTab'
import ReportsTab from './IA/components/ReportsTab'
import LegacyTab from './IA/components/LegacyTab'

const IA: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chatbot' | 'predictive' | 'payloads' | 'reports' | 'legacy'>('chatbot')
  const [chatHistory, setChatHistory] = useState<any[]>([])
  const [payloadData, setPayloadData] = useState({
    target_os: 'linux',
    vulnerability_type: '',
    delivery_method: 'remote',
    evasion_techniques: [] as string[]
  })
  const [reportData, setReportData] = useState({
    content: '',
    type: 'vulnerability_scan',
    target_info: {}
  })

  const {
    chatbotMutation,
    payloadMutation,
    reportAnalysisMutation,
    predictiveAnalysisMutation,
    analyzeMutation,
    commandMutation,
    predictiveMutation,
    isAnyLoading
  } = useIAMutations()

  const handleChatbotMessage = (message: string) => {
    chatbotMutation.mutate({
      message,
      context: {
        session_id: 'web_session',
        user_role: 'analyst',
        current_phase: 'analysis'
      }
    }, {
      onSuccess: (data) => {
        setChatHistory(prev => [...prev, {
          user: message,
          assistant: data.response,
          timestamp: new Date().toISOString()
        }])
      }
    })
  }

  const handlePayloadGeneration = () => {
    payloadMutation.mutate(payloadData)
  }

  const handleReportAnalysis = () => {
    if (!reportData.content.trim()) return
    reportAnalysisMutation.mutate(reportData)
  }

  const handlePredictiveAnalysis = () => {
    predictiveAnalysisMutation.mutate({
      target: '192.168.1.100',
      scan_results: ['port 80 open', 'service http'],
      historical_data: ['previous scan showed vulnerable service']
    })
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900 text-gray-900">
          🤖 Inteligencia Artificial Avanzada
        </h1>
        <p className="text-gray-500 mt-2">
          Sistema completo de IA para pentesting: Chatbot contextual, análisis predictivo, generación de payloads y más
        </p>
      </div>

      {/* Pestañas principales */}
      <div className="card">
        <IATabs activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Contenido según pestaña */}
        {activeTab === 'chatbot' && (
          <ChatbotTab
            chatHistory={chatHistory}
            onSendMessage={handleChatbotMessage}
            chatbotMutation={chatbotMutation}
          />
        )}

        {activeTab === 'predictive' && (
          <PredictiveTab
            onAnalyze={handlePredictiveAnalysis}
            predictiveAnalysisMutation={predictiveAnalysisMutation}
          />
        )}

        {activeTab === 'payloads' && (
          <PayloadsTab
            payloadData={payloadData}
            setPayloadData={setPayloadData}
            onGenerate={handlePayloadGeneration}
            payloadMutation={payloadMutation}
          />
        )}

        {activeTab === 'reports' && (
          <ReportsTab
            reportData={reportData}
            setReportData={setReportData}
            onAnalyze={handleReportAnalysis}
            reportAnalysisMutation={reportAnalysisMutation}
          />
        )}

        {activeTab === 'legacy' && (
          <LegacyTab
            analyzeMutation={analyzeMutation}
            commandMutation={commandMutation}
            predictiveMutation={predictiveMutation}
            isAnyLoading={isAnyLoading}
          />
        )}
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Historial de Consultas IA
        </h2>
        <div className="text-center py-8 text-gray-500">
          <Brain size={48} className="mx-auto mb-4 opacity-50" />
          <p>No hay consultas recientes</p>
          <p className="text-sm">Las consultas aparecerán aquí</p>
        </div>
      </div>
    </div>
  )
}

export default IA


