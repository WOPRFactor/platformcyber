import React from 'react'

interface AnalysisConfigProps {
  targetPath: string
  language: string
  packageManager: string
  scanners: string[]
  configTypes: string[]
  onTargetPathChange: (path: string) => void
  onLanguageChange: (lang: string) => void
  onPackageManagerChange: (pm: string) => void
  onScannersChange: (scanners: string[]) => void
  onConfigTypesChange: (types: string[]) => void
}

export const AnalysisConfig: React.FC<AnalysisConfigProps> = ({
  targetPath,
  language,
  packageManager,
  scanners,
  configTypes,
  onTargetPathChange,
  onLanguageChange,
  onPackageManagerChange,
  onScannersChange,
  onConfigTypesChange
}) => {
  return (
    <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-green-400">Configuración del Análisis</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-green-400 mb-2">Ruta del Código Fuente</label>
          <input
            type="text"
            value={targetPath}
            onChange={(e) => onTargetPathChange(e.target.value)}
            placeholder="/path/to/source/code"
            className="w-full bg-gray-900 border border-green-500 rounded px-3 py-2 text-green-400 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-green-400 mb-2">Lenguaje de Programación</label>
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value)}
            className="w-full bg-gray-900 border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="auto">Auto-detectar</option>
            <option value="python">Python</option>
            <option value="javascript">JavaScript/TypeScript</option>
            <option value="java">Java</option>
            <option value="php">PHP</option>
            <option value="go">Go</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-green-400 mb-2">Gestor de Paquetes</label>
          <select
            value={packageManager}
            onChange={(e) => onPackageManagerChange(e.target.value)}
            className="w-full bg-gray-900 border border-green-500 rounded px-3 py-2 text-green-400 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="auto">Auto-detectar</option>
            <option value="pip">Python (pip)</option>
            <option value="npm">Node.js (npm)</option>
            <option value="maven">Java (Maven)</option>
            <option value="composer">PHP (Composer)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-green-400 mb-2">Tipos de Configuración</label>
          <div className="space-y-2">
            {[
              { id: 'web_servers', label: 'Servidores Web' },
              { id: 'databases', label: 'Bases de Datos' },
              { id: 'permissions', label: 'Permisos' },
              { id: 'encryption', label: 'Encriptación' }
            ].map(type => (
              <label key={type.id} className="flex items-center">
                <input
                  type="checkbox"
                  checked={configTypes.includes(type.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      onConfigTypesChange([...configTypes, type.id])
                    } else {
                      onConfigTypesChange(configTypes.filter(t => t !== type.id))
                    }
                  }}
                  className="mr-2"
                />
                {type.label}
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-4">
        <label className="block text-sm font-medium text-green-400 mb-2">Escáneres de Secrets</label>
        <div className="space-y-2">
          {[
            { id: 'patterns', label: 'Patrones comunes' },
            { id: 'entropy', label: 'Análisis de entropía' },
            { id: 'known_keys', label: 'Claves conocidas' }
          ].map(scanner => (
            <label key={scanner.id} className="flex items-center">
              <input
                type="checkbox"
                checked={scanners.includes(scanner.id)}
                onChange={(e) => {
                  if (e.target.checked) {
                    onScannersChange([...scanners, scanner.id])
                  } else {
                    onScannersChange(scanners.filter(s => s !== scanner.id))
                  }
                }}
                className="mr-2"
              />
              {scanner.label}
            </label>
          ))}
        </div>
      </div>
    </div>
  )
}


