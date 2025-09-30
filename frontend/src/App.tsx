import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'

// Pages
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import OAuthCallback from './pages/OAuthCallback'
import DashboardPage from './pages/DashboardPage'
import DocumentsPage from './pages/DocumentsPage'
import FlashcardsPage from './pages/FlashcardsPage'
import QuizzesPage from './pages/QuizzesPage'
import QuizGenerationPage from './pages/QuizGenerationPage'
import QuizTakingPage from './pages/QuizTakingPage'
import QuizResultPage from './pages/QuizResultPage'
import FlashcardGenerationPage from './pages/FlashcardGenerationPage'
import DocumentDetailPage from './pages/DocumentDetailPage'
import ProgressPage from './pages/ProgressPage'

// Components
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  const { token } = useAuthStore()

  return (
    <div className="min-h-screen bg-background">
      <Routes>
        {/* Public routes */}
        <Route path="/" element={token ? <Navigate to="/dashboard" /> : <LandingPage />} />
        <Route path="/login" element={token ? <Navigate to="/dashboard" /> : <LoginPage />} />
        <Route path="/register" element={token ? <Navigate to="/dashboard" /> : <RegisterPage />} />

        {/* OAuth callback routes */}
        <Route path="/auth/google/callback" element={<OAuthCallback />} />
        <Route path="/auth/microsoft/callback" element={<OAuthCallback />} />
        <Route path="/auth/github/callback" element={<OAuthCallback />} />
        
        {/* Protected routes */}
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
          path="/documents/:documentId"
          element={
            <ProtectedRoute>
              <Layout>
                <DocumentDetailPage />
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
        <Route
          path="/progress"
          element={
            <ProtectedRoute>
              <Layout>
                <ProgressPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* AI Generation Routes */}
        <Route
          path="/documents/:documentId/quiz"
          element={
            <ProtectedRoute>
              <Layout>
                <QuizGenerationPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/documents/:documentId/flashcards"
          element={
            <ProtectedRoute>
              <Layout>
                <FlashcardGenerationPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Quiz Taking Routes */}
        <Route
          path="/quizzes/:quizId/take"
          element={
            <ProtectedRoute>
              <Layout>
                <QuizTakingPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/attempts/:attemptId/results"
          element={
            <ProtectedRoute>
              <Layout>
                <QuizResultPage />
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
