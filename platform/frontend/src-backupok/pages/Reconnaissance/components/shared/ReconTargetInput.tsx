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
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Target</h2>
        <p className="text-gray-500">
          Ingrese el dominio, IP o URL objetivo para reconocimiento
        </p>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-900 mb-2">
          Target Global
          {target && <span className="text-gray-900 ml-2 text-xs">🌍 (compartido)</span>}
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="ej: example.com, 192.168.1.1"
            className="flex-1 bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500"
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
          <p className="text-gray-500 text-sm mt-1">
            Target compartido: <span className="text-gray-700 font-mono">{target}</span>
          </p>
        )}
      </div>
    </div>
  )
}


