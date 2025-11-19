import { Routes, Route, Navigate } from "react-router-dom";
import { useEffect } from "react";
import { useAuthStore } from "./store/authStore";
import { userService } from "./services/userService";

// Pages
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import SetupLearningPage from "./pages/SetupLearningPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import OAuthCallback from "./pages/OAuthCallback";
import DashboardPage from "./pages/DashboardPage";
import ProfileOverview from "./pages/ProfileOverview";
import DocumentsPage from "./pages/DocumentsPage";
import FlashcardsPage from "./pages/FlashcardsPage";
import QuizzesPage from "./pages/QuizzesPage";
import QuizGenerationPage from "./pages/QuizGenerationPage";
import QuizTakingPage from "./pages/QuizTakingPage";
import QuizResultPage from "./pages/QuizResultPage";
import QuizEditPage from "./pages/QuizEditPage";
import FlashcardGenerationPage from "./pages/FlashcardGenerationPage";
import DocumentDetailPage from "./pages/DocumentDetailPage";
import ProgressPage from "./pages/ProgressPage";
import QuickQuizPage from "./pages/QuickQuizPage";
import FlashcardReviewPage from "./pages/FlashcardReviewPage";
import FlashcardSetDetailPage from "./pages/FlashcardSetDetailPage";
import LearningGoalsPage from "./pages/LearningGoalsPage";
import RecommendationsPage from "./pages/RecommendationsPage";
import StudySchedulePage from "./pages/StudySchedulePage";
import NotificationsPage from "./pages/NotificationsPage";

// Components
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  const { token, updateUser, logout } = useAuthStore();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const user = await userService.getProfile();
        if (user) updateUser(user);
      } catch (err) {
        console.error("❌ Failed to fetch user:", err);
        logout(); // If token expires then logout
      }
    };

    if (token) fetchUser();
  }, [token]);

  return (
    <div className="min-h-screen bg-background">
      <Routes>
        {/* ==== Public routes ==== */}
        <Route
          path="/"
          element={token ? <Navigate to="/dashboard" /> : <LandingPage />}
        />
        <Route
          path="/login"
          element={token ? <Navigate to="/dashboard" /> : <LoginPage />}
        />
        <Route
          path="/register"
          element={token ? <Navigate to="/dashboard" /> : <RegisterPage />}
        />
        <Route
          path="/forgot-password"
          element={
            token ? <Navigate to="/dashboard" /> : <ForgotPasswordPage />
          }
        />
        <Route
          path="/reset-password"
          element={token ? <Navigate to="/dashboard" /> : <ResetPasswordPage />}
        />

        {/* OAuth callback routes */}
        <Route path="/auth/oauth/google/callback" element={<OAuthCallback />} />
        <Route
          path="/auth/oauth/microsoft/callback"
          element={<OAuthCallback />}
        />
        <Route path="/auth/oauth/github/callback" element={<OAuthCallback />} />

        {/* ==== Protected routes ==== */}

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

        {/* Adaptive Learning */}
        <Route
          path="/today-plan"
          element={<Navigate to="/study-schedule" replace />}
        />

        <Route
          path="/learning-goals"
          element={
            <ProtectedRoute>
              <Layout>
                <LearningGoalsPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/recommendations"
          element={
            <ProtectedRoute>
              <Layout>
                <RecommendationsPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/study-schedule"
          element={
            <ProtectedRoute>
              <Layout>
                <StudySchedulePage />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Profile */}
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

        {/* Documents */}
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

        {/* Flashcards */}
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

        {/* Quizzes */}
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

        {/* AI Generation */}
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

        {/* Quiz Taking */}
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

        {/* Review + Quick Quiz */}
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

        {/* ===================== */}
        {/* 👉 NEW: Notifications Page */}
        {/* ===================== */}
        <Route
          path="/notifications"
          element={
            <ProtectedRoute>
              <Layout>
                <NotificationsPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  );
}

export default App;

