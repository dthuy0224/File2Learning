import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Progress } from '../components/ui/progress'
import { Badge } from '../components/ui/badge'
import { Loader2, Clock, CheckCircle, AlertCircle, ArrowLeft, Send } from 'lucide-react'
import { toast } from 'react-hot-toast'
import quizService from '../services/quizService'
import { invalidateProgressQueries } from '@/utils/progressInvalidation'

interface QuizQuestion {
  id: number
  question_text: string
  question_type: string
  options?: string[]
  correct_answer: string
  explanation?: string
  points: number
  order_index: number
}

interface QuizAttempt {
  id: number
  quiz_id: number
  user_id: number
  answers: Record<string, any>
  score: number
  max_score: number
  percentage: number
  time_taken?: number
  is_completed: boolean
  started_at: string
  completed_at?: string
}

export default function QuizTakingPage() {
  const { quizId } = useParams<{ quizId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Quiz data
  const [quiz, setQuiz] = useState<any>(null)
  const [questions, setQuestions] = useState<QuizQuestion[]>([])
  const [attempt, setAttempt] = useState<QuizAttempt | null>(null)

  // UI state
  const [loading, setLoading] = useState(true)
  const [starting, setStarting] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)

  // Timer state
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null)
  const [totalTimeElapsed, setTotalTimeElapsed] = useState(0)

  // Answers state
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({})

  useEffect(() => {
    if (quizId) {
      fetchQuizDetails()
    }
  }, [quizId])

  // Timer effect for countdown (if time limit exists)
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null

    if (timeRemaining !== null && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev !== null && prev > 1) {
            return prev - 1
          } else {
            // Time's up - auto submit
            if (prev === 1) {
              handleSubmitQuiz()
            }
            return 0
          }
        })
      }, 1000)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [timeRemaining])

  // Separate timer for tracking total elapsed time
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null

    // Start tracking time when quiz has started (has attempt)
    if (attempt && !submitting) {
      interval = setInterval(() => {
        setTotalTimeElapsed(prev => prev + 1)
      }, 1000)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [attempt, submitting])

  const fetchQuizDetails = async () => {
    try {
      setLoading(true)
      const quizData = await quizService.getQuiz(parseInt(quizId!))
      setQuiz(quizData)
      setQuestions(quizData.questions || [])

      // Set timer if quiz has time limit
      if (quizData.time_limit && quizData.time_limit > 0) {
        setTimeRemaining(quizData.time_limit * 60) // Convert minutes to seconds
      }
    } catch (error: any) {
      console.error('Error fetching quiz:', error)
      toast.error('Failed to load quiz details')
      navigate('/quizzes')
    } finally {
      setLoading(false)
    }
  }

  const handleStartQuiz = async () => {
    try {
      setStarting(true)
      const attemptData = await quizService.startQuizAttempt(parseInt(quizId!))
      setAttempt(attemptData)
      toast.success('Quiz started! Good luck!')
    } catch (error: any) {
      console.error('Error starting quiz:', error)
      toast.error('Failed to start quiz')
    } finally {
      setStarting(false)
    }
  }

  const handleAnswerSelect = (questionId: number, answer: string) => {
    setUserAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }))
  }

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1)
    }
  }

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1)
    }
  }

  const handleSubmitQuiz = async () => {
    if (!attempt || Object.keys(userAnswers).length === 0) {
      toast.error('Please answer at least one question before submitting')
      return
    }

    try {
      setSubmitting(true)
      const result = await quizService.submitQuizAttempt(parseInt(quizId!), {
        quiz_id: parseInt(quizId!),
        answers: userAnswers,
        total_time: totalTimeElapsed
      })

      // Invalidate all progress and stats queries to trigger refresh
      invalidateProgressQueries(queryClient, { includeTodayPlan: true })

      // Navigate to results page
      navigate(`/attempts/${result.id}/results`)
    } catch (error: any) {
      console.error('Error submitting quiz:', error)
      toast.error('Failed to submit quiz')
    } finally {
      setSubmitting(false)
    }
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading quiz...</span>
      </div>
    )
  }

  if (!quiz) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Quiz not found</h3>
        <p className="text-gray-600">The quiz you're looking for doesn't exist or has been deleted.</p>
        <Button className="mt-4" onClick={() => navigate('/quizzes')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Quizzes
        </Button>
      </div>
    )
  }

  // Show start screen if quiz hasn't started yet
  if (!attempt) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex items-center space-x-4">
          <Button variant="outline" onClick={() => navigate('/quizzes')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Quizzes
          </Button>
        </div>

        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">{quiz.title}</CardTitle>
            <CardDescription className="text-lg">
              {quiz.description}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{questions.length}</div>
                <div className="text-sm text-blue-600">Questions</div>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {quiz.difficulty_level || 'Medium'}
                </div>
                <div className="text-sm text-green-600">Difficulty</div>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {quiz.quiz_type?.replace('_', ' ').toUpperCase() || 'Mixed'}
                </div>
                <div className="text-sm text-purple-600">Type</div>
              </div>
              <div className="p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {quiz.time_limit ? `${quiz.time_limit}m` : 'No limit'}
                </div>
                <div className="text-sm text-orange-600">Time Limit</div>
              </div>
            </div>

            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-5 w-5 text-yellow-400" />
                </div>
                <div className="ml-3">
                  <p className="text-sm text-yellow-700">
                    <strong>Instructions:</strong> Read each question carefully and select the best answer.
                    {quiz.time_limit && ` You have ${quiz.time_limit} minutes to complete this quiz.`}
                  </p>
                </div>
              </div>
            </div>

            <Button
              onClick={handleStartQuiz}
              disabled={starting}
              className="w-full"
              size="lg"
            >
              {starting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Starting Quiz...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Start Quiz
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Show quiz taking interface
  const currentQuestion = questions[currentQuestionIndex]
  const progressPercentage = ((currentQuestionIndex + 1) / questions.length) * 100

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" onClick={() => navigate('/quizzes')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Quizzes
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{quiz.title}</h1>
            <p className="text-gray-600">Question {currentQuestionIndex + 1} of {questions.length}</p>
          </div>
        </div>

        {timeRemaining !== null && (
          <div className="flex items-center space-x-2 text-lg font-mono">
            <Clock className="h-5 w-5" />
            <span className={timeRemaining < 60 ? 'text-red-600 font-bold' : 'text-gray-700'}>
              {formatTime(timeRemaining)}
            </span>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-gray-600">
          <span>Progress</span>
          <span>{Math.round(progressPercentage)}%</span>
        </div>
        <Progress value={progressPercentage} className="h-2" />
      </div>

      {/* Question Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <Badge variant="secondary">
              Question {currentQuestionIndex + 1}
            </Badge>
            <Badge variant="outline">
              {currentQuestion.points} points
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-lg font-medium text-gray-900">
            {currentQuestion.question_text}
          </div>

          {/* Answer Options */}
          {currentQuestion.question_type === 'multiple_choice' && currentQuestion.options ? (
            <div className="space-y-3">
              {currentQuestion.options.map((option, optionIndex) => (
                <label
                  key={optionIndex}
                  className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50"
                >
                  <input
                    type="radio"
                    name={`question-${currentQuestion.id}`}
                    value={option}
                    checked={userAnswers[currentQuestion.id] === option}
                    onChange={(e) => handleAnswerSelect(currentQuestion.id, e.target.value)}
                    className="text-blue-600"
                  />
                  <span className="flex-1">{option}</span>
                </label>
              ))}
            </div>
          ) : (
            <div>
              <textarea
                value={userAnswers[currentQuestion.id] || ''}
                onChange={(e) => handleAnswerSelect(currentQuestion.id, e.target.value)}
                placeholder="Type your answer here..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                rows={4}
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <Button
          variant="outline"
          onClick={handlePreviousQuestion}
          disabled={currentQuestionIndex === 0}
        >
          Previous
        </Button>

        <div className="flex space-x-2">
          {questions.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentQuestionIndex(index)}
              className={`w-8 h-8 rounded-full text-sm font-medium ${
                index === currentQuestionIndex
                  ? 'bg-blue-600 text-white'
                  : userAnswers[questions[index].id]
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              {index + 1}
            </button>
          ))}
        </div>

        {currentQuestionIndex === questions.length - 1 ? (
          <Button onClick={handleSubmitQuiz} disabled={submitting}>
            {submitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <Send className="h-4 w-4 mr-2" />
                Submit Quiz
              </>
            )}
          </Button>
        ) : (
          <Button onClick={handleNextQuestion}>
            Next
          </Button>
        )}
      </div>
    </div>
  )
}
