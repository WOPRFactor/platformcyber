import React from 'react'
import { Search, Loader2 } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { reconnaissanceAPI } from '../../../../lib/api/reconnaissance'
import { commandPreviewAPI } from '../../../../lib/api/command-preview'
import { toast } from 'sonner'
import { useCommandPreview } from '../../../VulnerabilityAssessment/hooks/useCommandPreview'
import { useReconnaissanceScan } from '../../hooks/useReconnaissanceScan'

interface WebCrawlingSectionProps {
  target: string
  workspaceId: number
  commandPreview: ReturnType<typeof useCommandPreview>
}

export const WebCrawlingSection: React.FC<WebCrawlingSectionProps> = ({ target, workspaceId, commandPreview }) => {
  const { startReconScan } = useReconnaissanceScan()
  const { openPreview } = commandPreview

  const crawlMutation = useMutation({
    mutationFn: (tool: string = 'katana') => startReconScan(
      'Web Crawling',
      () => reconnaissanceAPI.crawl(`https://${target}`, workspaceId, tool),
      `crawl ${target}`,
      target
    )
  })

  const handleWebCrawlWithPreview = async (tool: string = 'katana') => {
    if (!target.trim() || !workspaceId) {
      toast.error('Target y workspace son requeridos')
      return
    }

    try {
      const preview = await commandPreviewAPI.previewWebCrawl({
        url: `https://${target}`,
        workspace_id: workspaceId,
        tool: tool
      })

      openPreview(preview, `Web Crawling (${tool})`, async () => {
        await startReconScan(
          'Web Crawling',
          () => reconnaissanceAPI.crawl(preview.parameters.url, workspaceId, preview.parameters.tool),
          preview.command_string,
          preview.parameters.url.replace('https://', '').replace('http://', '')
        )
      })
    } catch (error: any) {
      console.error('Error obteniendo preview:', error)
      toast.error('Error al obtener preview del comando')
    }
  }

  const tools = [
    { id: 'katana', name: 'Katana', desc: 'Crawling rápido con soporte JavaScript' },
    { id: 'gospider', name: 'GoSpider', desc: 'Crawling concurrente y rápido' },
    { id: 'hakrawler', name: 'Hakrawler', desc: 'Crawling ligero y eficiente' }
  ]

  return (
    <div className="mt-4">
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Search className="w-5 h-5" />
            Web Crawling
          </h3>
          <p className="text-gray-500">
            Herramientas de crawling web: Katana, GoSpider y Hakrawler
          </p>
        </div>

        <div className="space-y-4">
          {tools.map((tool) => (
            <div key={tool.id} className="bg-gray-100 rounded-xl p-4 border border-gray-200">
              <h4 className="text-md font-semibold text-teal-400 mb-2">{tool.name}</h4>
              <p className="text-sm text-gray-500 mb-3">{tool.desc}</p>
              <button
                onClick={() => handleWebCrawlWithPreview(tool.id)}
                disabled={crawlMutation.isPending || !target.trim()}
                className="w-full bg-teal-600 hover:bg-teal-700 disabled:bg-teal-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2"
              >
                {crawlMutation.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Search className="w-4 h-4" />
                )}
                Iniciar Crawling con {tool.name}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

