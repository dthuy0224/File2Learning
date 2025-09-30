import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { CreditCard, Plus, RotateCcw, Loader2, Trash2, Edit } from 'lucide-react'
import FlashcardService from '../services/flashcardService'
import { useFlashcards } from '../hooks/useFlashcards'
import toast from 'react-hot-toast'

export default function FlashcardsPage() {
  const navigate = useNavigate()
  const [creating, setCreating] = useState(false)

  // Use React Query hooks instead of local state and useEffect
  const { data: flashcards = [], isLoading: loading, error } = useFlashcards()

  // Calculate stats from flashcards using React Query data
  const stats = flashcards.length > 0 ? FlashcardService.getFlashcardStatsFromList(flashcards) : {
    total_cards: 0,
    due_today: 0,
    due_this_week: 0,
    mastered: 0,
    learning: 0,
    new: 0
  }

  const handleCreateFlashcard = async () => {
    try {
      setCreating(true)
      // Example flashcard creation - in real app this would come from a form
      await FlashcardService.createFlashcard({
        front_text: 'Example Word',
        back_text: 'Definition of example word',
        difficulty_level: 'medium'
      })

      toast.success('Flashcard created successfully')
      // React Query will automatically refetch the flashcards list
    } catch (error) {
      console.error('Error creating flashcard:', error)
      toast.error('Failed to create flashcard')
    } finally {
      setCreating(false)
    }
  }

  const handleReviewFlashcard = async (flashcardId: number) => {
    try {
      // Example review - in real app this would come from user interaction
      await FlashcardService.reviewFlashcard(flashcardId, {
        quality: 4, // 0-5 rating
        response_time: 2500 // 2.5 seconds
      })

      toast.success('Flashcard reviewed')
      // React Query will automatically refetch the flashcards and due cards
    } catch (error) {
      console.error('Error reviewing flashcard:', error)
      toast.error('Failed to review flashcard')
    }
  }

  const handleDeleteFlashcard = async (flashcardId: number) => {
    if (!confirm('Are you sure you want to delete this flashcard?')) return

    try {
      await FlashcardService.deleteFlashcard(flashcardId)
      toast.success('Flashcard deleted')
      // React Query will automatically refetch the flashcards list
    } catch (error) {
      console.error('Error deleting flashcard:', error)
      toast.error('Failed to delete flashcard')
    }
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
          <p className="text-red-600 mb-4">Error loading flashcards</p>
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
          <h1 className="text-3xl font-bold text-gray-900">Flashcards</h1>
          <p className="text-gray-600 mt-2">Review and practice your vocabulary</p>
        </div>
        <Button
          onClick={handleCreateFlashcard}
          disabled={creating}
          className="flex items-center space-x-2"
        >
          {creating ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Plus className="h-4 w-4" />
          )}
          <span>Create Flashcard</span>
        </Button>
      </div>

      {/* Study Session Card */}
      <Card className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
        <CardHeader>
          <CardTitle className="text-white">Ready for Review</CardTitle>
          <CardDescription className="text-blue-100">
            You have {stats.due_today} flashcards due for review
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            variant="secondary"
            className="flex items-center space-x-2"
            onClick={() => navigate('/flashcards/review')}
          >
            <RotateCcw className="h-4 w-4" />
            <span>Start Review Session</span>
          </Button>
        </CardContent>
      </Card>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Total Cards</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_cards}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Due Today</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.due_today}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Learning</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.learning}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Mastered</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.mastered}</div>
          </CardContent>
        </Card>
      </div>

      {/* Flashcards Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {flashcards.slice(0, 6).map((card) => (
          <Card key={card.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CreditCard className="h-5 w-5 text-blue-600" />
                  <CardTitle className="text-lg truncate">{card.front_text}</CardTitle>
                </div>
                <div className="flex space-x-1">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleReviewFlashcard(card.id)}
                  >
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleDeleteFlashcard(card.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <CardDescription className="line-clamp-2">
                {card.back_text}
              </CardDescription>
              <div className="mt-2 flex items-center justify-between text-sm text-gray-600">
                <span>Difficulty: {card.difficulty_level}</span>
                <span>Reps: {card.repetitions}</span>
              </div>
              {card.next_review_date && (
                <div className="mt-2 text-xs text-gray-500">
                  Next review: {new Date(card.next_review_date).toLocaleDateString()}
                </div>
              )}
              <div className="mt-4 flex space-x-2">
                <Button size="sm" variant="outline" onClick={() => handleReviewFlashcard(card.id)}>
                  Review
                </Button>
                <Button size="sm">Practice</Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {flashcards.length === 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-gray-500">
              <CreditCard className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No flashcards yet. Create your first flashcard to get started!</p>
              <Button className="mt-4" onClick={handleCreateFlashcard}>
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Flashcard
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
