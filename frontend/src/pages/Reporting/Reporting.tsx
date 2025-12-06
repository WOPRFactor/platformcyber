"""
Reporting Page
==============

Página principal de reporting refactorizada.
"""

import React, { useState } from 'react'
import { FileText } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { reportingAPI } from '../../lib/api/reporting'
import { toast } from 'sonner'
import { useReportingMutations } from './hooks/useReportingMutations'
import {
  ReportConfig,
  ReportingTabs,
  ReportGenerator,
  GeneratedReport,
  ReportsHistory
} from './components'

const Reporting: React.FC = () => {
  const [target, setTarget] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [complianceStandard, setComplianceStandard] = useState('general')
  const [exportFormat, setExportFormat] = useState<'json' | 'html' | 'pdf'>('html')
  const [activeTab, setActiveTab] = useState('executive')
  const [generatedReport, setGeneratedReport] = useState<any>(null)

  const {
    executiveMutation,
    technicalMutation,
    complianceMutation,
    exportMutation
  } = useReportingMutations()

  const { data: reports, isLoading: reportsLoading, refetch: refetchReports } = useQuery({
    queryKey: ['reports'],
    queryFn: reportingAPI.listReports,
    enabled: false,
    staleTime: 0,
    cacheTime: 0,
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
        executiveMutation.mutate(params, {
          onSuccess: (data) => {
            if (data.success) {
              setGeneratedReport(data)
            }
          }
        })
        break
      case 'technical':
        technicalMutation.mutate(params, {
          onSuccess: (data) => {
            if (data.success) {
              setGeneratedReport(data)
            }
          }
        })
        break
      case 'compliance':
        complianceMutation.mutate({ ...params, standard: complianceStandard }, {
          onSuccess: (data) => {
            if (data.success) {
              setGeneratedReport(data)
            }
          }
        })
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

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Reporting</h1>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <FileText className="w-4 h-4" />
          Sistema de reportes profesionales de pentesting
        </div>
      </div>

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

      <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
        <div className="w-full">
          <ReportingTabs activeTab={activeTab} setActiveTab={setActiveTab} />
          <ReportGenerator
            activeTab={activeTab}
            target={target}
            complianceStandard={complianceStandard}
            executiveMutation={executiveMutation}
            technicalMutation={technicalMutation}
            complianceMutation={complianceMutation}
            onGenerateReport={handleGenerateReport}
          />
        </div>
      </div>

      {generatedReport && (
        <GeneratedReport
          generatedReport={generatedReport}
          exportFormat={exportFormat}
          setExportFormat={setExportFormat}
          exportMutation={exportMutation}
          onExportReport={handleExportReport}
        />
      )}

      <ReportsHistory
        reports={reports}
        reportsLoading={reportsLoading}
        onRefresh={() => refetchReports()}
      />
    </div>
  )
}

export default Reporting


