import React, { useState } from 'react'
import { FileText } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { reportingAPI } from '../lib/api/reporting'
import { toast } from 'sonner'
import { useReportingMutations } from './Reporting/hooks/useReportingMutations'
import ReportConfig from './Reporting/components/ReportConfig'
import ReportingTabs from './Reporting/components/ReportingTabs'
import ReportGenerator from './Reporting/components/ReportGenerator'
import GeneratedReport from './Reporting/components/GeneratedReport'
import ReportsHistory from './Reporting/components/ReportsHistory'

const Reporting: React.FC = () => {
  const [target, setTarget] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [complianceStandard, setComplianceStandard] = useState('general')
  const [exportFormat, setExportFormat] = useState<'json' | 'html' | 'pdf'>('html')
  const [activeTab, setActiveTab] = useState('executive')
  const [generatedReport, setGeneratedReport] = useState<any>(null)

  // Query para listar reportes
  const { data: reports, isLoading: reportsLoading, refetch: refetchReports } = useQuery({
    queryKey: ['reports'],
    queryFn: reportingAPI.listReports,
    enabled: false, // Manual refresh only
    staleTime: 0,
    cacheTime: 0,
  })

  // Mutations para generar reportes
  const {
    executiveMutation,
    technicalMutation,
    complianceMutation,
    exportMutation
  } = useReportingMutations({
    setGeneratedReport,
    refetchReports
  })

  const handleGenerateReport = (reportType: string) => {
    if (!target.trim()) {
      toast.error('Por favor ingrese un target válido')
      return
    }

    const params = {
      target,
      startDate: startDate || undefined,
      endDate: endDate || undefined
    }

    switch (reportType) {
      case 'executive':
        executiveMutation.mutate(params)
        break
      case 'technical':
        technicalMutation.mutate(params)
        break
      case 'compliance':
        complianceMutation.mutate({ ...params, standard: complianceStandard })
        break
    }
  }

  const handleExportReport = () => {
    if (!generatedReport) {
      toast.error('Primero genere un reporte')
      return
    }

    exportMutation.mutate({
      reportData: generatedReport,
      format: exportFormat
    })
  }

  const handleDownloadReport = async (filename: string) => {
    try {
      const blob = await reportingAPI.downloadReport(filename)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      toast.success('Reporte descargado exitosamente')
    } catch (error: any) {
      toast.error(`Error descargando reporte: ${error.message}`)
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Reporting</h1>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <FileText className="w-4 h-4" />
          Sistema de reportes profesionales de pentesting
        </div>
      </div>

      {/* Configuración del reporte */}
      <ReportConfig
        target={target}
        setTarget={setTarget}
        startDate={startDate}
        setStartDate={setStartDate}
        endDate={endDate}
        setEndDate={setEndDate}
        complianceStandard={complianceStandard}
        setComplianceStandard={setComplianceStandard}
      />

      {/* Tipos de reporte */}
      <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
        <div className="mb-4">
          <h2 className="text-xl font-bold text-green-400">Generar Reporte</h2>
          <p className="text-green-600">
            Seleccione el tipo de reporte a generar
          </p>
        </div>

        <ReportingTabs activeTab={activeTab} setActiveTab={setActiveTab} />

        <ReportGenerator
          activeTab={activeTab}
          complianceStandard={complianceStandard}
          handleGenerateReport={handleGenerateReport}
          executiveMutation={executiveMutation}
          technicalMutation={technicalMutation}
          complianceMutation={complianceMutation}
        />
      </div>

      {/* Reporte generado */}
      {generatedReport && (
        <GeneratedReport
          generatedReport={generatedReport}
          exportFormat={exportFormat}
          setExportFormat={setExportFormat}
          handleExportReport={handleExportReport}
          exportMutation={exportMutation}
        />
      )}

      {/* Historial de reportes */}
      <ReportsHistory
        reports={reports}
        reportsLoading={reportsLoading}
        refetchReports={refetchReports}
        handleDownloadReport={handleDownloadReport}
      />
    </div>
  )
}

export default Reporting
