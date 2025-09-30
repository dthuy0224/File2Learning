import { useState } from 'react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Brain, Play, Plus, Clock, Loader2, Trash2, Edit, BarChart3 } from 'lucide-react'
import QuizService from '../services/quizService'
import { useQuizzes, useQuizAttempts } from '../hooks/useQuizzes'
import toast from 'react-hot-toast'

export default function QuizzesPage() {
  const [creating, setCreating] = useState(false)

  // Use React Query hooks instead of local state and useEffect
  const { data: quizzes = [], isLoading: loading, error } = useQuizzes()

  const handleCreateQuiz = async () => {
    try {
      setCreating(true)
      // Example quiz creation - in real app this would come from a form
      await QuizService.createQuiz({
        title: 'New Vocabulary Quiz',
        description: 'A quiz about vocabulary words',
        quiz_type: 'vocabulary',
        difficulty_level: 'medium',
        questions: []
      })

      toast.success('Quiz created successfully')
      // React Query will automatically refetch the quizzes list
    } catch (error) {
      console.error('Error creating quiz:', error)
      toast.error('Failed to create quiz')
    } finally {
      setCreating(false)
    }
  }

  const handleStartQuiz = async (quizId: number) => {
    try {
      await QuizService.startQuizAttempt(quizId)
      toast.success('Quiz started!')
      // Navigate to quiz taking page (would need to implement this route)
      window.location.href = `/quizzes/${quizId}/take`
    } catch (error) {
      console.error('Error starting quiz:', error)
      toast.error('Failed to start quiz')
    }
  }

  const handleDeleteQuiz = async (quizId: number) => {
    if (!confirm('Are you sure you want to delete this quiz?')) return

    try {
      await QuizService.deleteQuiz(quizId)
      toast.success('Quiz deleted')
      // React Query will automatically refetch the quizzes list
    } catch (error) {
      console.error('Error deleting quiz:', error)
      toast.error('Failed to delete quiz')
    }
  }

  const getQuizStats = (quizId: number) => {
    // Use React Query for quiz attempts instead of local state
    const { data: quizAttempts = [] } = useQuizAttempts(quizId)
    return QuizService.getQuizStatsFromAttempts(quizAttempts)
  }

  if (loading) {
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
          disabled={creating}
          className="flex items-center space-x-2"
        >
          {creating ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Plus className="h-4 w-4" />
          )}
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
            onClick={() => window.location.href = '/quizzes/quick'}
          >
            <Play className="h-4 w-4" />
            <span>Start Quick Quiz</span>
          </Button>
        </CardContent>
      </Card>

      {/* Quizzes Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {quizzes.map((quiz) => {
          const stats = getQuizStats(quiz.id)
          return (
            <Card key={quiz.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Brain className="h-5 w-5 text-purple-600" />
                    <CardTitle className="text-lg truncate">{quiz.title}</CardTitle>
                  </div>
                  <div className="flex space-x-1">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => window.location.href = `/quizzes/${quiz.id}/edit`}
                    >
                      <Edit className="h-3 w-3" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDeleteQuiz(quiz.id)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <CardDescription>
                    {quiz.questions.length} questions • {quiz.difficulty_level} difficulty
                  </CardDescription>
                  <div className="flex items-center space-x-1 text-sm text-gray-600">
                    <Clock className="h-4 w-4" />
                    <span>{quiz.time_limit ? `${quiz.time_limit} min` : 'No time limit'}</span>
                  </div>
                  {quiz.description && (
                    <p className="text-sm text-gray-600 line-clamp-2">{quiz.description}</p>
                  )}

                  {stats.total_attempts > 0 && (
                    <div className="mt-3 p-2 bg-gray-50 rounded">
                      <div className="flex items-center space-x-1 text-xs text-gray-600 mb-1">
                        <BarChart3 className="h-3 w-3" />
                        <span>Stats</span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>Avg Score: {stats.average_score}%</div>
                        <div>Attempts: {stats.total_attempts}</div>
                        <div>High Score: {stats.highest_score}%</div>
                        <div>Completion: {stats.completion_rate}%</div>
                      </div>
                    </div>
                  )}
                </div>
                <div className="mt-4 flex space-x-2">
                  <Button size="sm" variant="outline">Preview</Button>
                  <Button
                    size="sm"
                    className="flex items-center space-x-1"
                    onClick={() => handleStartQuiz(quiz.id)}
                  >
                    <Play className="h-3 w-3" />
                    <span>Start</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {quizzes.length === 0 && (
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
    </div>
  )
}
