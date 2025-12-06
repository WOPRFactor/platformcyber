import React from 'react'
import { Activity } from 'lucide-react'
import TaskMonitor from '../../../components/TaskMonitor'
import VulnerabilityAlerts from '../../../components/VulnerabilityAlerts'

interface Task {
  status: string
}

interface Vulnerability {
  id: string
}

interface RealTimeActivityProps {
  tasks: Task[]
  vulnerabilities: Vulnerability[]
}

export const RealTimeActivity: React.FC<RealTimeActivityProps> = ({ tasks, vulnerabilities }) => {
  const activeTasks = tasks.filter(t => t.status === 'STARTED').length
  const completedTasks = tasks.filter(t => t.status === 'SUCCESS').length

  return (
    <>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div>
          <TaskMonitor maxDisplay={5} showCompleted={false} />
        </div>

        <div>
          <VulnerabilityAlerts maxDisplay={5} autoScroll={true} />
        </div>
      </div>

      {(tasks.length > 0 || vulnerabilities.length > 0) && (
        <div className="mt-6 bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded-lg p-6 border border-blue-500/20">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-blue-400" />
            Real-Time Activity
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-800/50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-blue-400 mb-1">
                {activeTasks}
              </div>
              <div className="text-sm text-gray-400">Active Tasks</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-purple-400 mb-1">
                {vulnerabilities.length}
              </div>
              <div className="text-sm text-gray-400">Vulnerabilities Found</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-green-400 mb-1">
                {completedTasks}
              </div>
              <div className="text-sm text-gray-400">Completed</div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}


