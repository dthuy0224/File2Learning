import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { CreditCard, Plus, RotateCcw, Loader2, Trash2, Edit, Layers } from 'lucide-react'
import FlashcardService, { Flashcard, FlashcardSet } from '../services/flashcardService'
import AddFlashcardModal from '../components/AddFlashcardModal'
import PracticeModal from '../components/PracticeModal'
import FlashcardViewModal from '../components/FlashcardViewModal'
import DeleteConfirmationModal from '../components/DeleteConfirmationModal'
import toast from 'react-hot-toast'

export default function FlashcardsPage() {
  const navigate = useNavigate()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [practicingCard, setPracticingCard] = useState<Flashcard | null>(null)
  const [viewingCard, setViewingCard] = useState<Flashcard | null>(null)
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean
    cardId: number | null
    cardName: string | null
    isLoading: boolean
  }>({
    isOpen: false,
    cardId: null,
    cardName: null,
    isLoading: false
  })

  // Use React Query hooks for flashcard sets
  const { data: sets, isLoading: loading, error } = useQuery({
    queryKey: ['flashcardSets'],
    queryFn: () => FlashcardService.getFlashcardSets()
  })

  // Calculate total stats across all sets
  const totalCards = sets?.reduce((sum, set) => sum + set.card_count, 0) || 0
  const stats = {
    total_cards: totalCards,
    due_today: 0, // Will be calculated when needed
    due_this_week: 0,
    mastered: 0,
    learning: 0,
    new: 0
  }

  // Handle opening the create flashcard modal
  const handleCreateFlashcard = () => {
    setIsModalOpen(true)
  }

  const handleDeleteFlashcard = (flashcardId: number, cardName: string) => {
    setDeleteModal({
      isOpen: true,
      cardId: flashcardId,
      cardName: cardName,
      isLoading: false
    })
  }

  const confirmDeleteFlashcard = async () => {
    if (!deleteModal.cardId) return

    setDeleteModal(prev => ({ ...prev, isLoading: true }))

    try {
      await FlashcardService.deleteFlashcard(deleteModal.cardId)
      toast.success('Flashcard deleted')
      // React Query will automatically refetch the flashcards list
    } catch (error) {
      console.error('Error deleting flashcard:', error)
      toast.error('Failed to delete flashcard')
    } finally {
      setDeleteModal({
        isOpen: false,
        cardId: null,
        cardName: null,
        isLoading: false
      })
    }
  }

  // Component for displaying flashcard sets
  const FlashcardSetCard = ({ set }: { set: FlashcardSet }) => {
    const navigate = useNavigate()
    return (
      <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate(`/flashcard-sets/${set.id}`)}>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Layers className="text-indigo-500" />
            <span className="truncate">{set.title || set.original_filename}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600">{set.card_count} cards</p>
          <p className="text-xs text-gray-500 mt-1">
            Created on: {new Date(set.created_at).toLocaleDateString()}
          </p>
        </CardContent>
      </Card>
    )
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
          className="flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Create Flashcard</span>
        </Button>
      </div>

      {/* Study Session Card */}
      <Card className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
        <CardHeader>
          <CardTitle className="text-white">Ready for Review</CardTitle>
          <CardDescription className="text-blue-100">
            You have {stats.total_cards} flashcards across {sets?.length || 0} sets
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

      {/* Flashcard Sets Grid */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Your Flashcard Sets</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {loading ? (
            <p>Loading sets...</p>
          ) : sets?.length ? (
            sets.map((set) => (
              <FlashcardSetCard key={set.id} set={set} />
            ))
          ) : (
            <Card className="col-span-full">
              <CardContent className="pt-6">
                <div className="text-center text-gray-500">
                  <Layers className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>You haven't created any flashcard sets from documents yet.</p>
                  <p className="text-sm mt-2">Upload a document and generate flashcards to get started!</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Practice Modal - Temporarily disabled until we implement set-based practice */}
      {/* <PracticeModal
        card={practicingCard}
        allCards={flashcards}
        onClose={() => setPracticingCard(null)}
      /> */}

      {/* Add Flashcard Modal */}
      <AddFlashcardModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />

      {/* Flashcard View Modal - Temporarily disabled until we implement set-based view */}
      {/* <FlashcardViewModal
        card={viewingCard}
        onClose={() => setViewingCard(null)}
      /> */}

      {/* Delete Confirmation Modal */}
      <DeleteConfirmationModal
        isOpen={deleteModal.isOpen}
        onClose={() => setDeleteModal(prev => ({ ...prev, isOpen: false }))}
        onConfirm={confirmDeleteFlashcard}
        title="Delete Flashcard"
        description="Are you sure you want to delete this flashcard"
        itemName={deleteModal.cardName || undefined}
        isLoading={deleteModal.isLoading}
      />
    </div>
  )
}
