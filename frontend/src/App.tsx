import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from './store/authStore'
import { userService } from './services/userService' // ✅ thêm dòng này

// Pages
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import SetupLearningPage from "./pages/SetupLearningPage"
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import OAuthCallback from './pages/OAuthCallback'
import DashboardPage from './pages/DashboardPage'
import ProfileOverview from './pages/ProfileOverview'
import DocumentsPage from './pages/DocumentsPage'
import FlashcardsPage from './pages/FlashcardsPage'
import QuizzesPage from './pages/QuizzesPage'

// Components
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  const { token, updateUser, logout } = useAuthStore()

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const user = await userService.getProfile()
        if (user) updateUser(user)
      } catch (err) {
        console.error('❌ Failed to fetch user:', err)
        logout() // nếu token hết hạn thì logout
      }
    }

    if (token) fetchUser()
  }, [token, updateUser, logout])

  return (
    <div className="min-h-screen bg-background">
      <Routes>
        {/* Public routes */}
        <Route path="/" element={token ? <Navigate to="/dashboard" /> : <LandingPage />} />
        <Route path="/login" element={token ? <Navigate to="/dashboard" /> : <LoginPage />} />
        <Route path="/register" element={token ? <Navigate to="/dashboard" /> : <RegisterPage />} />
        <Route path="/forgot-password" element={token ? <Navigate to="/dashboard" /> : <ForgotPasswordPage />} />
        <Route path="/reset-password" element={token ? <Navigate to="/dashboard" /> : <ResetPasswordPage />} />

        {/* OAuth callback routes */}
        <Route path="/auth/oauth/google/callback" element={<OAuthCallback />} />
        <Route path="/auth/oauth/microsoft/callback" element={<OAuthCallback />} />
        <Route path="/auth/oauth/github/callback" element={<OAuthCallback />} />

        {/* Protected routes */}
        <Route
  path="/setup-learning"
  element={
    <ProtectedRoute>
      <SetupLearningPage />
    </ProtectedRoute>
  }
/>
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <DashboardPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Layout>
                <ProfileOverview />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/documents"
          element={
            <ProtectedRoute>
              <Layout>
                <DocumentsPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/flashcards"
          element={
            <ProtectedRoute>
              <Layout>
                <FlashcardsPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/quizzes"
          element={
            <ProtectedRoute>
              <Layout>
                <QuizzesPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  )
}

export default App
