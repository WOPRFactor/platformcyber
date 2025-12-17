import React from 'react'
import { Bug } from 'lucide-react'

interface SQLMapFinding {
  severity?: string
  type?: string
  description?: string
  technique?: string
}

interface SQLMapFindingsProps {
  findings: SQLMapFinding[]
}

export const SQLMapFindings: React.FC<SQLMapFindingsProps> = ({ findings }) => {
  return (
    <div className="space-y-2">
      {findings?.map((finding, idx) => (
        <div key={idx} className={`border rounded-xl p-4 ${
          finding?.severity === 'critical' ? 'border-red-500 bg-red-50' :
          finding?.severity === 'high' ? 'border-orange-500 bg-orange-50' :
          finding?.severity === 'medium' ? 'border-yellow-500 bg-yellow-50' :
          'border-blue-500 bg-blue-50'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Bug className="w-4 h-4" />
              <span className="font-semibold capitalize">{finding?.type?.replace('_', ' ') || 'Unknown'}</span>
            </div>
            <span className={`px-2 py-1 text-xs rounded ${
              finding?.severity === 'critical' ? 'bg-red-100 text-red-800' :
              finding?.severity === 'high' ? 'bg-orange-100 text-orange-800' :
              finding?.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
              'bg-blue-100 text-blue-800'
            }`}>
              {finding?.severity?.toUpperCase() || 'INFO'}
            </span>
          </div>
          <p className="text-sm">{finding?.description || 'No description available'}</p>
          {finding?.technique && (
            <p className="text-sm text-gray-600">
              <strong>Técnica:</strong> {finding.technique}
            </p>
          )}
        </div>
      ))}
    </div>
  )
}


