import React from 'react'
import { FolderOpen } from 'lucide-react'

interface DirectoryResult {
  url?: string
  status_code?: string
  size?: string
}

interface DirectoriesListProps {
  directories: DirectoryResult[]
}

export const DirectoriesList: React.FC<DirectoriesListProps> = ({ directories }) => {
  return (
    <div className="space-y-1 max-h-60 overflow-y-auto">
      {directories?.map((dir, idx) => (
        <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded">
          <div className="flex items-center gap-2">
            <FolderOpen className="w-4 h-4 text-blue-600" />
            <code className="text-sm">{dir?.url || 'Unknown'}</code>
          </div>
          <div className="flex items-center gap-2">
            <span className={`px-2 py-1 text-xs rounded ${
              dir?.status_code?.startsWith('2') ? 'bg-green-100 text-green-800' :
              dir?.status_code?.startsWith('3') ? 'bg-blue-100 text-blue-800' :
              dir?.status_code?.startsWith('4') ? 'bg-orange-100 text-orange-800' :
              'bg-red-100 text-red-800'
            }`}>
              {dir?.status_code || 'Unknown'}
            </span>
            {dir?.size && <span className="text-xs text-gray-500">{dir.size}</span>}
          </div>
        </div>
      ))}
    </div>
  )
}


