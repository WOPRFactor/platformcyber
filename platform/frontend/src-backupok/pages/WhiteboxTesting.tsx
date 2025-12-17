import React, { useState } from 'react'
import { Search, Eye } from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { whiteboxAPI } from '../lib/api/whitebox'
import { toast } from 'sonner'
import { useAuth } from '../contexts/AuthContext'
import { WhiteboxTabs } from './WhiteboxTesting/components/WhiteboxTabs'
import { AnalysisConfig } from './WhiteboxTesting/components/AnalysisConfig'
import { CodeAnalysisSection } from './WhiteboxTesting/components/CodeAnalysisSection'
import { DependencyAnalysisSection } from './WhiteboxTesting/components/DependencyAnalysisSection'
import { SecretsDetectionSection } from './WhiteboxTesting/components/SecretsDetectionSection'
import { ConfigAnalysisSection } from './WhiteboxTesting/components/ConfigAnalysisSection'
import { ComprehensiveAnalysisSection } from './WhiteboxTesting/components/ComprehensiveAnalysisSection'
import { SessionsHistory } from './WhiteboxTesting/components/SessionsHistory'

const WhiteboxTesting: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const [activeTab, setActiveTab] = useState('code_analysis')
  const [targetPath, setTargetPath] = useState('')
  const [language, setLanguage] = useState('auto')
  const [packageManager, setPackageManager] = useState('auto')
  const [scanners, setScanners] = useState(['patterns', 'entropy', 'known_keys'])
  const [configTypes, setConfigTypes] = useState(['web_servers', 'databases', 'permissions', 'encryption'])

  const queryClient = useQueryClient()

  // Queries
  const { data: sessions, isLoading: sessionsLoading } = useQuery({
    queryKey: ['whitebox_sessions'],
    queryFn: whiteboxAPI.getWhiteboxSessions,
    enabled: isAuthenticated,
    refetchInterval: 10000,
  })

  // Mutations
  const codeAnalysisMutation = useMutation({
    mutationFn: (data: { targetPath: string; language?: string; rules?: string }) =>
      whiteboxAPI.codeAnalysis(data.targetPath, data.language, data.rules),
    onSuccess: (data) => {
      if (data.success) {
        toast.success(`Análisis de código completado: ${data.data.summary.total_findings} hallazgos`)
        queryClient.invalidateQueries({ queryKey: ['whitebox_sessions'] })
      } else {
        toast.error('Error en análisis de código')
      }
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`)
    }
  })

  const dependencyAnalysisMutation = useMutation({
    mutationFn: (data: { targetPath: string; packageManager?: string }) =>
      whiteboxAPI.dependencyAnalysis(data.targetPath, data.packageManager),
    onSuccess: (data) => {
      if (data.success) {
        toast.success(`Análisis de dependencias completado: ${data.data.summary.total_vulnerable} vulnerables`)
        queryClient.invalidateQueries({ queryKey: ['whitebox_sessions'] })
      } else {
        toast.error('Error en análisis de dependencias')
      }
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`)
    }
  })

  const secretsDetectionMutation = useMutation({
    mutationFn: (data: { targetPath: string; scanners?: string[] }) =>
      whiteboxAPI.secretsDetection(data.targetPath, data.scanners),
    onSuccess: (data) => {
      if (data.success) {
        toast.success(`Detección de secrets completada: ${data.data.summary.total_secrets} encontrados`)
        queryClient.invalidateQueries({ queryKey: ['whitebox_sessions'] })
      } else {
        toast.error('Error en detección de secrets')
      }
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`)
    }
  })

  const configAnalysisMutation = useMutation({
    mutationFn: (data: { targetPath: string; configTypes?: string[] }) =>
      whiteboxAPI.configurationAnalysis(data.targetPath, data.configTypes),
    onSuccess: (data) => {
      if (data.success) {
        toast.success(`Análisis de configuración completado: ${data.data.summary.total_issues} problemas`)
        queryClient.invalidateQueries({ queryKey: ['whitebox_sessions'] })
      } else {
        toast.error('Error en análisis de configuración')
      }
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`)
    }
  })

  const comprehensiveAnalysisMutation = useMutation({
    mutationFn: (data: { targetPath: string; options?: any }) =>
      whiteboxAPI.comprehensiveWhitebox(data.targetPath, data.options),
    onSuccess: (data) => {
      toast.success(`Análisis completo completado: ${data.summary.total_findings} hallazgos en ${data.summary.successful_phases} fases`)
      queryClient.invalidateQueries({ queryKey: ['whitebox_sessions'] })
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`)
    }
  })

  const handleAnalysis = (analysisType: string) => {
    if (!targetPath.trim()) {
      toast.error('Por favor ingrese una ruta de destino válida')
      return
    }

    switch (analysisType) {
      case 'code':
        codeAnalysisMutation.mutate({
          targetPath,
          language: language === 'auto' ? undefined : language
        })
        break
      case 'dependency':
        dependencyAnalysisMutation.mutate({
          targetPath,
          packageManager: packageManager === 'auto' ? undefined : packageManager
        })
        break
      case 'secrets':
        secretsDetectionMutation.mutate({
          targetPath,
          scanners
        })
        break
      case 'config':
        configAnalysisMutation.mutate({
          targetPath,
          configTypes
        })
        break
      case 'comprehensive':
        comprehensiveAnalysisMutation.mutate({ targetPath })
        break
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Whitebox Testing</h1>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Search className="w-4 h-4" />
          Análisis de código fuente y configuraciones
        </div>
      </div>

      {/* Advertencia de whitebox testing */}
      <div className="border border-blue-500 bg-blue-50 p-6 rounded-xl">
        <div className="flex items-center gap-2 mb-4">
          <Eye className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-bold text-blue-800">WHITEBOX TESTING - ACCESO INTERNO</h2>
        </div>
        <div className="text-blue-700 space-y-2">
          <p>• <strong>Requiere acceso completo al código fuente</strong> de la aplicación objetivo</p>
          <p>• <strong>Ideal para desarrollo seguro</strong> y revisiones de código internas</p>
          <p>• <strong>Detecta vulnerabilidades</strong> antes del despliegue en producción</p>
          <p>• <strong>Análisis estático</strong> de dependencias, configuraciones y código fuente</p>
        </div>
      </div>

      {/* Configuración del análisis */}
      <AnalysisConfig
        targetPath={targetPath}
        language={language}
        packageManager={packageManager}
        scanners={scanners}
        configTypes={configTypes}
        onTargetPathChange={setTargetPath}
        onLanguageChange={setLanguage}
        onPackageManagerChange={setPackageManager}
        onScannersChange={setScanners}
        onConfigTypesChange={setConfigTypes}
      />

      {/* Tipos de análisis */}
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Análisis Disponibles</h2>
          <p className="text-gray-500">
            Seleccione el tipo de análisis whitebox a realizar
          </p>
        </div>

        <div className="w-full">
          <WhiteboxTabs activeTab={activeTab} setActiveTab={setActiveTab} />

          {activeTab === 'code_analysis' && (
            <CodeAnalysisSection
              mutation={codeAnalysisMutation}
              onExecute={() => handleAnalysis('code')}
            />
          )}

          {activeTab === 'dependency_analysis' && (
            <DependencyAnalysisSection
              mutation={dependencyAnalysisMutation}
              onExecute={() => handleAnalysis('dependency')}
            />
          )}

          {activeTab === 'secrets_detection' && (
            <SecretsDetectionSection
              mutation={secretsDetectionMutation}
              onExecute={() => handleAnalysis('secrets')}
            />
          )}

          {activeTab === 'config_analysis' && (
            <ConfigAnalysisSection
              mutation={configAnalysisMutation}
              onExecute={() => handleAnalysis('config')}
            />
          )}

          {activeTab === 'comprehensive' && (
            <ComprehensiveAnalysisSection
              mutation={comprehensiveAnalysisMutation}
              onExecute={() => handleAnalysis('comprehensive')}
            />
          )}
        </div>
      </div>

      {/* Historial de sesiones */}
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Historial de Análisis</h2>
          <p className="text-gray-500">
            Sesiones de análisis whitebox realizadas
          </p>
        </div>
        <SessionsHistory sessions={sessions} isLoading={sessionsLoading} />
      </div>
    </div>
  )
}

export default WhiteboxTesting
