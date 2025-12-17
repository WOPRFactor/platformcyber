/**
 * EnumerationSection Component
 * =============================
 * 
 * Componente para la sección de enumeración de servicios en Scanning.
 * Agrupa todas las herramientas de enumeración:
 * - SMB/CIFS (enum4linux, smbmap, smbclient)
 * - Network Services (SSH, FTP, SMTP, DNS, SNMP, LDAP, RDP)
 * - Databases (MySQL, PostgreSQL, Redis, MongoDB)
 * - SSL/TLS (sslscan, sslyze)
 */

import React, { useState, useRef } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Loader2, Server, Network, Database, Lock } from 'lucide-react'
import { scanningAPI } from '../../lib/api/scanning'
import { commandPreviewAPI } from '../../lib/api/command-preview'
import { useWorkspace } from '../../contexts/WorkspaceContext'
import { useTarget } from '../../contexts/TargetContext'
import { useConsole } from '../../contexts/ConsoleContext'
import CommandPreviewModal from '../CommandPreviewModal'

const EnumerationSection: React.FC = () => {
  const { currentWorkspace } = useWorkspace()
  const { target } = useTarget()
  const { startTask, addLog, updateTask, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  const [activeCategory, setActiveCategory] = useState<'smb' | 'network' | 'database' | 'ssl'>('smb')
  
  // Estado para preview
  const [showPreview, setShowPreview] = useState(false)
  const [previewData, setPreviewData] = useState<any>(null)
  const [previewToolName, setPreviewToolName] = useState('')
  const previewExecuteFnRef = useRef<(() => Promise<void>) | null>(null)

  // Helper para crear mutaciones
  const createEnumMutation = (
    toolName: string,
    apiCall: (target: string, workspaceId: number, options?: any) => Promise<any>
  ) => {
    return useMutation({
      mutationFn: (options?: any) => {
        if (!target?.trim() || !currentWorkspace?.id) {
          throw new Error('Target y workspace son requeridos')
        }
        const taskId = startTask(toolName, 'scanning', undefined, target)
        addLog('info', 'scanning', `Iniciando ${toolName} para ${target}`, taskId)
        updateTaskProgress(taskId, 10, `Iniciando ${toolName}...`)
        
        return apiCall(target, currentWorkspace.id, options).then(result => {
          if (result.scan_id) {
            updateTask(taskId, { session_id: String(result.scan_id) })
          }
          return result
        })
      },
      onSuccess: () => {
        toast.success(`${toolName} iniciado`)
        queryClient.invalidateQueries({ queryKey: ['scan-sessions'] })
      },
      onError: (error: any) => {
        toast.error(`Error en ${toolName}: ${error.message}`)
      }
    })
  }

  // Mutaciones SMB
  const enum4linuxMutation = createEnumMutation('enum4linux', scanningAPI.enum4linux)
  const smbmapMutation = createEnumMutation('smbmap', scanningAPI.smbmap)
  const smbclientMutation = createEnumMutation('smbclient', scanningAPI.smbclient)

  // Mutaciones Network Services
  const sshEnumMutation = createEnumMutation('SSH Enum', scanningAPI.sshEnum)
  const ftpEnumMutation = createEnumMutation('FTP Enum', scanningAPI.ftpEnum)
  const smtpEnumMutation = createEnumMutation('SMTP Enum', scanningAPI.smtpEnum)
  const dnsEnumMutation = createEnumMutation('DNS Enum', scanningAPI.dnsEnum)
  const snmpEnumMutation = createEnumMutation('SNMP Enum', scanningAPI.snmpEnum)
  const ldapEnumMutation = createEnumMutation('LDAP Enum', scanningAPI.ldapEnum)
  const rdpEnumMutation = createEnumMutation('RDP Enum', scanningAPI.rdpEnum)

  // Mutaciones Databases
  const mysqlEnumMutation = createEnumMutation('MySQL Enum', scanningAPI.mysqlEnum)
  const postgresqlEnumMutation = createEnumMutation('PostgreSQL Enum', scanningAPI.postgresqlEnum)
  const redisEnumMutation = createEnumMutation('Redis Enum', scanningAPI.redisEnum)
  const mongodbEnumMutation = createEnumMutation('MongoDB Enum', scanningAPI.mongodbEnum)

  // Mutaciones SSL/TLS
  const sslscanMutation = createEnumMutation('sslscan', scanningAPI.sslscan)
  const sslyzeMutation = createEnumMutation('sslyze', scanningAPI.sslyze)

  // Handlers con preview para FTP, DNS y RDP
  const handleFtpEnumWithPreview = async (port: number) => {
    if (!target?.trim() || !currentWorkspace?.id) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      console.log('🔍 [FTP Enum] Obteniendo preview...', { target: target.trim(), workspace_id: currentWorkspace.id, port })
      const preview = await commandPreviewAPI.previewFtpEnum({
        target: target.trim(),
        workspace_id: currentWorkspace.id,
        port
      })
      console.log('✅ [FTP Enum] Preview obtenido:', preview)

      setPreviewData(preview)
      setPreviewToolName('FTP Enum')
      previewExecuteFnRef.current = async () => {
        console.log('🚀 [FTP Enum] Ejecutando comando desde preview')
        await ftpEnumMutation.mutateAsync({ port })
      };
      setShowPreview(true)
      console.log('👁️ [FTP Enum] Modal de preview abierto')
    } catch (error: any) {
      console.error('❌ [FTP Enum] Error obteniendo preview:', error)
      const errorMessage = error?.response?.data?.error || error?.message || 'Error al obtener preview del comando'
      toast.error(`Error al obtener preview: ${errorMessage}`)
    }
  }

  const handleDnsEnumWithPreview = async (port: number) => {
    if (!target?.trim() || !currentWorkspace?.id) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      console.log('🔍 [DNS Enum] Obteniendo preview...', { target: target.trim(), workspace_id: currentWorkspace.id, port })
      const preview = await commandPreviewAPI.previewDnsEnum({
        target: target.trim(),
        workspace_id: currentWorkspace.id,
        port,
        tool: 'nmap'
      })
      console.log('✅ [DNS Enum] Preview obtenido:', preview)

      setPreviewData(preview)
      setPreviewToolName('DNS Enum')
      previewExecuteFnRef.current = async () => {
        console.log('🚀 [DNS Enum] Ejecutando comando desde preview')
        await dnsEnumMutation.mutateAsync({ port })
      };
      setShowPreview(true)
      console.log('👁️ [DNS Enum] Modal de preview abierto')
    } catch (error: any) {
      console.error('❌ [DNS Enum] Error obteniendo preview:', error)
      const errorMessage = error?.response?.data?.error || error?.message || 'Error al obtener preview del comando'
      toast.error(`Error al obtener preview: ${errorMessage}`)
    }
  }

  const handleRdpEnumWithPreview = async (port: number) => {
    if (!target?.trim() || !currentWorkspace?.id) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      console.log('🔍 [RDP Enum] Obteniendo preview...', { target: target.trim(), workspace_id: currentWorkspace.id, port })
      const preview = await commandPreviewAPI.previewRdpEnum({
        target: target.trim(),
        workspace_id: currentWorkspace.id,
        port
      })
      console.log('✅ [RDP Enum] Preview obtenido:', preview)

      setPreviewData(preview)
      setPreviewToolName('RDP Enum')
      previewExecuteFnRef.current = async () => {
        console.log('🚀 [RDP Enum] Ejecutando comando desde preview')
        await rdpEnumMutation.mutateAsync({ port })
      };
      setShowPreview(true)
      console.log('👁️ [RDP Enum] Modal de preview abierto')
    } catch (error: any) {
      console.error('❌ [RDP Enum] Error obteniendo preview:', error)
      const errorMessage = error?.response?.data?.error || error?.message || 'Error al obtener preview del comando'
      toast.error(`Error al obtener preview: ${errorMessage}`)
    }
  }

  // Handlers genéricos con preview para Network Services
  const handleSshEnumWithPreview = async (port: number, tool: string = 'nmap') => {
    if (!target?.trim() || !currentWorkspace?.id) return toast.error('Target y workspace son requeridos')
    try {
      const preview = await commandPreviewAPI.previewSshEnum({ target: target.trim(), workspace_id: currentWorkspace.id, port, tool })
      setPreviewData(preview)
      setPreviewToolName('SSH Enum')
      previewExecuteFnRef.current = async () => await sshEnumMutation.mutateAsync({ port, tool })
      setShowPreview(true)
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error?.response?.data?.error || error?.message || 'Error desconocido'}`)
    }
  }

  const handleSmtpEnumWithPreview = async (port: number, tool: string = 'nmap') => {
    if (!target?.trim() || !currentWorkspace?.id) return toast.error('Target y workspace son requeridos')
    try {
      const preview = await commandPreviewAPI.previewSmtpEnum({ target: target.trim(), workspace_id: currentWorkspace.id, port, tool })
      setPreviewData(preview)
      setPreviewToolName('SMTP Enum')
      previewExecuteFnRef.current = async () => await smtpEnumMutation.mutateAsync({ port, tool })
      setShowPreview(true)
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error?.response?.data?.error || error?.message || 'Error desconocido'}`)
    }
  }

  const handleSnmpEnumWithPreview = async (port: number, community: string = 'public') => {
    if (!target?.trim() || !currentWorkspace?.id) return toast.error('Target y workspace son requeridos')
    try {
      const preview = await commandPreviewAPI.previewSnmpEnum({ target: target.trim(), workspace_id: currentWorkspace.id, port, community, tool: 'nmap' })
      setPreviewData(preview)
      setPreviewToolName('SNMP Enum')
      previewExecuteFnRef.current = async () => await snmpEnumMutation.mutateAsync({ port, community })
      setShowPreview(true)
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error?.response?.data?.error || error?.message || 'Error desconocido'}`)
    }
  }

  const handleLdapEnumWithPreview = async (port: number, tool: string = 'nmap') => {
    if (!target?.trim() || !currentWorkspace?.id) return toast.error('Target y workspace son requeridos')
    try {
      const preview = await commandPreviewAPI.previewLdapEnum({ target: target.trim(), workspace_id: currentWorkspace.id, port, tool })
      setPreviewData(preview)
      setPreviewToolName('LDAP Enum')
      previewExecuteFnRef.current = async () => await ldapEnumMutation.mutateAsync({ port, tool })
      setShowPreview(true)
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error?.response?.data?.error || error?.message || 'Error desconocido'}`)
    }
  }

  // Handlers genéricos con preview para Databases
  const handleMysqlEnumWithPreview = async (port: number, tool: string = 'nmap', username?: string) => {
    if (!target?.trim() || !currentWorkspace?.id) return toast.error('Target y workspace son requeridos')
    try {
      const preview = await commandPreviewAPI.previewMysqlEnum({ target: target.trim(), workspace_id: currentWorkspace.id, port, tool, username })
      setPreviewData(preview)
      setPreviewToolName('MySQL Enum')
      previewExecuteFnRef.current = async () => await mysqlEnumMutation.mutateAsync({ port, tool, username })
      setShowPreview(true)
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error?.response?.data?.error || error?.message || 'Error desconocido'}`)
    }
  }

  const handlePostgresqlEnumWithPreview = async (port: number, tool: string = 'nmap', username: string = 'postgres') => {
    if (!target?.trim() || !currentWorkspace?.id) return toast.error('Target y workspace son requeridos')
    try {
      const preview = await commandPreviewAPI.previewPostgresqlEnum({ target: target.trim(), workspace_id: currentWorkspace.id, port, tool, username })
      setPreviewData(preview)
      setPreviewToolName('PostgreSQL Enum')
      previewExecuteFnRef.current = async () => await postgresqlEnumMutation.mutateAsync({ port, tool, username })
      setShowPreview(true)
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error?.response?.data?.error || error?.message || 'Error desconocido'}`)
    }
  }

  const handleRedisEnumWithPreview = async (port: number, tool: string = 'nmap') => {
    if (!target?.trim() || !currentWorkspace?.id) return toast.error('Target y workspace son requeridos')
    try {
      const preview = await commandPreviewAPI.previewRedisEnum({ target: target.trim(), workspace_id: currentWorkspace.id, port, tool })
      setPreviewData(preview)
      setPreviewToolName('Redis Enum')
      previewExecuteFnRef.current = async () => await redisEnumMutation.mutateAsync({ port, tool })
      setShowPreview(true)
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error?.response?.data?.error || error?.message || 'Error desconocido'}`)
    }
  }

  const handleMongodbEnumWithPreview = async (port: number) => {
    if (!target?.trim() || !currentWorkspace?.id) return toast.error('Target y workspace son requeridos')
    try {
      const preview = await commandPreviewAPI.previewMongodbEnum({ target: target.trim(), workspace_id: currentWorkspace.id, port })
      setPreviewData(preview)
      setPreviewToolName('MongoDB Enum')
      previewExecuteFnRef.current = async () => await mongodbEnumMutation.mutateAsync({ port })
      setShowPreview(true)
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error?.response?.data?.error || error?.message || 'Error desconocido'}`)
    }
  }

  // Handlers genéricos con preview para SSL/TLS
  const handleSslscanWithPreview = async (port: number, show_certificate: boolean = false) => {
    if (!target?.trim() || !currentWorkspace?.id) return toast.error('Target y workspace son requeridos')
    try {
      const preview = await commandPreviewAPI.previewSslscan({ target: target.trim(), workspace_id: currentWorkspace.id, port, show_certificate })
      setPreviewData(preview)
      setPreviewToolName('sslscan')
      previewExecuteFnRef.current = async () => await sslscanMutation.mutateAsync({ port, show_certificate })
      setShowPreview(true)
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error?.response?.data?.error || error?.message || 'Error desconocido'}`)
    }
  }

  const handleSslyzeWithPreview = async (port: number, regular: boolean = true) => {
    if (!target?.trim() || !currentWorkspace?.id) return toast.error('Target y workspace son requeridos')
    try {
      const preview = await commandPreviewAPI.previewSslyze({ target: target.trim(), workspace_id: currentWorkspace.id, port, regular })
      setPreviewData(preview)
      setPreviewToolName('sslyze')
      previewExecuteFnRef.current = async () => await sslyzeMutation.mutateAsync({ port, regular })
      setShowPreview(true)
    } catch (error: any) {
      toast.error(`Error al obtener preview: ${error?.response?.data?.error || error?.message || 'Error desconocido'}`)
    }
  }

  return (
    <div className="mt-4">
      {/* Categorías */}
      <div className="flex border-b border-gray-200 mb-4">
        <button
          onClick={() => setActiveCategory('smb')}
          className={`px-4 py-2 border-b-2 ${
            activeCategory === 'smb'
              ? 'border-gray-200 text-gray-900'
              : 'border-transparent text-gray-500 hover:text-gray-900'
          }`}
        >
          <Server className="w-4 h-4 inline mr-2" />
          SMB/CIFS
        </button>
        <button
          onClick={() => setActiveCategory('network')}
          className={`px-4 py-2 border-b-2 ${
            activeCategory === 'network'
              ? 'border-gray-200 text-gray-900'
              : 'border-transparent text-gray-500 hover:text-gray-900'
          }`}
        >
          <Network className="w-4 h-4 inline mr-2" />
          Servicios de Red
        </button>
        <button
          onClick={() => setActiveCategory('database')}
          className={`px-4 py-2 border-b-2 ${
            activeCategory === 'database'
              ? 'border-gray-200 text-gray-900'
              : 'border-transparent text-gray-500 hover:text-gray-900'
          }`}
        >
          <Database className="w-4 h-4 inline mr-2" />
          Bases de Datos
        </button>
        <button
          onClick={() => setActiveCategory('ssl')}
          className={`px-4 py-2 border-b-2 ${
            activeCategory === 'ssl'
              ? 'border-gray-200 text-gray-900'
              : 'border-transparent text-gray-500 hover:text-gray-900'
          }`}
        >
          <Lock className="w-4 h-4 inline mr-2" />
          SSL/TLS
        </button>
      </div>

      {/* SMB/CIFS */}
      {activeCategory === 'smb' && (
        <div className="space-y-4">
          {/* enum4linux */}
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
            <h3 className="text-lg font-bold mb-3">enum4linux</h3>
            <div className="space-y-3">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="enum4linux-use-ng"
                  defaultChecked={true}
                  className="w-4 h-4"
                />
                <span>Usar enum4linux-ng (moderno)</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="enum4linux-all"
                  defaultChecked={false}
                  className="w-4 h-4"
                />
                <span>Ejecutar todas las opciones (-A)</span>
              </label>
              <button
                onClick={async () => {
                  if (!target?.trim() || !currentWorkspace?.id) {
                    toast.error('Target y workspace son requeridos')
                    return
                  }
                  try {
                    const useNg = (document.getElementById('enum4linux-use-ng') as HTMLInputElement)?.checked ?? true
                    const all = (document.getElementById('enum4linux-all') as HTMLInputElement)?.checked ?? false
                    
                    console.log('🔍 [enum4linux] Obteniendo preview...', { use_ng: useNg, all })
                    const preview = await commandPreviewAPI.previewEnum4linux({
                      target: target.trim(),
                      workspace_id: currentWorkspace.id,
                      use_ng: useNg,
                      all: all
                    })
                    console.log('✅ [enum4linux] Preview obtenido:', preview)
                    setPreviewData(preview)
                    setPreviewToolName('enum4linux')
                    previewExecuteFnRef.current = async () => {
                      console.log('🚀 [enum4linux] Ejecutando comando desde preview')
                      await enum4linuxMutation.mutateAsync({
                        use_ng: useNg,
                        all: all
                      })
                    };
                    setShowPreview(true)
                    console.log('👁️ [enum4linux] Modal de preview abierto')
                  } catch (error: any) {
                    console.error('❌ [enum4linux] Error obteniendo preview:', error)
                    const errorMessage = error?.response?.data?.error || error?.message || 'Error al obtener preview del comando'
                    toast.error(`Error al obtener preview: ${errorMessage}`)
                  }
                }}
                disabled={enum4linuxMutation.isPending || !target?.trim()}
                className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                {enum4linuxMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Iniciar enum4linux'}
              </button>
            </div>
          </div>

          {/* smbmap */}
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
            <h3 className="text-lg font-bold mb-3">smbmap</h3>
            <div className="space-y-3">
              <input
                type="text"
                placeholder="Username (opcional)"
                id="smbmap-username"
                className="w-full bg-white border border-gray-200 rounded px-3 py-2"
              />
              <input
                type="password"
                placeholder="Password (opcional)"
                id="smbmap-password"
                className="w-full bg-white border border-gray-200 rounded px-3 py-2"
              />
              <input
                type="text"
                placeholder="Share (opcional)"
                id="smbmap-share"
                className="w-full bg-white border border-gray-200 rounded px-3 py-2"
              />
              <button
                onClick={async () => {
                  if (!target?.trim() || !currentWorkspace?.id) {
                    toast.error('Target y workspace son requeridos')
                    return
                  }
                  try {
                    console.log('🔍 [smbmap] Obteniendo preview...')
                    const preview = await commandPreviewAPI.previewSmbmap({
                      target: target.trim(),
                      workspace_id: currentWorkspace.id,
                      username: (document.getElementById('smbmap-username') as HTMLInputElement)?.value || undefined,
                      password: (document.getElementById('smbmap-password') as HTMLInputElement)?.value || undefined,
                      share: (document.getElementById('smbmap-share') as HTMLInputElement)?.value || undefined
                    })
                    console.log('✅ [smbmap] Preview obtenido:', preview)
                    setPreviewData(preview)
                    setPreviewToolName('smbmap')
                    previewExecuteFnRef.current = async () => {
                      console.log('🚀 [smbmap] Ejecutando comando desde preview')
                      await smbmapMutation.mutateAsync({
                        username: (document.getElementById('smbmap-username') as HTMLInputElement)?.value,
                        password: (document.getElementById('smbmap-password') as HTMLInputElement)?.value,
                        share: (document.getElementById('smbmap-share') as HTMLInputElement)?.value
                      })
                    };
                    setShowPreview(true)
                    console.log('👁️ [smbmap] Modal de preview abierto')
                  } catch (error: any) {
                    console.error('❌ [smbmap] Error obteniendo preview:', error)
                    const errorMessage = error?.response?.data?.error || error?.message || 'Error al obtener preview del comando'
                    toast.error(`Error al obtener preview: ${errorMessage}`)
                  }
                }}
                disabled={smbmapMutation.isPending || !target?.trim()}
                className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                {smbmapMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Iniciar smbmap'}
              </button>
            </div>
          </div>

          {/* smbclient */}
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
            <h3 className="text-lg font-bold mb-3">smbclient</h3>
            <div className="space-y-3">
              <input
                type="text"
                placeholder="Share (default: IPC$)"
                id="smbclient-share"
                className="w-full bg-white border border-gray-200 rounded px-3 py-2"
              />
              <input
                type="text"
                placeholder="Username (opcional)"
                id="smbclient-username"
                className="w-full bg-white border border-gray-200 rounded px-3 py-2"
              />
              <input
                type="password"
                placeholder="Password (opcional)"
                id="smbclient-password"
                className="w-full bg-white border border-gray-200 rounded px-3 py-2"
              />
              <button
                onClick={async () => {
                  if (!target?.trim() || !currentWorkspace?.id) {
                    toast.error('Target y workspace son requeridos')
                    return
                  }
                  try {
                    console.log('🔍 [smbclient] Obteniendo preview...')
                    const share = (document.getElementById('smbclient-share') as HTMLInputElement)?.value || 'IPC$'
                    const preview = await commandPreviewAPI.previewSmbclient({
                      target: target.trim(),
                      workspace_id: currentWorkspace.id,
                      share: share,
                      username: (document.getElementById('smbclient-username') as HTMLInputElement)?.value || undefined,
                      password: (document.getElementById('smbclient-password') as HTMLInputElement)?.value || undefined
                    })
                    console.log('✅ [smbclient] Preview obtenido:', preview)
                    setPreviewData(preview)
                    setPreviewToolName('smbclient')
                    previewExecuteFnRef.current = async () => {
                      console.log('🚀 [smbclient] Ejecutando comando desde preview')
                      await smbclientMutation.mutateAsync({
                        share: share,
                        username: (document.getElementById('smbclient-username') as HTMLInputElement)?.value,
                        password: (document.getElementById('smbclient-password') as HTMLInputElement)?.value
                      })
                    };
                    setShowPreview(true)
                    console.log('👁️ [smbclient] Modal de preview abierto')
                  } catch (error: any) {
                    console.error('❌ [smbclient] Error obteniendo preview:', error)
                    const errorMessage = error?.response?.data?.error || error?.message || 'Error al obtener preview del comando'
                    toast.error(`Error al obtener preview: ${errorMessage}`)
                  }
                }}
                disabled={smbclientMutation.isPending || !target?.trim()}
                className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                {smbclientMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Iniciar smbclient'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Network Services */}
      {activeCategory === 'network' && (
        <div className="space-y-4">
          {[
            { name: 'SSH', mutation: sshEnumMutation, defaultPort: 22, hasPreview: true, handler: handleSshEnumWithPreview },
            { name: 'FTP', mutation: ftpEnumMutation, defaultPort: 21, hasPreview: true, handler: handleFtpEnumWithPreview },
            { name: 'SMTP', mutation: smtpEnumMutation, defaultPort: 25, hasPreview: true, handler: handleSmtpEnumWithPreview },
            { name: 'DNS', mutation: dnsEnumMutation, defaultPort: 53, hasPreview: true, handler: handleDnsEnumWithPreview },
            { name: 'SNMP', mutation: snmpEnumMutation, defaultPort: 161, extraField: 'community', hasPreview: true, handler: handleSnmpEnumWithPreview },
            { name: 'LDAP', mutation: ldapEnumMutation, defaultPort: 389, hasPreview: true, handler: handleLdapEnumWithPreview },
            { name: 'RDP', mutation: rdpEnumMutation, defaultPort: 3389, hasPreview: true, handler: handleRdpEnumWithPreview }
          ].map(({ name, mutation, defaultPort, extraField, hasPreview, handler }) => (
            <div key={name} className="bg-gray-50 border border-gray-200 rounded-xl p-4">
              <h3 className="text-lg font-bold mb-3">{name} Enumeration</h3>
              <div className="space-y-3">
                <input
                  type="number"
                  placeholder={`Puerto (default: ${defaultPort})`}
                  id={`${name.toLowerCase()}-port`}
                  defaultValue={defaultPort}
                  className="w-full bg-white border border-gray-200 rounded px-3 py-2"
                />
                {extraField === 'community' && (
                  <input
                    type="text"
                    placeholder="Community (default: public)"
                    id={`${name.toLowerCase()}-community`}
                    defaultValue="public"
                    className="w-full bg-white border border-gray-200 rounded px-3 py-2"
                  />
                )}
                <div className="flex space-x-2">
                  {hasPreview && handler && (
                    <button
                      onClick={() => {
                        const port = parseInt((document.getElementById(`${name.toLowerCase()}-port`) as HTMLInputElement)?.value || String(defaultPort))
                        if (extraField === 'community') {
                          const community = (document.getElementById(`${name.toLowerCase()}-community`) as HTMLInputElement)?.value || 'public'
                          handler(port, community)
                        } else {
                          handler(port)
                        }
                      }}
                      disabled={mutation.isPending || !target?.trim()}
                      className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors"
                    >
                      Preview
                    </button>
                  )}
                  <button
                    onClick={() => {
                      const port = parseInt((document.getElementById(`${name.toLowerCase()}-port`) as HTMLInputElement)?.value || String(defaultPort))
                      const options: any = { port }
                      if (extraField === 'community') {
                        options.community = (document.getElementById(`${name.toLowerCase()}-community`) as HTMLInputElement)?.value || 'public'
                      }
                      mutation.mutate(options)
                    }}
                    disabled={mutation.isPending || !target?.trim()}
                    className={`${hasPreview && handler ? 'flex-1' : 'w-full'} bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white px-4 py-2 rounded`}
                  >
                    {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : `Iniciar ${name} Enum`}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Databases */}
      {activeCategory === 'database' && (
        <div className="space-y-4">
          {[
            { name: 'MySQL', mutation: mysqlEnumMutation, defaultPort: 3306, hasUsername: true, handler: handleMysqlEnumWithPreview },
            { name: 'PostgreSQL', mutation: postgresqlEnumMutation, defaultPort: 5432, hasUsername: true, defaultUsername: 'postgres', handler: handlePostgresqlEnumWithPreview },
            { name: 'Redis', mutation: redisEnumMutation, defaultPort: 6379, handler: handleRedisEnumWithPreview },
            { name: 'MongoDB', mutation: mongodbEnumMutation, defaultPort: 27017, handler: handleMongodbEnumWithPreview }
          ].map(({ name, mutation, defaultPort, hasUsername, defaultUsername, handler }) => (
            <div key={name} className="bg-gray-50 border border-gray-200 rounded-xl p-4">
              <h3 className="text-lg font-bold mb-3">{name} Enumeration</h3>
              <div className="space-y-3">
                <input
                  type="number"
                  placeholder={`Puerto (default: ${defaultPort})`}
                  id={`${name.toLowerCase()}-port`}
                  defaultValue={defaultPort}
                  className="w-full bg-white border border-gray-200 rounded px-3 py-2"
                />
                {hasUsername && (
                  <input
                    type="text"
                    placeholder={`Username${defaultUsername ? ` (default: ${defaultUsername})` : ''}`}
                    id={`${name.toLowerCase()}-username`}
                    defaultValue={defaultUsername || ''}
                    className="w-full bg-white border border-gray-200 rounded px-3 py-2"
                  />
                )}
                <button
                  onClick={() => {
                    const port = parseInt((document.getElementById(`${name.toLowerCase()}-port`) as HTMLInputElement)?.value || String(defaultPort))
                    const options: any = { port }
                    if (hasUsername) {
                      const username = (document.getElementById(`${name.toLowerCase()}-username`) as HTMLInputElement)?.value
                      if (username) options.username = username
                    }
                    if (handler) {
                      if (hasUsername) {
                        const username = (document.getElementById(`${name.toLowerCase()}-username`) as HTMLInputElement)?.value || defaultUsername
                        handler(port, 'nmap', username)
                      } else {
                        handler(port)
                      }
                    } else {
                      mutation.mutate(options)
                    }
                  }}
                  disabled={mutation.isPending || !target?.trim()}
                  className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : `Iniciar ${name} Enum`}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* SSL/TLS */}
      {activeCategory === 'ssl' && (
        <div className="space-y-4">
          {/* sslscan */}
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
            <h3 className="text-lg font-bold mb-3">sslscan</h3>
            <div className="space-y-3">
              <input
                type="number"
                placeholder="Puerto (default: 443)"
                id="sslscan-port"
                defaultValue={443}
                className="w-full bg-white border border-gray-200 rounded px-3 py-2"
              />
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="sslscan-certificate"
                  className="rounded"
                />
                <span>Mostrar certificado completo</span>
              </label>
              <button
                onClick={() => handleSslscanWithPreview(
                  parseInt((document.getElementById('sslscan-port') as HTMLInputElement)?.value || '443'),
                  (document.getElementById('sslscan-certificate') as HTMLInputElement)?.checked
                )}
                disabled={sslscanMutation.isPending || !target?.trim()}
                className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                {sslscanMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Iniciar sslscan'}
              </button>
            </div>
          </div>

          {/* sslyze */}
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
            <h3 className="text-lg font-bold mb-3">sslyze</h3>
            <div className="space-y-3">
              <input
                type="number"
                placeholder="Puerto (default: 443)"
                id="sslyze-port"
                defaultValue={443}
                className="w-full bg-white border border-gray-200 rounded px-3 py-2"
              />
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="sslyze-regular"
                  defaultChecked
                  className="rounded"
                />
                <span>Modo regular (--regular)</span>
              </label>
              <button
                onClick={() => handleSslyzeWithPreview(
                  parseInt((document.getElementById('sslyze-port') as HTMLInputElement)?.value || '443'),
                  (document.getElementById('sslyze-regular') as HTMLInputElement)?.checked
                )}
                disabled={sslyzeMutation.isPending || !target?.trim()}
                className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                {sslyzeMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Iniciar sslyze'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Command Preview Modal */}
      <CommandPreviewModal
        isOpen={showPreview}
        onClose={() => setShowPreview(false)}
        onExecute={async () => {
          if (previewExecuteFnRef.current) {
            setShowPreview(false)
            await previewExecuteFnRef.current()
          }
        }}
        previewData={previewData}
        toolName={previewToolName}
        category="scanning"
      />
    </div>
  )
}

export default EnumerationSection

