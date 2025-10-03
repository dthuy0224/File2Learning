import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Layers, RotateCcw, Play, ArrowLeft, BookOpen, Clock, Target } from 'lucide-react'
import FlashcardService, { Flashcard, FlashcardSet } from '../services/flashcardService'
import PracticeModal from '../components/PracticeModal'
import FlashcardViewModal from '../components/FlashcardViewModal'

export default function FlashcardSetDetailPage() {
  const { setId } = useParams<{ setId: string }>()
  const navigate = useNavigate()

  const [practicingCard, setPracticingCard] = useState<Flashcard | null>(null)
  const [viewingCard, setViewingCard] = useState<Flashcard | null>(null)

  // Fetch flashcard set info (we'll need to add this to the service)
  const { data: setInfo } = useQuery({
    queryKey: ['flashcardSetInfo', setId],
    queryFn: async () => {
      // For now, we'll fetch all sets and find the current one
      const sets = await FlashcardService.getFlashcardSets()
      return sets.find(set => set.id === parseInt(setId!))
    },
    enabled: !!setId
  })

  // Fetch all flashcards in this set
  const { data: cards, isLoading } = useQuery({
    queryKey: ['flashcardSet', setId],
    queryFn: () => FlashcardService.getFlashcardsInSet(parseInt(setId!)),
    enabled: !!setId
  })

  // Calculate stats for this set
  const stats = cards ? FlashcardService.getFlashcardStatsFromList(cards) : {
    total_cards: 0,
    due_today: 0,
    due_this_week: 0,
    mastered: 0,
    learning: 0,
    new: 0
  }

  const handleStartReview = () => {
    // Navigate to review session with this specific set
    navigate(`/flashcards/review?set=${setId}`)
  }

  const handlePractice = (card: Flashcard) => {
    setPracticingCard(card)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading flashcards...</span>
      </div>
    )
  }

  if (!setInfo || !cards) {
    return (
      <div className="text-center py-12">
        <Layers className="h-12 w-12 mx-auto mb-4 text-gray-400" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Flashcard set not found</h3>
        <p className="text-gray-600">The flashcard set you're looking for doesn't exist.</p>
        <Button className="mt-4" onClick={() => navigate('/flashcards')}>
          Back to Flashcard Sets
        </Button>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/flashcards')}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Sets
        </Button>
      </div>

      {/* Set Info */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Layers className="h-6 w-6 text-indigo-600" />
              </div>
              <div className="flex-1">
                <CardTitle className="text-xl">
                  {setInfo.title || setInfo.original_filename}
                </CardTitle>
                <CardDescription className="mt-1">
                  {setInfo.card_count} flashcards • Created {new Date(setInfo.created_at).toLocaleDateString()}
                </CardDescription>
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {/* Action Buttons */}
          <div className="flex space-x-3 mb-6">
            <Button
              onClick={handleStartReview}
              className="flex items-center space-x-2"
            >
              <Target className="h-4 w-4" />
              <span>Start Review Session</span>
            </Button>
            <Button
              variant="outline"
              onClick={() => handlePractice(cards[0])}
              className="flex items-center space-x-2"
            >
              <Play className="h-4 w-4" />
              <span>Practice (First Card)</span>
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{stats.total_cards}</div>
              <div className="text-sm text-blue-800">Total Cards</div>
            </div>
            <div className="text-center p-3 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{stats.due_today}</div>
              <div className="text-sm text-red-800">Due Today</div>
            </div>
            <div className="text-center p-3 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">{stats.learning}</div>
              <div className="text-sm text-yellow-800">Learning</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{stats.mastered}</div>
              <div className="text-sm text-green-800">Mastered</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Flashcards Grid */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Flashcards in this Set</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cards.map((card) => (
            <Card key={card.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-xs">
                    {card.difficulty_level}
                  </Badge>
                  <div className="flex space-x-1">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setViewingCard(card)}
                    >
                      <BookOpen className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-2">
                  <div className="font-medium text-sm text-gray-900 line-clamp-2">
                    {card.front_text}
                  </div>
                  <div className="text-sm text-gray-600 line-clamp-3">
                    {card.back_text}
                  </div>

                  {card.next_review_date && (
                    <div className="flex items-center space-x-1 text-xs text-gray-500">
                      <Clock className="h-3 w-3" />
                      <span>Next: {new Date(card.next_review_date).toLocaleDateString()}</span>
                    </div>
                  )}

                  <div className="flex space-x-2 pt-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setViewingCard(card)}
                    >
                      View
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handlePractice(card)}
                    >
                      Practice
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {cards.length === 0 && (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center text-gray-500">
                <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No flashcards in this set yet.</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Practice Modal */}
      <PracticeModal
        card={practicingCard}
        allCards={cards}
        onClose={() => setPracticingCard(null)}
      />

      {/* Flashcard View Modal */}
      <FlashcardViewModal
        card={viewingCard}
        onClose={() => setViewingCard(null)}
      />
    </div>
  )
}
