import React from 'react'
import { Settings } from 'lucide-react'

interface ConfigIssue {
  type: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  message: string
  file: string
  permissions?: string
}

interface ConfigIssuesListProps {
  issues: ConfigIssue[]
}

export const ConfigIssuesList: React.FC<ConfigIssuesListProps> = ({ issues }) => {
  const getSeverityStyles = (severity: string) => {
    switch (severity) {
      case 'critical': return 'border-red-500 bg-red-50'
      case 'high': return 'border-orange-500 bg-orange-50'
      case 'medium': return 'border-yellow-500 bg-yellow-50'
      default: return 'border-blue-500 bg-blue-50'
    }
  }

  const getSeverityBadgeStyles = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-blue-100 text-blue-800'
    }
  }

  return (
    <div className="space-y-2">
      {issues.map((issue, idx) => (
        <div key={idx} className={`border rounded-lg p-4 ${getSeverityStyles(issue.severity)}`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              <span className="font-semibold capitalize">{issue.type.replace('_', ' ')}</span>
            </div>
            <span className={`px-2 py-1 text-xs rounded ${getSeverityBadgeStyles(issue.severity)}`}>
              {issue.severity.toUpperCase()}
            </span>
          </div>
          <p className="text-sm mb-2">{issue.message}</p>
          <div className="text-xs text-gray-600">
            Archivo: <code className="bg-white px-1 rounded">{issue.file}</code>
            {issue.permissions && <div>Permisos: {issue.permissions}</div>}
          </div>
        </div>
      ))}
    </div>
  )
}


