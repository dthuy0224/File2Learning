import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Brain, Plus, Loader2, Play } from 'lucide-react'
import QuizService from '../services/quizService'
import { useQuizzes } from '../hooks/useQuizzes'
import QuizCard from '../components/QuizCard'
import SelectDocumentModal from '../components/SelectDocumentModal'

export default function QuizzesPage() {
  const navigate = useNavigate()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const { data: quizzes, isLoading: quizzesLoading, error } = useQuizzes()

  const handleCreateQuiz = () => {
    setIsModalOpen(true)
  }

  const handleStartQuiz = async (quizId: number) => {
    try {
      await QuizService.startQuizAttempt(quizId)
      navigate(`/quizzes/${quizId}/take`)
    } catch (error) {
      console.error('Failed to start quiz:', error)
    }
  }

  const handleDeleteQuiz = async (quizId: number) => {
    if (!confirm('Are you sure you want to delete this quiz?')) return

    try {
      await QuizService.deleteQuiz(quizId)
    } catch (error) {
      console.error('Failed to delete quiz:', error)
    }
  }

  if (quizzesLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error loading quizzes</p>
          <Button onClick={() => window.location.reload()}>
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Quizzes</h1>
          <p className="text-gray-600 mt-2">Test your knowledge with AI-generated quizzes</p>
        </div>
        <Button
          onClick={handleCreateQuiz}
          className="flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Create Quiz</span>
        </Button>
      </div>

      {/* Quick Start */}
      <Card className="bg-gradient-to-r from-green-500 to-blue-600 text-white">
        <CardHeader>
          <CardTitle className="text-white">Quick Quiz</CardTitle>
          <CardDescription className="text-green-100">
            Test your vocabulary with a 10-question mixed quiz
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            variant="secondary"
            className="flex items-center space-x-2"
            onClick={() => navigate('/quizzes/quick')}
          >
            <Play className="h-4 w-4" />
            <span>Start Quick Quiz</span>
          </Button>
        </CardContent>
      </Card>

      {/* Quizzes Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {quizzes?.map((quiz) => (
          <QuizCard
            key={quiz.id}
            quiz={quiz}
            onDelete={handleDeleteQuiz}
            onStart={handleStartQuiz}
          />
        ))}
      </div>

      {quizzes?.length === 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-gray-500">
              <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No quizzes yet. Create your first quiz to get started!</p>
              <Button className="mt-4" onClick={handleCreateQuiz}>
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Quiz
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Select Document Modal */}
      <SelectDocumentModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  )
}
