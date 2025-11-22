import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { meetingsAPI, tasksAPI } from '../services/api'
import {
  MicrophoneIcon,
  ClipboardDocumentListIcon,
  CheckCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalMeetings: 0,
    totalTasks: 0,
    pendingTasks: 0,
    confirmedTasks: 0,
  })
  const [recentMeetings, setRecentMeetings] = useState([])
  const [recentTasks, setRecentTasks] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [meetings, tasks] = await Promise.all([
        meetingsAPI.list(),
        tasksAPI.list(),
      ])

      setRecentMeetings(meetings.slice(0, 5))
      setRecentTasks(tasks.slice(0, 5))

      setStats({
        totalMeetings: meetings.length,
        totalTasks: tasks.length,
        pendingTasks: tasks.filter((t) => t.status === 'pending').length,
        confirmedTasks: tasks.filter((t) => t.status === 'confirmed').length,
      })
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
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

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Overview of your meetings and tasks</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <MicrophoneIcon className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Meetings
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.totalMeetings}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClipboardDocumentListIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Tasks
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.totalTasks}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Pending Tasks
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.pendingTasks}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Confirmed Tasks
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.confirmedTasks}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Meetings and Tasks */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Meetings */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Recent Meetings
            </h3>
            <div className="space-y-3">
              {recentMeetings.length === 0 ? (
                <p className="text-sm text-gray-500">No meetings yet</p>
              ) : (
                recentMeetings.map((meeting) => (
                  <Link
                    key={meeting.id}
                    to={`/meetings/${meeting.id}`}
                    className="block p-3 rounded-md hover:bg-gray-50 border border-gray-200"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {meeting.title || 'Untitled Meeting'}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(meeting.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <span
                        className={`ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          meeting.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : meeting.status === 'processing'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {meeting.status}
                      </span>
                    </div>
                  </Link>
                ))
              )}
            </div>
            <div className="mt-4">
              <Link
                to="/meetings"
                className="text-sm text-primary-600 hover:text-primary-500"
              >
                View all meetings →
              </Link>
            </div>
          </div>
        </div>

        {/* Recent Tasks */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Recent Tasks
            </h3>
            <div className="space-y-3">
              {recentTasks.length === 0 ? (
                <p className="text-sm text-gray-500">No tasks yet</p>
              ) : (
                recentTasks.map((task) => (
                  <Link
                    key={task.id}
                    to="/tasks"
                    className="block p-3 rounded-md hover:bg-gray-50 border border-gray-200"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900">{task.description}</p>
                        <div className="mt-1 flex items-center space-x-2">
                          {task.owner_name && (
                            <span className="text-xs text-gray-500">
                              Owner: {task.owner_name}
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
                        </div>
                      </div>
                    </div>
                  </Link>
                ))
              )}
            </div>
            <div className="mt-4">
              <Link
                to="/tasks"
                className="text-sm text-primary-600 hover:text-primary-500"
              >
                View all tasks →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

