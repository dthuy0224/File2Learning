import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Brain, Play, Clock, Trash2, Edit, BarChart3, Loader2 } from 'lucide-react'
import { Quiz } from '@/services/quizService'
import { useQuizAttempts } from '@/hooks/useQuizzes'
import QuizService from '@/services/quizService'

interface QuizCardProps {
  quiz: Quiz
  onDelete: (quizId: number) => void
  onStart: (quizId: number) => void
}

export default function QuizCard({ quiz, onDelete, onStart }: QuizCardProps) {
  // Hook được gọi ở top-level của component con, hoàn toàn hợp lệ
  const { data: attempts, isLoading: attemptsLoading } = useQuizAttempts(quiz.id)

  const stats = QuizService.getQuizStatsFromAttempts(attempts || [])

  return (
    <Card className="hover:shadow-md transition-shadow">
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
              onClick={() => onDelete(quiz.id)}
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

          {attemptsLoading ? (
             <div className="flex items-center text-xs text-gray-500"><Loader2 className="h-3 w-3 mr-1 animate-spin" /> Loading stats...</div>
          ) : stats.total_attempts > 0 && (
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
                onClick={() => onStart(quiz.id)}
              >
                <Play className="h-3 w-3" />
                <span>Start</span>
              </Button>
        </div>
      </CardContent>
    </Card>
  )
}
