import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { meetingsAPI } from '../services/api'
import { format } from 'date-fns'

const MeetingDetail = () => {
  const { id } = useParams()
  const [meeting, setMeeting] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMeeting()
    // Poll for updates if still processing
    const interval = setInterval(() => {
      if (meeting?.status === 'processing') {
        fetchMeeting()
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [id, meeting?.status])

  const fetchMeeting = async () => {
    try {
      const data = await meetingsAPI.get(id)
      setMeeting(data)
    } catch (error) {
      console.error('Failed to fetch meeting:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!meeting) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Meeting not found</p>
        <Link to="/meetings" className="text-primary-600 hover:text-primary-500 mt-4 inline-block">
          Back to meetings
        </Link>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <Link
          to="/meetings"
          className="text-sm text-primary-600 hover:text-primary-500 mb-4 inline-block"
        >
          ← Back to meetings
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">
          {meeting.title || 'Untitled Meeting'}
        </h1>
        <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
          <span>
            Created: {format(new Date(meeting.created_at), 'PPpp')}
          </span>
          {meeting.processed_at && (
            <span>
              Processed: {format(new Date(meeting.processed_at), 'PPpp')}
            </span>
          )}
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              meeting.status === 'completed'
                ? 'bg-green-100 text-green-800'
                : meeting.status === 'processing'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-red-100 text-red-800'
            }`}
          >
            {meeting.status}
          </span>
        </div>
      </div>

      {meeting.status === 'processing' && (
        <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <p className="text-sm text-yellow-800">
            Processing audio... This may take a few minutes.
          </p>
        </div>
      )}

      {meeting.status === 'failed' && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-sm text-red-800">
            Failed to process meeting. Please try uploading again.
          </p>
        </div>
      )}

      {meeting.transcript && (
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Transcript</h2>
            <div className="prose max-w-none">
              <p className="text-gray-700 whitespace-pre-wrap">{meeting.transcript}</p>
            </div>
          </div>
        </div>
      )}

      {meeting.tasks && meeting.tasks.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Extracted Tasks</h2>
            <div className="space-y-3">
              {meeting.tasks.map((task) => (
                <div
                  key={task.id}
                  className="border border-gray-200 rounded-md p-4 hover:bg-gray-50"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">
                        {task.description}
                      </p>
                      <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                        {task.owner_name && (
                          <span>Owner: {task.owner_name}</span>
                        )}
                        {task.deadline && (
                          <span>
                            Due: {format(new Date(task.deadline), 'PP')}
                          </span>
                        )}
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                            task.priority === 'high' || task.priority === 'critical'
                              ? 'bg-red-100 text-red-800'
                              : task.priority === 'medium'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-green-100 text-green-800'
                          }`}
                        >
                          {task.priority}
                        </span>
                        {task.confidence && (
                          <span>Confidence: {(task.confidence * 100).toFixed(0)}%</span>
                        )}
                      </div>
                    </div>
                    <Link
                      to="/tasks"
                      className="ml-4 text-primary-600 hover:text-primary-500 text-sm"
                    >
                      View →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {meeting.status === 'completed' && (!meeting.tasks || meeting.tasks.length === 0) && (
        <div className="bg-white shadow rounded-lg p-6 text-center">
          <p className="text-gray-500">No action items extracted from this meeting</p>
        </div>
      )}
    </div>
  )
}

export default MeetingDetail

