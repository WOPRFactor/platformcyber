import React, { useState } from 'react'
import { Globe, Network, Server, Shield, Loader2 } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { reconnaissanceAPI } from '../../../../lib/api/reconnaissance'
import { commandPreviewAPI } from '../../../../lib/api/command-preview'
import { useConsole } from '../../../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useCommandPreview } from '../../../VulnerabilityAssessment/hooks/useCommandPreview'
import { useReconnaissanceScan } from '../../hooks/useReconnaissanceScan'

interface BasicReconSectionProps {
  target: string
  workspaceId: number
  commandPreview: ReturnType<typeof useCommandPreview>
}

export const BasicReconSection: React.FC<BasicReconSectionProps> = ({ target, workspaceId, commandPreview }) => {
  const { startReconScan } = useReconnaissanceScan()
  const { openPreview } = commandPreview
  const [dnsLookupTool, setDnsLookupTool] = useState<string>('host')
  const [dnsLookupType, setDnsLookupType] = useState<string>('')
  const [tracerouteProtocol, setTracerouteProtocol] = useState<string>('icmp')
  const [tracerouteHops, setTracerouteHops] = useState<number>(30)

  const whoisMutation = useMutation({
    mutationFn: () => startReconScan(
      'WHOIS',
      () => reconnaissanceAPI.whois(target, workspaceId),
      `whois ${target}`,
      target
    )
  })

  const dnsMutation = useMutation({
    mutationFn: () => startReconScan(
      'DNS Enumeration',
      () => reconnaissanceAPI.dnsEnum(target, workspaceId),
      `dnsrecon -d ${target}`,
      target
    )
  })

  const subdomainsMutation = useMutation({
    mutationFn: (tool: string = 'subfinder') => startReconScan(
      `Subdomain Enumeration (${tool})`,
      () => reconnaissanceAPI.subdomainEnum(target, workspaceId, tool),
      `${tool} -d ${target}`,
      target
    )
  })

  const crtshMutation = useMutation({
    mutationFn: () => startReconScan(
      'crt.sh',
      () => reconnaissanceAPI.crtsh(target, workspaceId),
      `crtsh ${target}`,
      target
    )
  })

  const findomainMutation = useMutation({
    mutationFn: (resolversFile?: string) => startReconScan(
      'Findomain',
      () => reconnaissanceAPI.findomain(target, workspaceId, resolversFile),
      `findomain -t ${target}`,
      target
    )
  })

  const dnsLookupMutation = useMutation({
    mutationFn: (tool: string = 'host', recordType?: string, dnsServer?: string) => startReconScan(
      `DNS Lookup (${tool})`,
      () => reconnaissanceAPI.dnsLookup(target, workspaceId, tool, recordType, dnsServer),
      `${tool} ${target}`,
      target
    )
  })

  const dnsEnumAltMutation = useMutation({
    mutationFn: (tool: string = 'dnsenum', wordlist?: string) => startReconScan(
      `DNS Enum Alt (${tool})`,
      () => reconnaissanceAPI.dnsEnumAlt(target, workspaceId, tool, wordlist),
      `${tool} ${target}`,
      target
    )
  })

  const tracerouteMutation = useMutation({
    mutationFn: (protocol: string = 'icmp', maxHops: number = 30) => startReconScan(
      'Traceroute',
      () => reconnaissanceAPI.traceroute(target, workspaceId, protocol, maxHops),
      `traceroute ${target}`,
      target
    )
  })

  const handleWhoisWithPreview = async () => {
    if (!target.trim() || !workspaceId) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewWhois({
        target: target,
        workspace_id: workspaceId
      })

      openPreview(preview, 'WHOIS Lookup', async () => {
        await startReconScan(
          'WHOIS',
          () => reconnaissanceAPI.whois(preview.parameters.target, workspaceId),
          preview.command_string,
          preview.parameters.target
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  const handleDnsReconWithPreview = async () => {
    if (!target.trim() || !workspaceId) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewDnsRecon({
        domain: target,
        workspace_id: workspaceId
      })

      openPreview(preview, 'DNS Enumeration', async () => {
        await startReconScan(
          'DNS Enumeration',
          () => reconnaissanceAPI.dnsEnum(preview.parameters.domain, workspaceId),
          preview.command_string,
          preview.parameters.domain
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  const handleSubdomainEnumWithPreview = async (tool: string = 'subfinder') => {
    if (!target.trim() || !workspaceId) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewSubdomainEnum({
        domain: target,
        workspace_id: workspaceId,
        tool: tool
      })

      openPreview(preview, `Subdomain Enumeration (${tool})`, async () => {
        await startReconScan(
          `Subdomain Enumeration (${tool})`,
          () => reconnaissanceAPI.subdomainEnum(preview.parameters.domain, workspaceId, preview.parameters.tool),
          preview.command_string,
          preview.parameters.domain
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  const handleCrtshWithPreview = async () => {
    if (!target.trim() || !workspaceId) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewCrtsh({
        domain: target,
        workspace_id: workspaceId
      })

      openPreview(preview, 'crt.sh', async () => {
        await startReconScan(
          'crt.sh',
          () => reconnaissanceAPI.crtsh(preview.parameters.domain, workspaceId),
          preview.command_string,
          preview.parameters.domain
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  const handleFindomainWithPreview = async () => {
    if (!target.trim() || !workspaceId) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewFindomain({
        domain: target,
        workspace_id: workspaceId
      })

      openPreview(preview, 'Findomain', async () => {
        await startReconScan(
          'Findomain',
          () => reconnaissanceAPI.findomain(preview.parameters.domain, workspaceId),
          preview.command_string,
          preview.parameters.domain
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  const handleDnsLookupWithPreview = async (tool: string, recordType?: string) => {
    if (!target.trim() || !workspaceId) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewDnsLookup({
        domain: target,
        workspace_id: workspaceId,
        tool: tool,
        record_type: recordType
      })

      openPreview(preview, `DNS Lookup (${tool})`, async () => {
        await startReconScan(
          `DNS Lookup (${tool})`,
          () => reconnaissanceAPI.dnsLookup(preview.parameters.domain, workspaceId, preview.parameters.tool, preview.parameters.record_type),
          preview.command_string,
          preview.parameters.domain
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  const handleDnsEnumAltWithPreview = async (tool: string) => {
    if (!target.trim() || !workspaceId) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewDnsEnumAlt({
        domain: target,
        workspace_id: workspaceId,
        tool: tool
      })

      openPreview(preview, `DNS Enum Alt (${tool})`, async () => {
        await startReconScan(
          `DNS Enum Alt (${tool})`,
          () => reconnaissanceAPI.dnsEnumAlt(preview.parameters.domain, workspaceId, preview.parameters.tool),
          preview.command_string,
          preview.parameters.domain
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  const handleTracerouteWithPreview = async (protocol: string, maxHops: number) => {
    if (!target.trim() || !workspaceId) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewTraceroute({
        target: target,
        workspace_id: workspaceId,
        protocol: protocol,
        max_hops: maxHops
      })

      openPreview(preview, 'Traceroute', async () => {
        await startReconScan(
          'Traceroute',
          () => reconnaissanceAPI.traceroute(preview.parameters.target, workspaceId, preview.parameters.protocol, preview.parameters.max_hops),
          preview.command_string,
          preview.parameters.target
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  return (
    <div className="mt-4">
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Globe className="w-5 h-5" />
            Reconocimiento Básico
          </h3>
          <p className="text-gray-500">
            Herramientas fundamentales de reconocimiento: WHOIS, DNS y enumeración de subdominios
          </p>
        </div>

        <div className="space-y-4">
          {/* WHOIS */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-cyan-400 mb-2">WHOIS</h4>
            <p className="text-sm text-gray-500 mb-3">
              Consulta información de registro del dominio o IP
            </p>
            <button
              onClick={handleWhoisWithPreview}
              disabled={whoisMutation.isPending || !target.trim()}
              className="w-full bg-cyan-600 hover:bg-cyan-700 disabled:bg-cyan-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
            >
              {whoisMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Globe className="w-4 h-4" />
              )}
              Iniciar Consulta WHOIS
            </button>
          </div>

          {/* DNS */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-blue-400 mb-2">DNS Enumeration</h4>
            <p className="text-sm text-gray-500 mb-3">
              Enumeración DNS completa usando DNSRecon (A, AAAA, MX, NS, TXT, SOA, CNAME)
            </p>
            <button
              onClick={handleDnsReconWithPreview}
              disabled={dnsMutation.isPending || !target.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
            >
              {dnsMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Network className="w-4 h-4" />
              )}
              Iniciar Enumeración DNS
            </button>
          </div>

          {/* Subdominios */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-purple-400 mb-2">Subdomain Enumeration</h4>
            <p className="text-sm text-gray-500 mb-3">
              Descubre subdominios usando Subfinder, Amass, Assetfinder o Sublist3r
            </p>
            <div className="grid grid-cols-2 gap-2 mb-3">
              {['subfinder', 'amass', 'assetfinder', 'sublist3r'].map((tool) => (
                <button
                  key={tool}
                  onClick={() => handleSubdomainEnumWithPreview(tool)}
                  disabled={subdomainsMutation.isPending || !target.trim()}
                  className="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:cursor-not-allowed text-white px-3 py-2 rounded text-sm flex items-center justify-center gap-2"
                >
                  {subdomainsMutation.isPending ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    <Server className="w-3 h-3" />
                  )}
                  {tool.charAt(0).toUpperCase() + tool.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* crt.sh */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-indigo-400 mb-2">Certificate Transparency (crt.sh)</h4>
            <p className="text-sm text-gray-500 mb-3">
              Busca subdominios usando Certificate Transparency logs
            </p>
            <button
              onClick={handleCrtshWithPreview}
              disabled={crtshMutation.isPending || !target.trim()}
              className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
            >
              {crtshMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Shield className="w-4 h-4" />
              )}
              Iniciar búsqueda crt.sh
            </button>
          </div>

          {/* Findomain */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-violet-400 mb-2">Findomain</h4>
            <p className="text-sm text-gray-500 mb-3">
              Enumeración rápida de subdominios con APIs
            </p>
            <button
              onClick={handleFindomainWithPreview}
              disabled={findomainMutation.isPending || !target.trim()}
              className="w-full bg-violet-600 hover:bg-violet-700 disabled:bg-violet-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
            >
              {findomainMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Server className="w-4 h-4" />
              )}
              Iniciar Findomain
            </button>
          </div>

          {/* DNS Lookup */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-cyan-400 mb-2">DNS Lookup (host/nslookup)</h4>
            <p className="text-sm text-gray-500 mb-3">
              Consultas DNS simples con host o nslookup
            </p>
            <div className="grid grid-cols-2 gap-2 mb-3">
              <select
                value={dnsLookupTool}
                onChange={(e) => setDnsLookupTool(e.target.value)}
                className="bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-600 text-sm"
              >
                <option value="host">host</option>
                <option value="nslookup">nslookup</option>
              </select>
              <select
                value={dnsLookupType}
                onChange={(e) => setDnsLookupType(e.target.value)}
                className="bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-600 text-sm"
              >
                <option value="">Todos</option>
                <option value="A">A</option>
                <option value="AAAA">AAAA</option>
                <option value="MX">MX</option>
                <option value="NS">NS</option>
                <option value="TXT">TXT</option>
                <option value="SOA">SOA</option>
                <option value="CNAME">CNAME</option>
              </select>
            </div>
            <button
              onClick={() => handleDnsLookupWithPreview(dnsLookupTool, dnsLookupType || undefined)}
              disabled={dnsLookupMutation.isPending || !target.trim()}
              className="w-full bg-cyan-600 hover:bg-cyan-700 disabled:bg-cyan-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
            >
              {dnsLookupMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Network className="w-4 h-4" />
              )}
              Iniciar DNS Lookup
            </button>
          </div>

          {/* DNS Enum Alt */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-emerald-400 mb-2">DNS Enumeration Alternativa</h4>
            <p className="text-sm text-gray-500 mb-3">
              Enumeración DNS con dnsenum o fierce
            </p>
            <div className="grid grid-cols-2 gap-2">
              {['dnsenum', 'fierce'].map((tool) => (
                <button
                  key={tool}
                  onClick={() => handleDnsEnumAltWithPreview(tool)}
                  disabled={dnsEnumAltMutation.isPending || !target.trim()}
                  className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-800 disabled:cursor-not-allowed text-white px-3 py-2 rounded text-sm flex items-center justify-center gap-2"
                >
                  {dnsEnumAltMutation.isPending ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    <Network className="w-3 h-3" />
                  )}
                  {tool.charAt(0).toUpperCase() + tool.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Traceroute */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-amber-400 mb-2">Traceroute</h4>
            <p className="text-sm text-gray-500 mb-3">
              Mapeo de ruta de red
            </p>
            <div className="grid grid-cols-2 gap-2 mb-3">
              <select
                value={tracerouteProtocol}
                onChange={(e) => setTracerouteProtocol(e.target.value)}
                className="bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-600 text-sm"
              >
                <option value="icmp">ICMP</option>
                <option value="tcp">TCP</option>
                <option value="udp">UDP</option>
              </select>
              <input
                type="number"
                value={tracerouteHops}
                onChange={(e) => setTracerouteHops(Number(e.target.value))}
                placeholder="Max hops (30)"
                className="bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-600 text-sm"
              />
            </div>
            <button
              onClick={() => handleTracerouteWithPreview(tracerouteProtocol, tracerouteHops)}
              disabled={tracerouteMutation.isPending || !target.trim()}
              className="w-full bg-amber-600 hover:bg-amber-700 disabled:bg-amber-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
            >
              {tracerouteMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Network className="w-4 h-4" />
              )}
              Iniciar Traceroute
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

