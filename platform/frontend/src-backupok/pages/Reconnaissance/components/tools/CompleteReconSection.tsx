import React, { useState } from 'react'
import { Activity, Loader2 } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { reconnaissanceAPI } from '../../../../lib/api/reconnaissance'
import { useReconnaissanceScan } from '../../hooks/useReconnaissanceScan'

interface CompleteReconSectionProps {
  target: string
  workspaceId: number
}

export const CompleteReconSection: React.FC<CompleteReconSectionProps> = ({ target, workspaceId }) => {
  const { startReconScan } = useReconnaissanceScan()
  const [includeAdvanced, setIncludeAdvanced] = useState(false)

  const completeMutation = useMutation({
    mutationFn: (includeAdvanced: boolean = false) => startReconScan(
      'Reconocimiento Completo',
      () => reconnaissanceAPI.complete(target, workspaceId, includeAdvanced),
      `reconocimiento completo ${target}`,
      target
    )
  })

  return (
    <div className="mt-4">
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Reconocimiento Completo
          </h3>
          <p className="text-gray-500">
            Ejecuta todas las fases básicas de reconocimiento automáticamente
          </p>
        </div>

        <div className="bg-white rounded-xl p-4 mb-4">
          <h4 className="text-md font-semibold text-gray-900 mb-2">Fases Incluidas</h4>
          <ul className="text-sm text-gray-500 space-y-1 list-disc list-inside">
            <li>WHOIS - Consulta de información de registro</li>
            <li>DNS - Enumeración DNS completa</li>
            <li>Subdominios - Enumeración con Subfinder</li>
            <li>Emails - Búsqueda de emails con theHarvester</li>
          </ul>
        </div>

        <div className="flex items-center mb-4">
          <input
            type="checkbox"
            id="include-advanced"
            checked={includeAdvanced}
            onChange={(e) => setIncludeAdvanced(e.target.checked)}
            className="w-4 h-4 text-gray-800 bg-gray-700 border-gray-200 rounded focus:ring-red-500"
          />
          <label htmlFor="include-advanced" className="ml-2 text-sm text-gray-600">
            Incluir herramientas avanzadas (Wayback URLs)
          </label>
        </div>

        <button
          onClick={() => completeMutation.mutate(includeAdvanced)}
          disabled={completeMutation.isPending || !target.trim()}
          className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2 text-lg font-semibold"
        >
          {completeMutation.isPending ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Ejecutando Reconocimiento Completo...
            </>
          ) : (
            <>
              <Activity className="w-5 h-5" />
              Iniciar Reconocimiento Completo
            </>
          )}
        </button>
      </div>
    </div>
  )
}


