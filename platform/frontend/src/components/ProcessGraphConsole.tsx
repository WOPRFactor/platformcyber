import React, { useState } from 'react'
import { X, PieChart } from 'lucide-react'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title } from 'chart.js'
import { useConsole } from '../contexts/ConsoleContext'
import { useWindowManager } from '../contexts/WindowManagerContext'
import { useDragResize } from './ProcessGraphConsole/hooks/useDragResize'
import { usePentestMetrics } from './ProcessGraphConsole/hooks/usePentestMetrics'
import OverviewTab from './ProcessGraphConsole/components/OverviewTab'
import ProgressTab from './ProcessGraphConsole/components/ProgressTab'
import VulnerabilitiesTab from './ProcessGraphConsole/components/VulnerabilitiesTab'
import DiscoveryTab from './ProcessGraphConsole/components/DiscoveryTab'
import ProcessGraphTabs from './ProcessGraphConsole/components/ProcessGraphTabs'

// Registrar componentes de Chart.js
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title
)

interface ProcessGraphConsoleProps {
  isOpen: boolean
  onClose: () => void
}

const ProcessGraphConsole: React.FC<ProcessGraphConsoleProps> = ({ isOpen, onClose }) => {
  const { tasks, logs } = useConsole()
  const { getZIndex, bringToFront } = useWindowManager()
  const [activeTab, setActiveTab] = useState<'overview' | 'progress' | 'vulnerabilities' | 'discovery'>('overview')
  const windowId = 'process-graph-console'

  const {
    modalRef,
    position,
    size,
    isDragging,
    handleMouseDown,
    handleResizeMouseDown
  } = useDragResize({
    onBringToFront: () => bringToFront(windowId)
  })

  const pentestMetrics = usePentestMetrics(tasks, logs)

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-50 pointer-events-none">
      <div
        ref={modalRef}
        className="bg-gray-50 border border-gray-200 rounded-xl shadow-2xl flex flex-col pointer-events-auto"
        style={{
          position: 'absolute',
          left: position.x,
          top: position.y,
          width: size.width,
          height: size.height,
          cursor: isDragging ? 'grabbing' : 'grab',
          zIndex: getZIndex(windowId)
        }}
        onMouseDown={handleMouseDown}
      >
        {/* Header - Draggable */}
        <div className="modal-header flex items-center justify-between p-4 border-b border-gray-200 select-none">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <PieChart className="w-6 h-6" />
            Consola de Gráficos
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded-md text-gray-900 hover:text-gray-700 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Resize Handle */}
        <div
          className="absolute bottom-0 right-0 w-4 h-4 cursor-nw-resize"
          onMouseDown={handleResizeMouseDown}
        >
          <div className="w-full h-full bg-red-600 rounded-tl opacity-50 hover:opacity-100 transition-opacity" />
        </div>

        {/* Tabs */}
        <ProcessGraphTabs activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Content */}
        <div className="flex-1 p-6 overflow-auto">
          {activeTab === 'overview' && <OverviewTab metrics={pentestMetrics} />}
          {activeTab === 'progress' && <ProgressTab tasks={tasks} />}
          {activeTab === 'vulnerabilities' && <VulnerabilitiesTab metrics={pentestMetrics} />}
          {activeTab === 'discovery' && <DiscoveryTab metrics={pentestMetrics} logs={logs} />}
        </div>
      </div>
    </div>
  )
}

export default ProcessGraphConsole

