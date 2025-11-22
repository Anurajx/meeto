import React, { useState, useEffect } from 'react'
import { tasksAPI, integrationsAPI } from '../services/api'
import {
  PencilIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowUpTrayIcon,
} from '@heroicons/react/24/outline'
import { format } from 'date-fns'

const Tasks = () => {
  const [tasks, setTasks] = useState([])
  const [integrations, setIntegrations] = useState([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  const [editingTask, setEditingTask] = useState(null)
  const [showSyncModal, setShowSyncModal] = useState(null)

  useEffect(() => {
    fetchTasks()
    fetchIntegrations()
  }, [statusFilter])

  const fetchTasks = async () => {
    try {
      const data = await tasksAPI.list(null, statusFilter || undefined)
      setTasks(data)
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchIntegrations = async () => {
    try {
      const data = await integrationsAPI.list()
      setIntegrations(data)
    } catch (error) {
      console.error('Failed to fetch integrations:', error)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return
    }

    try {
      await tasksAPI.delete(id)
      fetchTasks()
    } catch (error) {
      console.error('Failed to delete task:', error)
      alert('Failed to delete task')
    }
  }

  const handleConfirm = async (id) => {
    try {
      await tasksAPI.confirm(id)
      fetchTasks()
    } catch (error) {
      console.error('Failed to confirm task:', error)
      alert('Failed to confirm task')
    }
  }

  const handleUpdate = async (task) => {
    try {
      await tasksAPI.update(task.id, {
        description: task.description,
        owner_name: task.owner_name,
        deadline: task.deadline ? new Date(task.deadline) : null,
        priority: task.priority,
      })
      setEditingTask(null)
      fetchTasks()
    } catch (error) {
      console.error('Failed to update task:', error)
      alert('Failed to update task')
    }
  }

  const handleSync = async (taskId, service, projectKey, listId) => {
    try {
      await tasksAPI.sync(taskId, service, projectKey, listId)
      setShowSyncModal(null)
      fetchTasks()
    } catch (error) {
      console.error('Failed to sync task:', error)
      alert(`Failed to sync task: ${error.response?.data?.detail || error.message}`)
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800'
      case 'high':
        return 'bg-orange-100 text-orange-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed':
        return 'bg-blue-100 text-blue-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
          <p className="mt-2 text-gray-600">Manage action items from your meetings</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {tasks.length === 0 ? (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <p className="text-gray-500">No tasks found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((task) => (
            <div
              key={task.id}
              className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              {editingTask?.id === task.id ? (
                <TaskEditForm
                  task={editingTask}
                  onSave={handleUpdate}
                  onCancel={() => setEditingTask(null)}
                />
              ) : (
                <div>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">
                        {task.description}
                      </p>
                      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-gray-500">
                        {task.owner_name && (
                          <span className="inline-flex items-center">
                            👤 {task.owner_name}
                          </span>
                        )}
                        {task.deadline && (
                          <span className="inline-flex items-center">
                            📅 {format(new Date(task.deadline), 'PP')}
                          </span>
                        )}
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded ${getPriorityColor(
                            task.priority
                          )}`}
                        >
                          {task.priority}
                        </span>
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded ${getStatusColor(
                            task.status
                          )}`}
                        >
                          {task.status}
                        </span>
                        {task.confidence && (
                          <span>Confidence: {(task.confidence * 100).toFixed(0)}%</span>
                        )}
                        {task.jira_issue_key && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded bg-blue-100 text-blue-800">
                            Jira: {task.jira_issue_key}
                          </span>
                        )}
                        {task.trello_card_id && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded bg-blue-100 text-blue-800">
                            Trello: {task.trello_card_id.slice(0, 8)}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="ml-4 flex items-center space-x-2">
                      {task.status === 'pending' && (
                        <button
                          onClick={() => handleConfirm(task.id)}
                          className="text-green-600 hover:text-green-800"
                          title="Confirm task"
                        >
                          <CheckCircleIcon className="h-5 w-5" />
                        </button>
                      )}
                      {task.status === 'pending' &&
                        integrations.some((i) => i.is_active && i.service_type === 'jira') && (
                          <button
                            onClick={() => setShowSyncModal({ task, service: 'jira' })}
                            className="text-blue-600 hover:text-blue-800"
                            title="Sync to Jira"
                          >
                            <ArrowUpTrayIcon className="h-5 w-5" />
                          </button>
                        )}
                      {task.status === 'pending' &&
                        integrations.some((i) => i.is_active && i.service_type === 'trello') && (
                          <button
                            onClick={() => setShowSyncModal({ task, service: 'trello' })}
                            className="text-blue-600 hover:text-blue-800"
                            title="Sync to Trello"
                          >
                            <ArrowUpTrayIcon className="h-5 w-5" />
                          </button>
                        )}
                      <button
                        onClick={() => setEditingTask(task)}
                        className="text-gray-600 hover:text-gray-800"
                        title="Edit task"
                      >
                        <PencilIcon className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleDelete(task.id)}
                        className="text-red-600 hover:text-red-800"
                        title="Delete task"
                      >
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Sync Modal */}
      {showSyncModal && (
        <SyncModal
          task={showSyncModal.task}
          service={showSyncModal.service}
          integrations={integrations}
          onSync={handleSync}
          onClose={() => setShowSyncModal(null)}
        />
      )}
    </div>
  )
}

const TaskEditForm = ({ task, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    description: task.description,
    owner_name: task.owner_name || '',
    deadline: task.deadline
      ? format(new Date(task.deadline), 'yyyy-MM-dd')
      : '',
    priority: task.priority,
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSave({ ...task, ...formData })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          rows="3"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Owner
          </label>
          <input
            type="text"
            value={formData.owner_name}
            onChange={(e) => setFormData({ ...formData, owner_name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Deadline
          </label>
          <input
            type="date"
            value={formData.deadline}
            onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Priority
        </label>
        <select
          value={formData.priority}
          onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>
      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
        >
          Save
        </button>
      </div>
    </form>
  )
}

const SyncModal = ({ task, service, integrations, onSync, onClose }) => {
  const [projectKey, setProjectKey] = useState('')
  const [listId, setListId] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    onSync(task.id, service, projectKey || undefined, listId || undefined)
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Sync to {service === 'jira' ? 'Jira' : 'Trello'}
        </h3>
        <form onSubmit={handleSubmit}>
          {service === 'jira' && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project Key
              </label>
              <input
                type="text"
                value={projectKey}
                onChange={(e) => setProjectKey(e.target.value)}
                placeholder="e.g., PROJ"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          )}
          {service === 'trello' && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                List ID (optional)
              </label>
              <input
                type="text"
                value={listId}
                onChange={(e) => setListId(e.target.value)}
                placeholder="Leave empty for default list"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          )}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
            >
              Sync
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Tasks

