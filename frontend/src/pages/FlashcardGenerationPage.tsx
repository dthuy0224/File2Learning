import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Loader2, ArrowLeft, FileText, BookOpen, AlertCircle, Save } from 'lucide-react'
import { toast } from 'react-hot-toast'
import AIService, { Flashcard, FlashcardResponse } from '../services/aiService'
import FlashcardService from '../services/flashcardService'

export default function FlashcardGenerationPage() {
  const { documentId } = useParams<{ documentId: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [document, setDocument] = useState<any>(null)
  const [flashcards, setFlashcards] = useState<Flashcard[]>([])
  const [selectedCards, setSelectedCards] = useState<Set<number>>(new Set())
  const [isSaving, setIsSaving] = useState(false)

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
      setSelectedCards(new Set()) // Reset selection when generating new cards
      toast.success(`Generated ${response.flashcards.length} flashcards!`)
    } catch (error: any) {
      console.error('Error generating flashcards:', error)
      toast.error(error.response?.data?.detail || 'Failed to generate flashcards')
    } finally {
      setGenerating(false)
    }
  }

  const handleSelectCard = (index: number) => {
    setSelectedCards(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const handleSaveSelectedCards = async () => {
    setIsSaving(true);
    const cardsToSave = Array.from(selectedCards).map(index => flashcards[index]);

    try {
      // Gọi API để lưu từng thẻ
      await FlashcardService.createMultipleFlashcards(cardsToSave.map(card => ({
          ...card,
          document_id: parseInt(documentId!)
      })));
      toast.success(`${cardsToSave.length} flashcards saved successfully!`);
      navigate('/flashcards'); // Điều hướng về trang danh sách flashcard
    } catch (error) {
      toast.error('Failed to save flashcards.');
    } finally {
      setIsSaving(false);
    }
  };


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

      {/* AI Generated Flashcards Review and Save */}
      {flashcards.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>AI Generated Flashcards</CardTitle>
            <CardDescription>
              Review and select the flashcards you want to save to your collection.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {flashcards.map((card, index) => (
              <div key={index} className="flex items-start space-x-4 p-4 border rounded-md">
                <input
                  type="checkbox"
                  className="mt-1"
                  checked={selectedCards.has(index)}
                  onChange={() => handleSelectCard(index)}
                />
                <div className="flex-1">
                  <p className="font-semibold">{card.front_text}</p>
                  <p className="text-gray-600">{card.back_text}</p>
                  {card.example_sentence && (
                    <p className="text-sm italic text-gray-500 mt-1">
                      "{card.example_sentence}"
                    </p>
                  )}
                </div>
              </div>
            ))}

            <div className="flex items-center justify-between pt-4 border-t">
              <span className="text-sm text-gray-600">
                {selectedCards.size} of {flashcards.length} cards selected
              </span>
              <Button
                onClick={handleSaveSelectedCards}
                disabled={isSaving || selectedCards.size === 0}
                className="flex items-center space-x-2"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    <span>Save {selectedCards.size} Cards</span>
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
