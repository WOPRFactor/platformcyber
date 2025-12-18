import React, { useState } from 'react'
import { Shield, Mail, History, Search, Network, Loader2 } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { reconnaissanceAPI } from '../../../../lib/api/reconnaissance'
import { commandPreviewAPI } from '../../../../lib/api/command-preview'
import { toast } from 'sonner'
import { useCommandPreview } from '../../../VulnerabilityAssessment/hooks/useCommandPreview'
import { useReconnaissanceScan } from '../../hooks/useReconnaissanceScan'

interface OSINTSectionProps {
  target: string
  workspaceId: number
  commandPreview: ReturnType<typeof useCommandPreview>
}

export const OSINTSection: React.FC<OSINTSectionProps> = ({ target, workspaceId, commandPreview }) => {
  const { startReconScan } = useReconnaissanceScan()
  const { openPreview } = commandPreview
  
  const [shodanQuery, setShodanQuery] = useState('')
  const [censysQuery, setCensysQuery] = useState('')
  const [censysIndex, setCensysIndex] = useState('hosts')
  const [googleDorksTool, setGoogleDorksTool] = useState('manual')
  const [googleDorksQuery, setGoogleDorksQuery] = useState('')
  const [hunterApiKey, setHunterApiKey] = useState('')
  const [linkedinTool, setLinkedinTool] = useState('crosslinked')
  const [linkedinCompany, setLinkedinCompany] = useState('')

  const emailsMutation = useMutation({
    mutationFn: () => startReconScan(
      'Email Harvesting',
      () => reconnaissanceAPI.emails(target, workspaceId),
      `theHarvester -d ${target}`,
      target
    )
  })

  const waybackMutation = useMutation({
    mutationFn: () => startReconScan(
      'Wayback URLs',
      () => reconnaissanceAPI.wayback(target, workspaceId),
      `waybackurls ${target}`,
      target
    )
  })

  const shodanMutation = useMutation({
    mutationFn: (query: string) => startReconScan(
      'Shodan Search',
      () => reconnaissanceAPI.shodan(query, workspaceId),
      `shodan search ${query}`,
      query
    )
  })

  const censysMutation = useMutation({
    mutationFn: (query: string, indexType: string = 'hosts') => startReconScan(
      'Censys Search',
      () => reconnaissanceAPI.censys(query, workspaceId, indexType),
      `censys search ${query}`,
      query
    )
  })

  const googleDorksMutation = useMutation({
    mutationFn: (tool: string = 'manual', dorkQuery?: string) => startReconScan(
      `Google Dorks (${tool})`,
      () => reconnaissanceAPI.googleDorks(target, workspaceId, dorkQuery, tool),
      `google-dorks ${tool} ${target}`,
      target
    )
  })

  const hunterIoMutation = useMutation({
    mutationFn: (apiKey?: string) => startReconScan(
      'Hunter.io',
      () => reconnaissanceAPI.hunterIo(target, workspaceId, apiKey),
      `hunter.io ${target}`,
      target
    )
  })

  const linkedinEnumMutation = useMutation({
    mutationFn: (tool: string = 'crosslinked', companyName?: string) => startReconScan(
      `LinkedIn Enum (${tool})`,
      () => reconnaissanceAPI.linkedinEnum(target, workspaceId, companyName, tool),
      `${tool} ${target}`,
      target
    )
  })

  const handleEmailHarvestWithPreview = async () => {
    if (!target.trim() || !workspaceId) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewTheHarvester({
        domain: target,
        workspace_id: workspaceId
      })

      openPreview(preview, 'Email Harvesting', async () => {
        await startReconScan(
          'Email Harvesting',
          () => reconnaissanceAPI.emails(preview.parameters.domain, workspaceId),
          preview.command_string,
          preview.parameters.domain
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  const handleWaybackWithPreview = async () => {
    if (!target.trim() || !workspaceId) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewWayback({
        domain: target,
        workspace_id: workspaceId
      })

      openPreview(preview, 'Wayback URLs', async () => {
        await startReconScan(
          'Wayback URLs',
          () => reconnaissanceAPI.wayback(preview.parameters.domain, workspaceId),
          preview.command_string,
          preview.parameters.domain
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  const handleShodanWithPreview = async (query: string) => {
    if (!query.trim() || !workspaceId) {
      toast.error('Query y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewShodan({
        query: query,
        workspace_id: workspaceId
      })

      openPreview(preview, 'Shodan Search', async () => {
        await startReconScan(
          'Shodan Search',
          () => reconnaissanceAPI.shodan(preview.parameters.query, workspaceId),
          preview.command_string,
          preview.parameters.query
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  const handleCensysWithPreview = async (query: string, indexType: string = 'hosts') => {
    if (!query.trim() || !workspaceId) {
      toast.error('Query y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewCensys({
        query: query,
        workspace_id: workspaceId,
        index_type: indexType
      })

      openPreview(preview, 'Censys Search', async () => {
        await startReconScan(
          'Censys Search',
          () => reconnaissanceAPI.censys(preview.parameters.query, workspaceId, preview.parameters.index_type),
          preview.command_string,
          preview.parameters.query
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  const handleGoogleDorksWithPreview = async (dorkQuery?: string, tool: string = 'manual') => {
    if (!target.trim() || !workspaceId) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewGoogleDorks({
        domain: target,
        workspace_id: workspaceId,
        dork_query: dorkQuery,
        tool: tool
      })

      openPreview(preview, `Google Dorks (${tool})`, async () => {
        await startReconScan(
          'Google Dorks',
          () => reconnaissanceAPI.googleDorks(preview.parameters.domain, workspaceId, preview.parameters.dork_query, preview.parameters.tool),
          preview.command_string,
          preview.parameters.domain
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  const handleHunterIoWithPreview = async (apiKey?: string) => {
    if (!target.trim() || !workspaceId) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewHunterIo({
        domain: target,
        workspace_id: workspaceId,
        api_key: apiKey
      })

      openPreview(preview, 'Hunter.io', async () => {
        await startReconScan(
          'Hunter.io',
          () => reconnaissanceAPI.hunterIo(preview.parameters.domain, workspaceId, apiKey),
          preview.command_string,
          preview.parameters.domain
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  const handleLinkedInEnumWithPreview = async (tool: string, companyName?: string) => {
    if (!target.trim() || !workspaceId) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewLinkedInEnum({
        domain: target,
        workspace_id: workspaceId,
        tool,
        company_name: companyName
      })

      openPreview(preview, `LinkedIn Enumeration (${tool})`, async () => {
        await startReconScan(
          'LinkedIn Enumeration',
          () => reconnaissanceAPI.linkedinEnum(preview.parameters.domain, workspaceId, preview.parameters.company_name, preview.parameters.tool),
          preview.command_string,
          preview.parameters.domain
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
            <Shield className="w-5 h-5" />
            OSINT (Open Source Intelligence)
          </h3>
          <p className="text-gray-500">
            Herramientas de inteligencia de fuentes abiertas: emails, Shodan y URLs históricas
          </p>
        </div>

        <div className="space-y-4">
          {/* Email Harvesting */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-yellow-400 mb-2">Email Harvesting</h4>
            <p className="text-sm text-gray-500 mb-3">
              Busca emails asociados al dominio usando theHarvester (Google, Bing, LinkedIn, Twitter, etc.)
            </p>
            <button
              onClick={handleEmailHarvestWithPreview}
              disabled={emailsMutation.isPending || !target.trim()}
              className="w-full bg-yellow-600 hover:bg-yellow-700 disabled:bg-yellow-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
            >
              {emailsMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Mail className="w-4 h-4" />
              )}
              Iniciar Búsqueda de Emails
            </button>
          </div>

          {/* Wayback URLs */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-orange-400 mb-2">Wayback URLs</h4>
            <p className="text-sm text-gray-500 mb-3">
              Obtiene URLs históricas del dominio desde Wayback Machine
            </p>
            <button
              onClick={handleWaybackWithPreview}
              disabled={waybackMutation.isPending || !target.trim()}
              className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-orange-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
            >
              {waybackMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <History className="w-4 h-4" />
              )}
              Iniciar Búsqueda Wayback
            </button>
          </div>

          {/* Shodan */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-red-400 mb-2">Shodan Search</h4>
            <p className="text-sm text-gray-500 mb-3">
              Busca información en Shodan (requiere API key configurada)
            </p>
            <input
              type="text"
              value={shodanQuery}
              onChange={(e) => setShodanQuery(e.target.value)}
              placeholder="Query Shodan (ej: org:Example OR hostname:example.com)"
              className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-600 mb-3"
            />
            <button
              onClick={() => handleShodanWithPreview(shodanQuery || target)}
              disabled={shodanMutation.isPending || !target.trim()}
              className="w-full bg-red-600 hover:bg-red-700 disabled:bg-red-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
            >
              {shodanMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Shield className="w-4 h-4" />
              )}
              Iniciar Búsqueda Shodan
            </button>
          </div>

          {/* Censys */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-rose-400 mb-2">Censys Search</h4>
            <p className="text-sm text-gray-500 mb-3">
              Busca información en Censys (requiere API credentials configuradas)
            </p>
            <input
              type="text"
              value={censysQuery}
              onChange={(e) => setCensysQuery(e.target.value)}
              placeholder="Query Censys (ej: example.com)"
              className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-600 mb-3"
            />
            <div className="grid grid-cols-2 gap-2 mb-3">
              <select
                value={censysIndex}
                onChange={(e) => setCensysIndex(e.target.value)}
                className="bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-600 text-sm"
              >
                <option value="hosts">Hosts</option>
                <option value="certificates">Certificates</option>
              </select>
            </div>
            <button
              onClick={() => handleCensysWithPreview(censysQuery || target, censysIndex)}
              disabled={censysMutation.isPending || !target.trim()}
              className="w-full bg-rose-600 hover:bg-rose-700 disabled:bg-rose-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
            >
              {censysMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Shield className="w-4 h-4" />
              )}
              Iniciar Búsqueda Censys
            </button>
          </div>

          {/* Google Dorks */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-purple-400 mb-2">Google Dorks</h4>
            <p className="text-sm text-gray-500 mb-3">
              Búsquedas avanzadas en Google (manual o automatizado)
            </p>
            <div className="grid grid-cols-2 gap-2 mb-3">
              <select
                value={googleDorksTool}
                onChange={(e) => setGoogleDorksTool(e.target.value)}
                className="bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-600 text-sm"
              >
                <option value="manual">Manual</option>
                <option value="goofuzz">GooFuzz</option>
                <option value="pagodo">Pagodo</option>
                <option value="dorkscanner">dorkScanner</option>
              </select>
            </div>
            <input
              type="text"
              value={googleDorksQuery}
              onChange={(e) => setGoogleDorksQuery(e.target.value)}
              placeholder="Dork query (opcional, ej: site:example.com filetype:pdf)"
              className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-600 mb-3"
            />
            <button
              onClick={() => handleGoogleDorksWithPreview(googleDorksQuery || undefined, googleDorksTool)}
              disabled={googleDorksMutation.isPending || !target.trim()}
              className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
            >
              {googleDorksMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              Iniciar Google Dorks
            </button>
          </div>

          {/* Hunter.io */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-indigo-400 mb-2">Hunter.io</h4>
            <p className="text-sm text-gray-500 mb-3">
              Busca emails corporativos usando Hunter.io API
            </p>
            <input
              type="text"
              value={hunterApiKey}
              onChange={(e) => setHunterApiKey(e.target.value)}
              placeholder="API Key (opcional, puede estar en env)"
              className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-600 mb-3"
            />
            <button
              onClick={() => handleHunterIoWithPreview(hunterApiKey || undefined)}
              disabled={hunterIoMutation.isPending || !target.trim()}
              className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
            >
              {hunterIoMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Mail className="w-4 h-4" />
              )}
              Iniciar Búsqueda Hunter.io
            </button>
          </div>

          {/* LinkedIn Enumeration */}
          <div className="bg-gray-100 rounded-xl p-4 border border-gray-200">
            <h4 className="text-md font-semibold text-blue-400 mb-2">LinkedIn Enumeration</h4>
            <p className="text-sm text-gray-500 mb-3">
              Enumera empleados usando LinkedIn
            </p>
            <div className="grid grid-cols-2 gap-2 mb-3">
              <select
                value={linkedinTool}
                onChange={(e) => setLinkedinTool(e.target.value)}
                className="bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-600 text-sm"
              >
                <option value="crosslinked">CrossLinked</option>
                <option value="linkedin2username">linkedin2username</option>
              </select>
            </div>
            <input
              type="text"
              value={linkedinCompany}
              onChange={(e) => setLinkedinCompany(e.target.value)}
              placeholder="Nombre de la compañía (opcional)"
              className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-600 mb-3"
            />
            <button
              onClick={() => handleLinkedInEnumWithPreview(linkedinTool, linkedinCompany || undefined)}
              disabled={linkedinEnumMutation.isPending || !target.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
            >
              {linkedinEnumMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Network className="w-4 h-4" />
              )}
              Iniciar LinkedIn Enum
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

