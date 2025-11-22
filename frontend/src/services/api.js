import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (email, password) => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    return axios.post(`${API_BASE_URL}/auth/login`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(res => res.data)
  },
  
  register: (email, password, fullName) => {
    return api.post('/auth/register', { email, password, full_name: fullName })
      .then(res => res.data)
  },
  
  getCurrentUser: (token) => {
    return axios.get(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then(res => res.data)
  },
}

export const meetingsAPI = {
  list: () => api.get('/meetings').then(res => res.data),
  get: (id) => api.get(`/meetings/${id}`).then(res => res.data),
  upload: (file, title, isLocalOnly) => {
    const formData = new FormData()
    formData.append('file', file)
    if (title) formData.append('title', title)
    formData.append('is_local_only', isLocalOnly)
    return api.post('/meetings/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(res => res.data)
  },
  delete: (id) => api.delete(`/meetings/${id}`).then(res => res.data),
}

export const tasksAPI = {
  list: (meetingId, statusFilter) => {
    const params = {}
    if (meetingId) params.meeting_id = meetingId
    if (statusFilter) params.status_filter = statusFilter
    return api.get('/tasks', { params }).then(res => res.data)
  },
  get: (id) => api.get(`/tasks/${id}`).then(res => res.data),
  update: (id, updates) => api.patch(`/tasks/${id}`, updates).then(res => res.data),
  delete: (id) => api.delete(`/tasks/${id}`).then(res => res.data),
  confirm: (id) => api.post(`/tasks/${id}/confirm`).then(res => res.data),
  sync: (id, service, projectKey, listId) => {
    return api.post(`/tasks/${id}/sync`, {
      service,
      project_key: projectKey,
      list_id: listId,
    }).then(res => res.data)
  },
}

export const integrationsAPI = {
  list: () => api.get('/integrations').then(res => res.data),
  get: (id) => api.get(`/integrations/${id}`).then(res => res.data),
  create: (serviceType, config) => {
    return api.post('/integrations', {
      service_type: serviceType,
      config,
    }).then(res => res.data)
  },
  delete: (id) => api.delete(`/integrations/${id}`).then(res => res.data),
  toggle: (id) => api.patch(`/integrations/${id}/toggle`).then(res => res.data),
}

export default api

