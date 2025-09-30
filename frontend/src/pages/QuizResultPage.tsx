import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Progress } from '../components/ui/progress'
import {
  CheckCircle,
  XCircle,
  Clock,
  Trophy,
  RotateCcw,
  ArrowLeft,
  BookOpen,
  Target
} from 'lucide-react'
import { toast } from 'react-hot-toast'
import quizService from '../services/quizService'

interface QuizAttemptDetail {
  id: number
  quiz_id: number
  user_id: number
  answers: Record<number, {
    question_text: string
    user_answer: string
    correct_answer: string
    is_correct: boolean
    explanation?: string
    points: number
  }>
  score: number
  max_score: number
  percentage: number
  time_taken?: number
  is_completed: boolean
  started_at: string
  completed_at?: string
  quiz?: {
    title: string
    description?: string
    quiz_type: string
    difficulty_level: string
  }
}

export default function QuizResultPage() {
  const { attemptId } = useParams<{ attemptId: string }>()
  const navigate = useNavigate()

  const [attempt, setAttempt] = useState<QuizAttemptDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (attemptId) {
      fetchAttemptDetails()
    }
  }, [attemptId])

  const fetchAttemptDetails = async () => {
    try {
      setLoading(true)
      // For now, we'll need to add a method to get attempt by ID
      // This might need to be added to the quiz service
      const attemptData = await quizService.getQuizAttempt(parseInt(attemptId!))
      setAttempt(attemptData)
    } catch (error: any) {
      console.error('Error fetching attempt:', error)
      toast.error('Failed to load quiz results')
      navigate('/quizzes')
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (seconds?: number) => {
    if (!seconds) return 'N/A'
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getScoreColor = (percentage: number) => {
    if (percentage >= 90) return 'text-green-600'
    if (percentage >= 80) return 'text-blue-600'
    if (percentage >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBgColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-green-50 border-green-200'
    if (percentage >= 80) return 'bg-blue-50 border-blue-200'
    if (percentage >= 70) return 'bg-yellow-50 border-yellow-200'
    return 'bg-red-50 border-red-200'
  }

  const getPerformanceMessage = (percentage: number) => {
    if (percentage >= 90) return 'Excellent! Outstanding performance!'
    if (percentage >= 80) return 'Great job! You have a solid understanding.'
    if (percentage >= 70) return 'Good work! You\'re on the right track.'
    if (percentage >= 60) return 'Not bad! Keep practicing to improve.'
    return 'Keep studying and try again. You can do better!'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading results...</span>
      </div>
    )
  }

  if (!attempt) {
    return (
      <div className="text-center py-12">
        <XCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Results not found</h3>
        <p className="text-gray-600">The quiz results you're looking for don't exist.</p>
        <Button className="mt-4" onClick={() => navigate('/quizzes')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Quizzes
        </Button>
      </div>
    )
  }

  const totalQuestions = Object.keys(attempt.answers).length
  const correctAnswers = Object.values(attempt.answers).filter(answer => answer.is_correct).length

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button variant="outline" onClick={() => navigate('/quizzes')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Quizzes
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Quiz Results</h1>
          <p className="text-gray-600 mt-1">
            Completed on {formatDate(attempt.completed_at || attempt.started_at)}
          </p>
        </div>
      </div>

      {/* Score Overview */}
      <Card className={`${getScoreBgColor(attempt.percentage)} border-2`}>
        <CardHeader className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-2">
            <Trophy className={`h-8 w-8 ${getScoreColor(attempt.percentage)}`} />
            <CardTitle className="text-2xl">Your Score</CardTitle>
          </div>
          <div className={`text-6xl font-bold ${getScoreColor(attempt.percentage)}`}>
            {attempt.percentage}%
          </div>
          <CardDescription className="text-lg">
            {correctAnswers} out of {totalQuestions} questions correct
          </CardDescription>
        </CardHeader>
        <CardContent className="text-center space-y-4">
          <Progress value={attempt.percentage} className="h-3" />
          <p className={`text-lg font-medium ${getScoreColor(attempt.percentage)}`}>
            {getPerformanceMessage(attempt.percentage)}
          </p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{correctAnswers}</div>
              <div className="text-sm text-gray-600">Correct</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{totalQuestions - correctAnswers}</div>
              <div className="text-sm text-gray-600">Incorrect</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{formatTime(attempt.time_taken)}</div>
              <div className="text-sm text-gray-600">Time Taken</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${getScoreColor(attempt.percentage)}`}>
                {attempt.score}/{attempt.max_score}
              </div>
              <div className="text-sm text-gray-600">Points</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quiz Info */}
      {attempt.quiz && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BookOpen className="h-5 w-5" />
              <span>Quiz Details</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <div className="text-sm font-medium text-gray-500">Quiz Title</div>
                <div className="font-medium">{attempt.quiz.title}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-500">Type</div>
                <Badge variant="secondary">
                  {attempt.quiz.quiz_type.replace('_', ' ').toUpperCase()}
                </Badge>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-500">Difficulty</div>
                <Badge variant={attempt.quiz.difficulty_level === 'easy' ? 'secondary' : attempt.quiz.difficulty_level === 'medium' ? 'default' : 'destructive'}>
                  {attempt.quiz.difficulty_level}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Question Review */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Target className="h-5 w-5" />
            <span>Question Review</span>
          </CardTitle>
          <CardDescription>
            Review each question and see the correct answers
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {Object.entries(attempt.answers).map(([questionId, answer], index) => (
            <div
              key={questionId}
              className={`p-6 rounded-lg border-2 ${
                answer.is_correct
                  ? 'bg-green-50 border-green-200'
                  : 'bg-red-50 border-red-200'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <h4 className="font-medium text-gray-900">
                  Question {index + 1}
                </h4>
                <div className="flex items-center space-x-2">
                  {answer.is_correct ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                  <Badge variant={answer.is_correct ? 'default' : 'destructive'}>
                    {answer.is_correct ? 'Correct' : 'Incorrect'}
                  </Badge>
                </div>
              </div>

              <p className="text-gray-800 mb-4">{answer.question_text}</p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-500 mb-1">Your Answer</div>
                  <div className={`p-3 rounded-lg ${
                    answer.is_correct ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {answer.user_answer || 'No answer provided'}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500 mb-1">Correct Answer</div>
                  <div className="p-3 rounded-lg bg-green-100 text-green-800">
                    {answer.correct_answer}
                  </div>
                </div>
              </div>

              {answer.explanation && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="text-sm font-medium text-gray-500 mb-1">Explanation</div>
                  <p className="text-gray-700">{answer.explanation}</p>
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex justify-center space-x-4">
        <Button
          variant="outline"
          onClick={() => navigate(`/quizzes/${attempt.quiz_id}/take`)}
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          Retake Quiz
        </Button>
        <Button onClick={() => navigate('/quizzes')}>
          Back to Quizzes
        </Button>
      </div>
    </div>
  )
}
