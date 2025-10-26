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
import QuizGenerationPage from './pages/QuizGenerationPage'
import QuizTakingPage from './pages/QuizTakingPage'
import QuizResultPage from './pages/QuizResultPage'
import QuizEditPage from './pages/QuizEditPage'
import FlashcardGenerationPage from './pages/FlashcardGenerationPage'
import DocumentDetailPage from './pages/DocumentDetailPage'
import ProgressPage from './pages/ProgressPage'
import QuickQuizPage from './pages/QuickQuizPage'
import FlashcardReviewPage from './pages/FlashcardReviewPage'
import FlashcardSetDetailPage from './pages/FlashcardSetDetailPage'

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
          path="/quizzes/:quizId/edit"
          element={
            <ProtectedRoute>
              <Layout>
                <QuizEditPage />
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

        {/* Review and Quick Quiz Routes */}
        <Route
          path="/flashcards/review"
          element={
            <ProtectedRoute>
              <Layout>
                <FlashcardReviewPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/flashcard-sets/:setId"
          element={
            <ProtectedRoute>
              <Layout>
                <FlashcardSetDetailPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/quizzes/quick"
          element={
            <ProtectedRoute>
              <Layout>
                <QuickQuizPage />
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
