/**
 * NetworkTopologyGraph - Grafo interactivo de topología de red
 * Muestra hosts, servicios y conexiones descubiertas
 * Usa React Flow para interactividad (zoom, pan, drag)
 */

import React, { useCallback, useMemo } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Connection,
  addEdge,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { motion } from 'framer-motion'
import { CHART_COLORS, getSeverityColor } from '../../config/chartConfig'
import ChartContainer from './ChartContainer'
import { Server, Shield, AlertTriangle, Globe } from 'lucide-react'

interface NetworkHost {
  id: string
  ip: string
  hostname?: string
  os?: string
  openPorts: number[]
  vulnerabilities: number
  severity: 'critical' | 'high' | 'medium' | 'low'
  services?: Array<{
    port: number
    service: string
    version?: string
  }>
}

interface NetworkConnection {
  from: string
  to: string
  type?: 'http' | 'ssh' | 'database' | 'other'
  protocol?: string
}

interface NetworkTopologyGraphProps {
  hosts: NetworkHost[]
  connections?: NetworkConnection[]
  title?: string
  description?: string
  isLoading?: boolean
  onRefresh?: () => void
  onHostClick?: (host: NetworkHost) => void
}

const NetworkTopologyGraph: React.FC<NetworkTopologyGraphProps> = ({
  hosts,
  connections = [],
  title = 'Topología de Red',
  description = 'Mapa interactivo de hosts y servicios descubiertos',
  isLoading = false,
  onRefresh,
  onHostClick,
}) => {
  // Convertir hosts a nodos de React Flow
  const initialNodes = useMemo<Node[]>(() => {
    return hosts.map((host, index) => {
      // Layout en círculo para mejor visualización
      const angle = (index / hosts.length) * 2 * Math.PI
      const radius = Math.min(200, hosts.length * 30)
      const x = 400 + radius * Math.cos(angle)
      const y = 300 + radius * Math.sin(angle)

      // Color basado en severidad
      const severityColor = getSeverityColor(host.severity)
      const bgColor = severityColor + '20' // Agregar transparencia

      return {
        id: host.id,
        type: 'default',
        position: { x, y },
        data: {
          label: (
            <div className="px-3 py-2">
              <div className="flex items-center space-x-2 mb-1">
                <Server className="w-4 h-4" />
                <span className="font-semibold text-sm text-white">
                  {host.hostname || host.ip}
                </span>
              </div>
              <div className="text-xs text-gray-400">{host.ip}</div>
              {host.vulnerabilities > 0 && (
                <div className="flex items-center space-x-1 mt-1">
                  <AlertTriangle className="w-3 h-3 text-red-400" />
                  <span className="text-xs text-red-400">
                    {host.vulnerabilities} vulns
                  </span>
                </div>
              )}
            </div>
          ),
          host,
        },
        style: {
          background: bgColor,
          border: `2px solid ${severityColor}`,
          borderRadius: '8px',
          minWidth: 150,
          color: '#fff',
        },
      }
    })
  }, [hosts])

  // Convertir conexiones a edges de React Flow
  const initialEdges = useMemo<Edge[]>(() => {
    return connections.map((conn) => ({
      id: `${conn.from}-${conn.to}`,
      source: conn.from,
      target: conn.to,
      type: 'smoothstep',
      animated: conn.type === 'http',
      style: {
        stroke: CHART_COLORS.text.secondary,
        strokeWidth: 2,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: CHART_COLORS.text.secondary,
      },
      label: conn.type || conn.protocol || '',
      labelStyle: {
        fill: CHART_COLORS.text.secondary,
        fontSize: 10,
      },
    }))
  }, [connections])

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  // Actualizar cuando cambian los datos
  React.useEffect(() => {
    setNodes(initialNodes)
    setEdges(initialEdges)
  }, [initialNodes, initialEdges, setNodes, setEdges])

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  // Custom node styles
  const nodeTypes = useMemo(
    () => ({
      default: ({ data }: any) => (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.3 }}
          className="px-4 py-3 bg-gray-800 border-2 rounded-lg cursor-pointer hover:shadow-lg transition-shadow"
          style={{
            borderColor: getSeverityColor(data.host.severity),
            backgroundColor: getSeverityColor(data.host.severity) + '20',
          }}
          onClick={() => onHostClick?.(data.host)}
        >
          {data.label}
        </motion.div>
      ),
    }),
    [onHostClick]
  )

  const isEmpty = hosts.length === 0

  return (
    <ChartContainer
      title={title}
      description={description}
      isLoading={isLoading}
      isEmpty={isEmpty}
      emptyMessage="No hay hosts descubiertos para mostrar"
      onRefresh={onRefresh}
      height={600}
    >
      <div className="w-full h-full relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
          className="bg-gray-900"
        >
          <Background color="#374151" gap={16} />
          <Controls
            style={{
              backgroundColor: '#1F2937',
              border: '1px solid #4B5563',
            }}
          />
          <MiniMap
            style={{
              backgroundColor: '#1F2937',
              border: '1px solid #4B5563',
            }}
            nodeColor={(node: any) => {
              const host = node.data?.host
              if (!host) return '#6B7280'
              return getSeverityColor(host.severity)
            }}
            maskColor="rgba(0, 0, 0, 0.5)"
          />
        </ReactFlow>

        {/* Legend */}
        <div className="absolute top-4 right-4 bg-gray-800/90 border border-gray-700 rounded-lg p-4 space-y-2 z-10">
          <div className="text-white font-semibold text-sm mb-2">Leyenda</div>
          {['critical', 'high', 'medium', 'low'].map((severity) => {
            const count = hosts.filter((h) => h.severity === severity).length
            if (count === 0) return null

            return (
              <div key={severity} className="flex items-center space-x-2 text-xs">
                <div
                  className="w-3 h-3 rounded-full border-2"
                  style={{
                    backgroundColor: getSeverityColor(severity) + '40',
                    borderColor: getSeverityColor(severity),
                  }}
                />
                <span className="text-gray-300 capitalize">{severity}</span>
                <span className="text-gray-500">({count})</span>
              </div>
            )
          })}
        </div>

        {/* Stats */}
        <div className="absolute bottom-4 left-4 bg-gray-800/90 border border-gray-700 rounded-lg p-3 z-10">
          <div className="text-xs text-gray-400 space-y-1">
            <div className="flex items-center space-x-2">
              <Globe className="w-3 h-3" />
              <span>{hosts.length} hosts</span>
            </div>
            <div className="flex items-center space-x-2">
              <Shield className="w-3 h-3" />
              <span>
                {hosts.reduce((sum, h) => sum + h.vulnerabilities, 0)} vulnerabilidades
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <Server className="w-3 h-3" />
              <span>
                {hosts.reduce((sum, h) => sum + h.openPorts.length, 0)} puertos abiertos
              </span>
            </div>
          </div>
        </div>
      </div>
    </ChartContainer>
  )
}

export default NetworkTopologyGraph




