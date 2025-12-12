import React, { useState } from 'react'
import { Terminal, CheckCircle, XCircle, Loader, Play, Zap, Search } from 'lucide-react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import { integrationsAPI } from '../../../../lib/api/integrations'

export const MetasploitSection: React.FC = () => {
  const [metasploitModule, setMetasploitModule] = useState('')
  const [exploitOptions, setExploitOptions] = useState<any>({
    RHOSTS: '',
    RPORT: '445',
    LHOST: '',
    LPORT: '4444',
    PAYLOAD: 'windows/meterpreter/reverse_tcp'
  })

  const hasToken = !!localStorage.getItem('access_token')
  const isAuthenticated = true // TODO: Get from context

  const { data: metasploitStatus, refetch: refetchMetasploitStatus } = useQuery({
    queryKey: ['metasploit_status'],
    queryFn: integrationsAPI.checkMetasploitStatus,
    enabled: isAuthenticated && hasToken,
    refetchInterval: (isAuthenticated && hasToken) ? 30000 : false,
  })

  const checkMetasploitMutation = useMutation({
    mutationFn: integrationsAPI.checkMetasploitStatus,
    onSuccess: (data) => {
      if (data.connected) {
        toast.success('Conexión con Metasploit exitosa')
      } else {
        toast.error(`Error de conexión: ${data.error}`)
      }
      refetchMetasploitStatus()
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`)
    }
  })

  const listModulesMutation = useMutation({
    mutationFn: (moduleType: string) => integrationsAPI.listMetasploitModules(moduleType),
    onSuccess: () => {
      toast.success('Módulos listados correctamente')
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`)
    }
  })

  const runExploitMutation = useMutation({
    mutationFn: () => integrationsAPI.runMetasploitExploit(metasploitModule, exploitOptions),
    onSuccess: () => {
      toast.success('Exploit ejecutado correctamente')
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.message}`)
    }
  })

  return (
    <div className="space-y-6">
      {/* Status Card */}
      <div className="bg-gray-50 border border-red-500 rounded-xl p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Terminal className="w-6 h-6 text-red-600" />
            <h3 className="text-lg font-bold text-red-400">Metasploit Framework</h3>
          </div>
          <div className="flex items-center gap-2">
            {metasploitStatus?.connected ? (
              <CheckCircle className="w-5 h-5 text-gray-500" />
            ) : (
              <XCircle className="w-5 h-5 text-red-600" />
            )}
            <span className={metasploitStatus?.connected ? 'text-gray-500' : 'text-red-600'}>
              {metasploitStatus?.connected ? 'Conectado' : 'Desconectado'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <div className="text-sm text-gray-600">Estado RPC</div>
            <div className={`text-lg font-bold ${metasploitStatus?.connected ? 'text-gray-500' : 'text-red-600'}`}>
              {metasploitStatus?.connected ? 'Activo' : 'Inactivo'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600">Versión</div>
            <div className="text-lg font-bold text-blue-600">
              {metasploitStatus?.version || 'Desconocida'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600">Host:Port</div>
            <div className="text-lg font-bold text-purple-600">
              127.0.0.1:55553
            </div>
          </div>
        </div>

        <button
          onClick={() => checkMetasploitMutation.mutate()}
          disabled={checkMetasploitMutation.isPending}
          className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {checkMetasploitMutation.isPending ? (
            <Loader className="w-4 h-4 animate-spin mr-2" />
          ) : (
            <Zap className="w-4 h-4 mr-2" />
          )}
          Verificar Conexión
        </button>

        {metasploitStatus?.error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
            <p className="text-red-800 text-sm">{metasploitStatus.error}</p>
          </div>
        )}
      </div>

      {/* Exploit Form */}
      <div className="bg-gray-50 border border-red-500 rounded-xl p-6">
        <h3 className="text-lg font-bold text-red-400 mb-4 flex items-center gap-2">
          <Play className="w-5 h-5" />
          Ejecutar Exploit
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">Módulo de Exploit</label>
            <input
              type="text"
              value={metasploitModule}
              onChange={(e) => setMetasploitModule(e.target.value)}
              placeholder="exploit/windows/smb/ms17_010_eternalblue"
              className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">RHOSTS (Objetivo)</label>
            <input
              type="text"
              value={exploitOptions.RHOSTS}
              onChange={(e) => setExploitOptions({...exploitOptions, RHOSTS: e.target.value})}
              placeholder="192.168.1.100"
              className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">RPORT</label>
            <input
              type="text"
              value={exploitOptions.RPORT}
              onChange={(e) => setExploitOptions({...exploitOptions, RPORT: e.target.value})}
              className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">LHOST</label>
            <input
              type="text"
              value={exploitOptions.LHOST}
              onChange={(e) => setExploitOptions({...exploitOptions, LHOST: e.target.value})}
              placeholder="tu-ip"
              className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">LPORT</label>
            <input
              type="text"
              value={exploitOptions.LPORT}
              onChange={(e) => setExploitOptions({...exploitOptions, LPORT: e.target.value})}
              className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">PAYLOAD</label>
            <input
              type="text"
              value={exploitOptions.PAYLOAD}
              onChange={(e) => setExploitOptions({...exploitOptions, PAYLOAD: e.target.value})}
              className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500"
            />
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => listModulesMutation.mutate('exploits')}
            disabled={listModulesMutation.isPending}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center gap-2 disabled:opacity-50"
          >
            {listModulesMutation.isPending ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            Listar Exploits
          </button>

          <button
            onClick={() => runExploitMutation.mutate()}
            disabled={runExploitMutation.isPending || !metasploitModule.trim() || !exploitOptions.RHOSTS.trim()}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded flex items-center gap-2 disabled:opacity-50"
          >
            {runExploitMutation.isPending ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            Ejecutar Exploit
          </button>
        </div>

        {runExploitMutation.data && (
          <div className="mt-4">
            <h4 className="font-semibold mb-2 text-gray-900">Resultado del Exploit</h4>
            <div className="bg-black text-gray-900 p-4 rounded font-mono text-sm max-h-40 overflow-y-auto">
              {runExploitMutation.data?.console_output || 'Sin salida de consola'}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

