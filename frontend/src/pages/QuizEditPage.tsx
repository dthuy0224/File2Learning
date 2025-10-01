import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Textarea } from '../components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { ArrowLeft, Save, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import QuizService, { Quiz } from '../services/quizService'

export default function QuizEditPage() {
  const { quizId } = useParams<{ quizId: string }>()
  const navigate = useNavigate()

  const [quiz, setQuiz] = useState<Quiz | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  // Form state
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [difficultyLevel, setDifficultyLevel] = useState('')

  useEffect(() => {
    if (quizId) {
      fetchQuiz()
    }
  }, [quizId])

  const fetchQuiz = async () => {
    if (!quizId) return

    try {
      setLoading(true)
      const quizData = await QuizService.getQuiz(parseInt(quizId))
      setQuiz(quizData)
      setTitle(quizData.title)
      setDescription(quizData.description || '')
      setDifficultyLevel(quizData.difficulty_level)
    } catch (error: any) {
      console.error('Error fetching quiz:', error)
      toast.error('Failed to load quiz')
      navigate('/quizzes')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!quiz || !title.trim()) {
      toast.error('Title is required')
      return
    }

    try {
      setSaving(true)
      await QuizService.updateQuiz(parseInt(quizId!), {
        title: title.trim(),
        description: description.trim() || undefined,
        difficulty_level: difficultyLevel
      })

      toast.success('Quiz updated successfully')
      navigate('/quizzes')
    } catch (error: any) {
      console.error('Error updating quiz:', error)
      toast.error('Failed to update quiz')
    } finally {
      setSaving(false)
    }
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
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Quiz not found</h3>
        <p className="text-gray-600">The quiz you're looking for doesn't exist.</p>
        <Button className="mt-4" onClick={() => navigate('/quizzes')}>
          Back to Quizzes
        </Button>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/quizzes')}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Quizzes
        </Button>
      </div>

      {/* Edit Form */}
      <Card>
        <CardHeader>
          <CardTitle>Edit Quiz</CardTitle>
          <CardDescription>
            Update the basic information for your quiz
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Title */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Quiz Title</label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter quiz title"
              maxLength={100}
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Description (Optional)</label>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter quiz description"
              maxLength={500}
              rows={3}
            />
          </div>

          {/* Difficulty Level */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Difficulty Level</label>
            <Select value={difficultyLevel} onValueChange={setDifficultyLevel}>
              <SelectTrigger>
                <SelectValue placeholder="Select difficulty" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="easy">Easy</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="hard">Hard</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Quiz Info (Read-only) */}
          <div className="pt-4 border-t">
            <div className="text-sm text-gray-600 space-y-1">
              <div>Questions: {quiz.questions.length}</div>
              <div>Type: {quiz.quiz_type}</div>
              <div>Created: {new Date(quiz.created_at).toLocaleDateString()}</div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-2 pt-4">
            <Button
              variant="outline"
              onClick={() => navigate('/quizzes')}
              disabled={saving}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              disabled={saving || !title.trim()}
            >
              {saving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Note about future features */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-4">
          <p className="text-sm text-blue-800">
            <strong>Note:</strong> This page currently allows editing basic quiz information.
            Editing individual questions will be available in a future update.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
