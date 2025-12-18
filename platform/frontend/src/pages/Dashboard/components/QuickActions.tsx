import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, Activity, Shield, CheckCircle, LineChart, Search } from 'lucide-react'

export const QuickActions: React.FC = () => {
  const navigate = useNavigate()

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Zap className="w-5 h-5 mr-2" />
        Acciones Rápidas
      </h2>
      <div className="grid grid-cols-1 gap-3">
        <button 
          onClick={() => navigate('/reconnaissance')}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg flex items-center justify-start space-x-3 py-4 px-4 transition-colors cursor-pointer"
        >
          <Search size={20} />
          <div className="text-left">
            <div className="font-medium">Reconocimiento</div>
            <div className="text-xs text-gray-500">Recopilar información inicial</div>
          </div>
        </button>

        <button 
          onClick={() => navigate('/scanning')}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg flex items-center justify-start space-x-3 py-4 px-4 transition-colors cursor-pointer"
        >
          <Activity size={20} />
          <div className="text-left">
            <div className="font-medium">Nuevo Escaneo</div>
            <div className="text-xs text-gray-500">Iniciar escaneo de red</div>
          </div>
        </button>

        <button 
          onClick={() => navigate('/ia')}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg flex items-center justify-start space-x-3 py-4 px-4 transition-colors cursor-pointer"
        >
          <Shield size={20} />
          <div className="text-left">
            <div className="font-medium">Análisis IA</div>
            <div className="text-xs text-gray-500">Evaluación inteligente</div>
          </div>
        </button>

        <button 
          onClick={() => navigate('/owasp')}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg flex items-center justify-start space-x-3 py-4 px-4 transition-colors cursor-pointer"
        >
          <CheckCircle size={20} />
          <div className="text-left">
            <div className="font-medium">Auditoría OWASP</div>
            <div className="text-xs text-gray-500">Top 10 vulnerabilities</div>
          </div>
        </button>

        <button 
          onClick={() => navigate('/reporting')}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg flex items-center justify-start space-x-3 py-4 px-4 transition-colors cursor-pointer"
        >
          <LineChart size={20} />
          <div className="text-left">
            <div className="font-medium">Generar Reporte</div>
            <div className="text-xs text-gray-500">Informe ejecutivo</div>
          </div>
        </button>
      </div>
    </div>
  )
}


