import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import PrivateRoute from './components/PrivateRoute'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Meetings from './pages/Meetings'
import MeetingDetail from './pages/MeetingDetail'
import Tasks from './pages/Tasks'
import Integrations from './pages/Integrations'
import Layout from './components/Layout'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/meetings"
            element={
              <PrivateRoute>
                <Layout>
                  <Meetings />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/meetings/:id"
            element={
              <PrivateRoute>
                <Layout>
                  <MeetingDetail />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/tasks"
            element={
              <PrivateRoute>
                <Layout>
                  <Tasks />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/integrations"
            element={
              <PrivateRoute>
                <Layout>
                  <Integrations />
                </Layout>
              </PrivateRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App

