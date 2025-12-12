import React from 'react'
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

interface CodeFinding {
  type: string
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  message: string
  file: string
  line?: number
  code?: string
}

interface CodeFindingsListProps {
  findings: CodeFinding[]
}

export const CodeFindingsList: React.FC<CodeFindingsListProps> = ({ findings }) => {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <XCircle className="w-4 h-4 text-red-600" />
      case 'high': return <AlertTriangle className="w-4 h-4 text-orange-600" />
      case 'medium': return <AlertTriangle className="w-4 h-4 text-yellow-600" />
      case 'low': return <AlertTriangle className="w-4 h-4 text-blue-600" />
      case 'info': return <CheckCircle className="w-4 h-4 text-blue-600" />
      default: return <AlertTriangle className="w-4 h-4 text-gray-600" />
    }
  }

  const getSeverityStyles = (severity: string) => {
    switch (severity) {
      case 'critical': return 'border-red-500 bg-red-50'
      case 'high': return 'border-orange-500 bg-orange-50'
      case 'medium': return 'border-yellow-500 bg-yellow-50'
      case 'low': return 'border-blue-500 bg-blue-50'
      default: return 'border-blue-500 bg-blue-50'
    }
  }

  const getSeverityBadgeStyles = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-2">
      {findings.map((finding, idx) => (
        <div key={idx} className={`border rounded-xl p-4 ${getSeverityStyles(finding.severity)}`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              {getSeverityIcon(finding.severity)}
              <span className="font-semibold capitalize">{finding.type.replace('_', ' ')}</span>
            </div>
            <span className={`px-2 py-1 text-xs rounded ${getSeverityBadgeStyles(finding.severity)}`}>
              {finding.severity.toUpperCase()}
            </span>
          </div>
          <p className="text-sm mb-2">{finding.message}</p>
          <div className="text-xs text-gray-600">
            <div>Archivo: <code className="bg-white px-1 rounded">{finding.file}</code></div>
            {finding.line && <div>Línea: {finding.line}</div>}
            {finding.code && (
              <div className="mt-1">
                <div className="bg-black text-gray-900 p-2 rounded font-mono text-xs overflow-x-auto">
                  {finding.code}
                </div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}


