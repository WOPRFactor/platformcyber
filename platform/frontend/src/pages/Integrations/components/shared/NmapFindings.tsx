import React from 'react'
import { Server } from 'lucide-react'

interface NmapFinding {
  severity?: string
  type?: string
  port?: number
  protocol?: string
  service?: string
  state?: string
  os_details?: string
  description?: string
  details?: string
}

interface NmapFindingsProps {
  findings: NmapFinding[]
}

export const NmapFindings: React.FC<NmapFindingsProps> = ({ findings }) => {
  return (
    <div className="space-y-2">
      {findings?.map((finding, idx) => (
        <div key={idx} className={`border rounded-lg p-4 ${
          finding?.severity === 'critical' ? 'border-red-500 bg-red-50' :
          finding?.severity === 'high' ? 'border-orange-500 bg-orange-50' :
          finding?.severity === 'medium' ? 'border-yellow-500 bg-yellow-50' :
          'border-blue-500 bg-blue-50'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Server className="w-4 h-4" />
              <span className="font-semibold capitalize">{finding?.type?.replace('_', ' ') || 'Unknown'}</span>
              {finding?.port && finding?.protocol && (
                <span className="bg-gray-200 px-2 py-1 rounded text-sm">
                  {finding.port}/{finding.protocol}
                </span>
              )}
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

          {finding?.service && (
            <p className="text-sm mb-1">
              <strong>Servicio:</strong> {finding.service}
              {finding?.state && <span className="ml-2">({finding.state})</span>}
            </p>
          )}

          {finding?.os_details && (
            <p className="text-sm mb-1">
              <strong>OS:</strong> {finding.os_details}
            </p>
          )}

          {finding?.description && (
            <p className="text-sm text-gray-600">{finding.description}</p>
          )}

          {finding?.details && (
            <p className="text-sm text-gray-600">{finding.details}</p>
          )}
        </div>
      ))}
    </div>
  )
}


