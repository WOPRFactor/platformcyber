import React from 'react'
import { Lock } from 'lucide-react'

interface SecretFinding {
  type: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  file: string
  line?: number
  entropy?: number
  matched_text: string
}

interface SecretsFindingsListProps {
  secrets: SecretFinding[]
}

export const SecretsFindingsList: React.FC<SecretsFindingsListProps> = ({ secrets }) => {
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
      {secrets.map((secret, idx) => (
        <div key={idx} className={`border rounded-xl p-4 ${getSeverityStyles(secret.severity)}`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4" />
              <span className="font-semibold">{secret.type}</span>
            </div>
            <span className={`px-2 py-1 text-xs rounded ${getSeverityBadgeStyles(secret.severity)}`}>
              {secret.severity.toUpperCase()}
            </span>
          </div>
          <div className="text-xs text-gray-600 mb-2">
            <div>Archivo: <code className="bg-white px-1 rounded">{secret.file}</code></div>
            {secret.line && <div>Línea: {secret.line}</div>}
            {secret.entropy && <div>Entropía: {secret.entropy.toFixed(2)}</div>}
          </div>
          <div className="bg-black text-gray-900 p-2 rounded font-mono text-xs overflow-x-auto">
            {secret.matched_text}
          </div>
        </div>
      ))}
    </div>
  )
}


