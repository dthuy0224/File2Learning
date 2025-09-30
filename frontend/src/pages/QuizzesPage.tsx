import { useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Brain, Plus, Loader2, Play } from 'lucide-react'
import QuizService from '../services/quizService'
import { useQuizzes } from '../hooks/useQuizzes'
import QuizCard from '../components/QuizCard'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'

export default function QuizzesPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { data: quizzes, isLoading: quizzesLoading, error } = useQuizzes()

  const createQuizMutation = useMutation({
    mutationFn: () => QuizService.createQuiz({
      title: 'New Vocabulary Quiz',
      description: 'A quiz about vocabulary words',
      quiz_type: 'vocabulary',
      difficulty_level: 'medium',
      questions: []
    }),
    onSuccess: () => {
      toast.success('Quiz created successfully')
      // Refresh the quizzes list after successful creation
      queryClient.invalidateQueries({ queryKey: ['quizzes'] })
    },
    onError: () => {
      toast.error('Failed to create quiz')
    }
  })

  const deleteQuizMutation = useMutation({
    mutationFn: (quizId: number) => QuizService.deleteQuiz(quizId),
    onSuccess: () => {
      toast.success('Quiz deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['quizzes'] })
    },
    onError: () => {
      toast.error('Failed to delete quiz')
    }
  })

  const handleStartQuiz = async (quizId: number) => {
    try {
      await QuizService.startQuizAttempt(quizId)
      toast.success('Quiz started!')
      navigate(`/quizzes/${quizId}/take`)
    } catch (error) {
      toast.error('Failed to start quiz')
    }
  }

  const handleDeleteQuiz = (quizId: number) => {
    if (!confirm('Are you sure you want to delete this quiz?')) return
    deleteQuizMutation.mutate(quizId)
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
          onClick={() => createQuizMutation.mutate()}
          disabled={createQuizMutation.isPending}
          className="flex items-center space-x-2"
        >
          {createQuizMutation.isPending ? (
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
              <Button className="mt-4" onClick={() => createQuizMutation.mutate()}>
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
