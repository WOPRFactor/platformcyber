/**
 * Payloads Tab Component
 * ======================
 * 
 * Componente para la pestaña de generación inteligente de payloads.
 */

import React from 'react'
import { Code, Loader } from 'lucide-react'
import { UseMutationResult } from '@tanstack/react-query'

interface PayloadData {
  target_os: string
  vulnerability_type: string
  delivery_method: string
  evasion_techniques: string[]
}

interface PayloadsTabProps {
  payloadData: PayloadData
  setPayloadData: (data: PayloadData) => void
  onGenerate: () => void
  payloadMutation: UseMutationResult<any, any, any>
}

const PayloadsTab: React.FC<PayloadsTabProps> = ({
  payloadData,
  setPayloadData,
  onGenerate,
  payloadMutation
}) => {
  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center space-x-2">
        <Code size={20} />
        <span>Generación Inteligente de Payloads</span>
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">Sistema Operativo Objetivo</label>
            <select
              value={payloadData.target_os}
              onChange={(e) => setPayloadData({...payloadData, target_os: e.target.value})}
              className="input w-full"
            >
              <option value="linux">Linux</option>
              <option value="windows">Windows</option>
              <option value="macos">macOS</option>
              <option value="android">Android</option>
              <option value="ios">iOS</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">Tipo de Vulnerabilidad</label>
            <input
              type="text"
              value={payloadData.vulnerability_type}
              onChange={(e) => setPayloadData({...payloadData, vulnerability_type: e.target.value})}
              className="input w-full"
              placeholder="Ej: SQL Injection, RCE, XSS..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">Método de Entrega</label>
            <select
              value={payloadData.delivery_method}
              onChange={(e) => setPayloadData({...payloadData, delivery_method: e.target.value})}
              className="input w-full"
            >
              <option value="remote">Remoto</option>
              <option value="local">Local</option>
              <option value="web">Web</option>
              <option value="email">Email</option>
              <option value="usb">USB</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">Técnicas de Evasión</label>
            <div className="space-y-2">
              {['encoding', 'obfuscation', 'encryption', 'polymorphism'].map(technique => (
                <label key={technique} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={payloadData.evasion_techniques.includes(technique)}
                    onChange={(e) => {
                      const updated = e.target.checked
                        ? [...payloadData.evasion_techniques, technique]
                        : payloadData.evasion_techniques.filter(t => t !== technique)
                      setPayloadData({...payloadData, evasion_techniques: updated})
                    }}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-500 capitalize">{technique}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Generación de Payload</h3>
          <div className="bg-gray-50/50 p-4 rounded border border-gray-200/20">
            <p className="text-sm text-gray-500 mb-4">
              La IA generará payloads optimizados basándose en la configuración especificada.
              Se incluirán técnicas de evasión y explicaciones detalladas.
            </p>
            <button
              onClick={onGenerate}
              disabled={payloadMutation.isPending || !payloadData.vulnerability_type}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              {payloadMutation.isPending ? (
                <Loader size={16} className="animate-spin" />
              ) : (
                <Code size={16} />
              )}
              <span>Generar Payload Inteligente</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PayloadsTab


