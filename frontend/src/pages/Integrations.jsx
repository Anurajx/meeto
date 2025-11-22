import React, { useState, useEffect } from 'react'
import { integrationsAPI } from '../services/api'
import {
  PlusIcon,
  TrashIcon,
  Cog6ToothIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline'

const Integrations = () => {
  const [integrations, setIntegrations] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(null)

  useEffect(() => {
    fetchIntegrations()
  }, [])

  const fetchIntegrations = async () => {
    try {
      const data = await integrationsAPI.list()
      setIntegrations(data)
    } catch (error) {
      console.error('Failed to fetch integrations:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (serviceType, config) => {
    try {
      await integrationsAPI.create(serviceType, config)
      setShowModal(null)
      fetchIntegrations()
    } catch (error) {
      console.error('Failed to create integration:', error)
      alert('Failed to create integration. Please check your credentials.')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this integration?')) {
      return
    }

    try {
      await integrationsAPI.delete(id)
      fetchIntegrations()
    } catch (error) {
      console.error('Failed to delete integration:', error)
      alert('Failed to delete integration')
    }
  }

  const handleToggle = async (id) => {
    try {
      await integrationsAPI.toggle(id)
      fetchIntegrations()
    } catch (error) {
      console.error('Failed to toggle integration:', error)
      alert('Failed to toggle integration')
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
          <h1 className="text-3xl font-bold text-gray-900">Integrations</h1>
          <p className="mt-2 text-gray-600">
            Connect your Jira or Trello accounts to sync tasks
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setShowModal('jira')}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Jira
          </button>
          <button
            onClick={() => setShowModal('trello')}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Trello
          </button>
        </div>
      </div>

      {integrations.length === 0 ? (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <Cog6ToothIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 mb-4">No integrations configured</p>
          <p className="text-sm text-gray-400">
            Connect Jira or Trello to sync your tasks automatically
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {integrations.map((integration) => (
            <div
              key={integration.id}
              className="bg-white shadow rounded-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div
                    className={`h-10 w-10 rounded-full flex items-center justify-center ${
                      integration.service_type === 'jira'
                        ? 'bg-blue-100'
                        : 'bg-green-100'
                    }`}
                  >
                    <Cog6ToothIcon
                      className={`h-6 w-6 ${
                        integration.service_type === 'jira'
                          ? 'text-blue-600'
                          : 'text-green-600'
                      }`}
                    />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900 capitalize">
                      {integration.service_type}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {integration.is_active ? 'Active' : 'Inactive'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {integration.is_active ? (
                    <CheckCircleIcon className="h-6 w-6 text-green-500" />
                  ) : (
                    <XCircleIcon className="h-6 w-6 text-gray-400" />
                  )}
                  <button
                    onClick={() => handleToggle(integration.id)}
                    className={`px-3 py-1 text-xs font-medium rounded-md ${
                      integration.is_active
                        ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    }`}
                  >
                    {integration.is_active ? 'Disable' : 'Enable'}
                  </button>
                  <button
                    onClick={() => handleDelete(integration.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
              <div className="border-t pt-4">
                <p className="text-xs text-gray-500">
                  Configuration details are hidden for security
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Integration Modal */}
      {showModal && (
        <IntegrationModal
          serviceType={showModal}
          onSave={handleCreate}
          onClose={() => setShowModal(null)}
        />
      )}
    </div>
  )
}

const IntegrationModal = ({ serviceType, onSave, onClose }) => {
  const [config, setConfig] = useState({})

  const handleSubmit = (e) => {
    e.preventDefault()
    onSave(serviceType, config)
  }

  const handleChange = (key, value) => {
    setConfig({ ...config, [key]: value })
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Configure {serviceType === 'jira' ? 'Jira' : 'Trello'}
        </h3>
        <form onSubmit={handleSubmit}>
          {serviceType === 'jira' ? (
            <>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Base URL
                </label>
                <input
                  type="url"
                  required
                  placeholder="https://your-domain.atlassian.net"
                  value={config.base_url || ''}
                  onChange={(e) => handleChange('base_url', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  required
                  value={config.email || ''}
                  onChange={(e) => handleChange('email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Token
                </label>
                <input
                  type="password"
                  required
                  placeholder="Get from Jira account settings"
                  value={config.api_token || ''}
                  onChange={(e) => handleChange('api_token', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Default Project Key (optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g., PROJ"
                  value={config.project_key || ''}
                  onChange={(e) => handleChange('project_key', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </>
          ) : (
            <>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Key
                </label>
                <input
                  type="text"
                  required
                  placeholder="Get from Trello developer portal"
                  value={config.api_key || ''}
                  onChange={(e) => handleChange('api_key', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Token
                </label>
                <input
                  type="password"
                  required
                  placeholder="Get from Trello developer portal"
                  value={config.api_token || ''}
                  onChange={(e) => handleChange('api_token', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Board ID (optional)
                </label>
                <input
                  type="text"
                  placeholder="Leave empty to use default"
                  value={config.board_id || ''}
                  onChange={(e) => handleChange('board_id', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </>
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
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Integrations

