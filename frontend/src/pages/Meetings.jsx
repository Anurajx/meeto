import React, { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { meetingsAPI } from '../services/api'
import {
  PlusIcon,
  TrashIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline'

const Meetings = () => {
  const [meetings, setMeetings] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [title, setTitle] = useState('')
  const [isLocalOnly, setIsLocalOnly] = useState(false)
  const fileInputRef = useRef(null)

  useEffect(() => {
    fetchMeetings()
  }, [])

  const fetchMeetings = async () => {
    try {
      const data = await meetingsAPI.list()
      setMeetings(data)
    } catch (error) {
      console.error('Failed to fetch meetings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    const file = fileInputRef.current?.files[0]
    if (!file) return

    setUploading(true)
    try {
      await meetingsAPI.upload(file, title || undefined, isLocalOnly)
      setShowUploadModal(false)
      setTitle('')
      setIsLocalOnly(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      fetchMeetings()
    } catch (error) {
      console.error('Failed to upload meeting:', error)
      alert('Failed to upload meeting. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this meeting?')) {
      return
    }

    try {
      await meetingsAPI.delete(id)
      fetchMeetings()
    } catch (error) {
      console.error('Failed to delete meeting:', error)
      alert('Failed to delete meeting. Please try again.')
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'processing':
        return <ClockIcon className="h-5 w-5 text-yellow-500 animate-spin" />
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />
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
          <h1 className="text-3xl font-bold text-gray-900">Meetings</h1>
          <p className="mt-2 text-gray-600">Manage your meeting recordings</p>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Upload Meeting
        </button>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Upload Meeting Audio
              </h3>
              <form onSubmit={handleUpload}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title (optional)
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Meeting title"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Audio File
                  </label>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".mp3,.wav,.m4a,.ogg,.flac"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div className="mb-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={isLocalOnly}
                      onChange={(e) => setIsLocalOnly(e.target.checked)}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      Process locally only (no data sent externally)
                    </span>
                  </label>
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowUploadModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={uploading}
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
                  >
                    {uploading ? 'Uploading...' : 'Upload'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Meetings List */}
      {meetings.length === 0 ? (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <p className="text-gray-500 mb-4">No meetings yet</p>
          <button
            onClick={() => setShowUploadModal(true)}
            className="text-primary-600 hover:text-primary-500"
          >
            Upload your first meeting
          </button>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {meetings.map((meeting) => (
              <li key={meeting.id}>
                <Link
                  to={`/meetings/${meeting.id}`}
                  className="block hover:bg-gray-50 px-4 py-4 sm:px-6"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center flex-1 min-w-0">
                      {getStatusIcon(meeting.status)}
                      <div className="ml-4 flex-1">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {meeting.title || 'Untitled Meeting'}
                        </p>
                        <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                          <span>
                            {new Date(meeting.created_at).toLocaleString()}
                          </span>
                          {meeting.is_local_only && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                              Local Only
                            </span>
                          )}
                          {meeting.is_redacted && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                              Redacted
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          meeting.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : meeting.status === 'processing'
                            ? 'bg-yellow-100 text-yellow-800'
                            : meeting.status === 'failed'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {meeting.status}
                      </span>
                      <button
                        onClick={(e) => {
                          e.preventDefault()
                          e.stopPropagation()
                          handleDelete(meeting.id)
                        }}
                        className="text-red-600 hover:text-red-800"
                      >
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default Meetings

