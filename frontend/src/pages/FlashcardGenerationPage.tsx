import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Loader2, ArrowLeft, FileText, BookOpen, RotateCcw, CheckCircle, AlertCircle } from 'lucide-react'
import { toast } from 'react-hot-toast'
import AIService, { Flashcard, FlashcardResponse } from '../services/aiService'

export default function FlashcardGenerationPage() {
  const { documentId } = useParams<{ documentId: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [document, setDocument] = useState<any>(null)
  const [flashcards, setFlashcards] = useState<Flashcard[]>([])
  const [currentCardIndex, setCurrentCardIndex] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)
  const [masteredCards, setMasteredCards] = useState<Set<number>>(new Set())

  // Flashcard generation settings
  const [numCards, setNumCards] = useState(10)

  useEffect(() => {
    if (documentId) {
      fetchDocumentDetails()
    }
  }, [documentId])

  const fetchDocumentDetails = async () => {
    try {
      setLoading(true)
      const documentData = await AIService.getDocumentContent(parseInt(documentId!))
      setDocument(documentData)
    } catch (error) {
      console.error('Error fetching document:', error)
      toast.error('Failed to load document details')
      navigate('/documents')
    } finally {
      setLoading(false)
    }
  }

  const generateFlashcards = async () => {
    try {
      setGenerating(true)
      const response: FlashcardResponse = await AIService.generateFlashcards(
        parseInt(documentId!),
        numCards
      )

      setFlashcards(response.flashcards)
      setCurrentCardIndex(0)
      setShowAnswer(false)
      setMasteredCards(new Set())
      toast.success(`Generated ${response.flashcards.length} flashcards!`)
    } catch (error: any) {
      console.error('Error generating flashcards:', error)
      toast.error(error.response?.data?.detail || 'Failed to generate flashcards')
    } finally {
      setGenerating(false)
    }
  }

  const nextCard = () => {
    if (currentCardIndex < flashcards.length - 1) {
      setCurrentCardIndex(currentCardIndex + 1)
      setShowAnswer(false)
    }
  }

  const prevCard = () => {
    if (currentCardIndex > 0) {
      setCurrentCardIndex(currentCardIndex - 1)
      setShowAnswer(false)
    }
  }

  const toggleAnswer = () => {
    setShowAnswer(!showAnswer)
  }

  const markAsMastered = () => {
    setMasteredCards(prev => new Set([...prev, currentCardIndex]))
    toast.success('Card marked as mastered!')
  }

  const resetProgress = () => {
    setCurrentCardIndex(0)
    setShowAnswer(false)
    setMasteredCards(new Set())
    toast.success('Progress reset!')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading document...</span>
      </div>
    )
  }

  if (!document) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Document not found</h3>
        <p className="text-gray-600">The document you're looking for doesn't exist or has been deleted.</p>
        <Button className="mt-4" onClick={() => navigate('/documents')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Documents
        </Button>
      </div>
    )
  }

  const currentCard = flashcards[currentCardIndex]
  const progress = flashcards.length > 0 ? ((currentCardIndex + 1) / flashcards.length) * 100 : 0
  const masteredCount = masteredCards.size

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" onClick={() => navigate('/documents')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Documents
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Generate Flashcards</h1>
            <p className="text-gray-600 mt-2">
              Create AI-powered flashcards from: {document.title || document.original_filename}
            </p>
          </div>
        </div>

        <Button variant="outline" onClick={resetProgress}>
          <RotateCcw className="h-4 w-4 mr-2" />
          Reset Progress
        </Button>
      </div>

      {/* Document Info */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-3">
            <FileText className="h-6 w-6 text-blue-600" />
            <div>
              <CardTitle>{document.title || document.original_filename}</CardTitle>
              <CardDescription>
                {document.word_count.toLocaleString()} words • {document.document_type.toUpperCase()}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Flashcard Generation Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BookOpen className="h-5 w-5" />
            <span>Flashcard Settings</span>
          </CardTitle>
          <CardDescription>
            Configure your AI-generated flashcard parameters
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Cards
            </label>
            <Select value={numCards.toString()} onValueChange={(value) => setNumCards(parseInt(value))}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select number of flashcards" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5 Cards</SelectItem>
                <SelectItem value="10">10 Cards</SelectItem>
                <SelectItem value="15">15 Cards</SelectItem>
                <SelectItem value="20">20 Cards</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button
            onClick={generateFlashcards}
            disabled={generating}
            className="w-full"
            size="lg"
          >
            {generating ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating Flashcards...
              </>
            ) : (
              <>
                <BookOpen className="h-4 w-4 mr-2" />
                Generate Flashcards
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Flashcard Study Interface */}
      {flashcards.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Study Flashcards</CardTitle>
                <CardDescription>
                  Card {currentCardIndex + 1} of {flashcards.length} • {masteredCount} mastered
                </CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <span className="text-sm text-gray-600">{Math.round(progress)}%</span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {currentCard && (
              <div className="text-center">
                {/* Flashcard */}
                <div
                  className="bg-white border-2 border-gray-200 rounded-lg p-8 mb-6 cursor-pointer transition-all duration-300 hover:shadow-lg"
                  onClick={toggleAnswer}
                >
                  <div className="min-h-[200px] flex items-center justify-center">
                    {showAnswer ? (
                      <div>
                        <p className="text-lg font-medium text-gray-900 mb-4">
                          {currentCard.back_text}
                        </p>
                        {currentCard.example_sentence && (
                          <p className="text-sm text-gray-600 italic">
                            "{currentCard.example_sentence}"
                          </p>
                        )}
                      </div>
                    ) : (
                      <p className="text-xl font-semibold text-gray-900">
                        {currentCard.front_text}
                      </p>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 mt-4">
                    Click to {showAnswer ? 'see question' : 'see answer'}
                  </p>
                </div>

                {/* Controls */}
                <div className="flex items-center justify-between">
                  <Button
                    variant="outline"
                    onClick={prevCard}
                    disabled={currentCardIndex === 0}
                  >
                    Previous
                  </Button>

                  <div className="flex items-center space-x-2">
                    <Button
                      variant={masteredCards.has(currentCardIndex) ? "default" : "outline"}
                      onClick={markAsMastered}
                      className="flex items-center space-x-2"
                    >
                      <CheckCircle className="h-4 w-4" />
                      <span>Mastered</span>
                    </Button>
                  </div>

                  <Button
                    variant="outline"
                    onClick={nextCard}
                    disabled={currentCardIndex === flashcards.length - 1}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
