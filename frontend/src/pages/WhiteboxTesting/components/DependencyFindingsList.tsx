import React from 'react'
import { Package } from 'lucide-react'

interface VulnerableDependency {
  package: string
  version: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  vulnerability: string
}

interface DependencyFindingsListProps {
  dependencies: VulnerableDependency[]
}

export const DependencyFindingsList: React.FC<DependencyFindingsListProps> = ({ dependencies }) => {
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
      {dependencies.map((dep, idx) => (
        <div key={idx} className={`border rounded-lg p-4 ${getSeverityStyles(dep.severity)}`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Package className="w-4 h-4" />
              <span className="font-semibold">{dep.package}</span>
              <span className="text-sm bg-gray-200 px-2 py-1 rounded">{dep.version}</span>
            </div>
            <span className={`px-2 py-1 text-xs rounded ${getSeverityBadgeStyles(dep.severity)}`}>
              {dep.severity.toUpperCase()}
            </span>
          </div>
          <p className="text-sm">{dep.vulnerability}</p>
        </div>
      ))}
    </div>
  )
}


