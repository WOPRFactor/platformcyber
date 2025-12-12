/**
 * Integrations Page
 * =================
 * 
 * Página de integraciones avanzadas con herramientas de seguridad.
 * 
 * Características:
 * - Integración con Metasploit Framework
 * - Integración con Burp Suite Professional
 * - Escaneos avanzados con Nmap, SQLMap y Gobuster
 * - Historial de sesiones de integraciones
 * 
 * Refactorizado: 2025-12-04
 */

import React, { useState } from 'react'
import { Zap, AlertTriangle } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../contexts/AuthContext'
import { IntegrationTabs } from './Integrations/components/shared/IntegrationTabs'
import { IntegrationHistory } from './Integrations/components/shared/IntegrationHistory'
import { MetasploitSection } from './Integrations/components/integrations/MetasploitSection'
import { BurpSection } from './Integrations/components/integrations/BurpSection'
import { NmapSection } from './Integrations/components/integrations/NmapSection'
import { SQLMapSection } from './Integrations/components/integrations/SQLMapSection'
import { GobusterSection } from './Integrations/components/integrations/GobusterSection'
import { integrationsAPI } from '../lib/api/integrations'

const Integrations: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const hasToken = !!localStorage.getItem('access_token')
  const [activeTab, setActiveTab] = useState('metasploit')

  const { data: integrationSessions, isLoading: sessionsLoading } = useQuery({
    queryKey: ['integration_sessions'],
    queryFn: integrationsAPI.getIntegrationSessions,
    enabled: isAuthenticated && hasToken,
    refetchInterval: (isAuthenticated && hasToken) ? 10000 : false,
  })

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-red-400">Debes iniciar sesión para acceder a esta página</p>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Integraciones Avanzadas</h1>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Zap className="w-4 h-4" />
          Metasploit, Burp Suite & Herramientas Avanzadas
        </div>
      </div>

      {/* Advertencia de integraciones avanzadas */}
      <div className="border border-yellow-500 bg-yellow-50 p-6 rounded-xl">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-6 h-6 text-yellow-600" />
          <h2 className="text-xl font-bold text-yellow-800">INTEGRACIONES DE ALTO RIESGO</h2>
        </div>
        <div className="text-yellow-700 space-y-2">
          <p>• <strong>Metasploit Framework:</strong> Solo para uso autorizado en entornos de testing controlados</p>
          <p>• <strong>Burp Suite Professional:</strong> Requiere licencia válida y configuración correcta</p>
          <p>• <strong>Herramientas de escaneo avanzado:</strong> Pueden ser detectadas por sistemas de seguridad</p>
          <p>• <strong>Configuración requerida:</strong> Verifica que los servicios estén ejecutándose antes de usar</p>
        </div>
      </div>

      {/* Pestañas principales */}
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Herramientas de Integración</h2>
          <p className="text-gray-500">
            Seleccione la herramienta de integración a utilizar
          </p>
        </div>

        <div className="w-full">
          <IntegrationTabs activeTab={activeTab} setActiveTab={setActiveTab} />

          {/* Contenido de cada tab */}
          {activeTab === 'metasploit' && <MetasploitSection />}
          {activeTab === 'burp' && <BurpSection />}
          {activeTab === 'nmap' && <NmapSection />}
          {activeTab === 'sqlmap' && <SQLMapSection />}
          {activeTab === 'gobuster' && <GobusterSection />}
        </div>
      </div>

      {/* Historial de sesiones */}
      <IntegrationHistory sessions={integrationSessions} isLoading={sessionsLoading} />
    </div>
  )
}

export default Integrations
