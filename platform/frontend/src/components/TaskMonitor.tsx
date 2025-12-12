/**
 * Task Monitor Component
 * ======================
 * 
 * Monitorea el estado de tareas Celery en tiempo real.
 */

import React from 'react';
import { useTaskUpdates, TaskUpdateEvent } from '../contexts/WebSocketContext';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { Clock, CheckCircle, XCircle, Loader, Pause } from 'lucide-react';

interface TaskCardProps {
  task: TaskUpdateEvent;
}

const TaskCard: React.FC<TaskCardProps> = ({ task }) => {
  const getStatusIcon = () => {
    switch (task.status) {
      case 'SUCCESS':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'FAILURE':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'STARTED':
        return <Loader className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'PENDING':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      default:
        return <Pause className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = () => {
    switch (task.status) {
      case 'SUCCESS':
        return 'border-green-500 bg-green-500/5';
      case 'FAILURE':
        return 'border-red-500 bg-red-500/5';
      case 'STARTED':
        return 'border-blue-500 bg-blue-500/5';
      case 'PENDING':
        return 'border-yellow-500 bg-yellow-500/5';
      default:
        return 'border-gray-500 bg-gray-500/5';
    }
  };

  const getProgressColor = () => {
    switch (task.status) {
      case 'SUCCESS':
        return 'bg-green-500';
      case 'FAILURE':
        return 'bg-red-500';
      case 'STARTED':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div
      className={`
        border-l-4 rounded-lg p-4 transition-all duration-200
        ${getStatusColor()}
      `}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          {getStatusIcon()}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-1">
              <h4 className="font-medium text-gray-200 text-sm truncate">
                Task {task.task_id.substring(0, 8)}...
              </h4>
              <span
                className={`
                  text-xs px-2 py-0.5 rounded-full font-medium uppercase
                  ${task.status === 'SUCCESS' ? 'bg-green-500/20 text-green-400' : ''}
                  ${task.status === 'FAILURE' ? 'bg-red-500/20 text-red-400' : ''}
                  ${task.status === 'STARTED' ? 'bg-blue-500/20 text-blue-400' : ''}
                  ${task.status === 'PENDING' ? 'bg-yellow-500/20 text-yellow-400' : ''}
                `}
              >
                {task.status}
              </span>
            </div>

            {/* Progress Bar */}
            {task.progress !== undefined && task.status === 'STARTED' && (
              <div className="mt-2 mb-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-400">Progress</span>
                  <span className="text-xs text-gray-300 font-semibold">{task.progress}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full ${getProgressColor()} transition-all duration-300 ease-out`}
                    style={{ width: `${Math.min(task.progress, 100)}%` }}
                  />
                </div>
              </div>
            )}

            {/* Result or Error */}
            {task.result && task.status === 'SUCCESS' && (
              <div className="mt-2 text-xs text-gray-400">
                <span className="font-medium">Result:</span>{' '}
                {typeof task.result === 'string' 
                  ? task.result 
                  : task.result.message || 'Task completed successfully'
                }
              </div>
            )}

            {task.error && task.status === 'FAILURE' && (
              <div className="mt-2 text-xs text-red-400">
                <span className="font-medium">Error:</span> {task.error}
              </div>
            )}

            {/* Timestamp */}
            <div className="mt-2 text-xs text-gray-500">
              {new Date(task.timestamp * 1000).toLocaleString()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

interface TaskMonitorProps {
  maxDisplay?: number;
  showCompleted?: boolean;
}

export const TaskMonitor: React.FC<TaskMonitorProps> = ({
  maxDisplay = 10,
  showCompleted = true
}) => {
  const { currentWorkspace } = useWorkspace();
  const workspaceId = currentWorkspace?.id || null;

  const tasks = useTaskUpdates(workspaceId);

  // Filter tasks
  const filteredTasks = showCompleted 
    ? tasks 
    : tasks.filter(t => t.status !== 'SUCCESS' && t.status !== 'FAILURE');

  // Limitar cantidad mostrada
  const displayedTasks = filteredTasks.slice(-maxDisplay).reverse();

  // Statistics
  const stats = {
    total: tasks.length,
    pending: tasks.filter(t => t.status === 'PENDING').length,
    running: tasks.filter(t => t.status === 'STARTED').length,
    success: tasks.filter(t => t.status === 'SUCCESS').length,
    failed: tasks.filter(t => t.status === 'FAILURE').length,
  };

  if (tasks.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg shadow p-6 text-center">
        <div className="text-6xl mb-4">📋</div>
        <h3 className="text-lg font-semibold text-gray-300 mb-2">
          No Tasks Running
        </h3>
        <p className="text-sm text-gray-500">
          Tasks will appear here when scans or operations are running.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg shadow">
      {/* Header with Stats */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-200">
            📋 Active Tasks
          </h3>
          <span className="bg-blue-500 text-white text-sm px-3 py-1 rounded-full font-semibold">
            {stats.running + stats.pending}
          </span>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <StatCard
            label="Running"
            value={stats.running}
            color="text-blue-400"
            icon="🔄"
          />
          <StatCard
            label="Pending"
            value={stats.pending}
            color="text-yellow-400"
            icon="⏳"
          />
          <StatCard
            label="Completed"
            value={stats.success}
            color="text-green-400"
            icon="✅"
          />
          <StatCard
            label="Failed"
            value={stats.failed}
            color="text-red-400"
            icon="❌"
          />
        </div>
      </div>

      {/* Tasks List */}
      <div className="p-4 space-y-3 max-h-[600px] overflow-y-auto">
        {displayedTasks.map((task, index) => (
          <TaskCard key={`${task.task_id}-${index}`} task={task} />
        ))}
      </div>

      {/* Footer */}
      {tasks.length > maxDisplay && (
        <div className="p-3 bg-gray-900 border-t border-gray-700 text-center text-sm text-gray-400">
          Showing {displayedTasks.length} of {tasks.length} tasks
        </div>
      )}
    </div>
  );
};

interface StatCardProps {
  label: string;
  value: number;
  color: string;
  icon: string;
}

const StatCard: React.FC<StatCardProps> = ({ label, value, color, icon }) => (
  <div className="bg-gray-900 rounded-lg p-3 text-center">
    <div className="text-2xl mb-1">{icon}</div>
    <div className={`text-2xl font-bold ${color} mb-1`}>{value}</div>
    <div className="text-xs text-gray-500 uppercase">{label}</div>
  </div>
);

export default TaskMonitor;

