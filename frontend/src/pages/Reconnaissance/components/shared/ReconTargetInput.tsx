import React from 'react'

interface ReconTargetInputProps {
  target: string
  setTarget: (target: string) => void
  clearTarget?: () => void
}

export const ReconTargetInput: React.FC<ReconTargetInputProps> = ({
  target,
  setTarget,
  clearTarget
}) => {
  return (
    <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-green-400">Target</h2>
        <p className="text-green-600">
          Ingrese el dominio, IP o URL objetivo para reconocimiento
        </p>
      </div>
      <div>
        <label className="block text-sm font-medium text-green-400 mb-2">
          Target Global
          {target && <span className="text-green-400 ml-2 text-xs">🌍 (compartido)</span>}
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="ej: example.com, 192.168.1.1"
            className="flex-1 bg-gray-900 border border-green-500 rounded px-3 py-2 text-green-400 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          {target && clearTarget && (
            <button
              onClick={clearTarget}
              className="btn-secondary px-3"
              title="Limpiar target"
            >
              🗑️
            </button>
          )}
        </div>
        {target && (
          <p className="text-green-600 text-sm mt-1">
            Target compartido: <span className="text-green-300 font-mono">{target}</span>
          </p>
        )}
      </div>
    </div>
  )
}


