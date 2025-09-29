import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { ArrowLeft, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { toast } from 'react-hot-toast'
import AIService, { Document } from '../services/aiService'

export default function DocumentDetailPage() {
  const { documentId } = useParams<{ documentId: string }>()
  const navigate = useNavigate()
  const [document, setDocument] = useState<Document | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (documentId) {
      fetchDocument()
    }
  }, [documentId])

  const fetchDocument = async () => {
    if (!documentId) return

    try {
      setLoading(true)
      setError(null)
      const docId = parseInt(documentId)
      const data = await AIService.getDocument(docId)
      setDocument(data)
    } catch (error: any) {
      console.error('Error fetching document:', error)
      setError(error.response?.data?.detail || 'Failed to load document')
      toast.error('Failed to load document')
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />
      case 'processing':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
      default:
        return <FileText className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-700 bg-green-100'
      case 'failed':
        return 'text-red-700 bg-red-100'
      case 'processing':
        return 'text-blue-700 bg-blue-100'
      default:
        return 'text-gray-700 bg-gray-100'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading document...</span>
      </div>
    )
  }

  if (error || !document) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/documents')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Documents
          </Button>
        </div>

        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <AlertCircle className="h-12 w-12 text-red-400 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Document not found</h3>
            <p className="text-gray-600 text-center">
              {error || 'The requested document could not be loaded.'}
            </p>
            <Button
              className="mt-4"
              onClick={() => navigate('/documents')}
            >
              Back to Documents
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/documents')}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Documents
        </Button>
      </div>

      {/* Document Info */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <CardTitle className="text-xl">
                  {document.title || document.original_filename}
                </CardTitle>
                <CardDescription className="mt-1">
                  {document.original_filename} • {document.word_count.toLocaleString()} words
                  {document.content_quality && (
                    <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs">
                      Quality: {document.content_quality}
                    </span>
                  )}
                </CardDescription>
              </div>
            </div>
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${getStatusColor(document.processing_status)}`}>
              {getStatusIcon(document.processing_status)}
              <span className="capitalize">{document.processing_status}</span>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Metadata */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Upload Date</span>
              <p className="font-medium">{new Date(document.created_at).toLocaleDateString()}</p>
            </div>
            {document.quality_score && (
              <div>
                <span className="text-gray-500">Quality Score</span>
                <p className="font-medium">{document.quality_score}/100</p>
              </div>
            )}
            {document.difficulty_level && (
              <div>
                <span className="text-gray-500">Difficulty</span>
                <p className="font-medium capitalize">{document.difficulty_level}</p>
              </div>
            )}
            {document.language_detected && (
              <div>
                <span className="text-gray-500">Language</span>
                <p className="font-medium capitalize">{document.language_detected}</p>
              </div>
            )}
          </div>

          {/* Processing Error */}
          {document.processing_error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-md">
              <h4 className="text-sm font-medium text-red-800 mb-2">Processing Error</h4>
              <p className="text-sm text-red-700">{document.processing_error}</p>
            </div>
          )}

          {/* Content */}
          {document.content && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Content</h3>
              <div className="p-4 bg-gray-50 rounded-lg max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                  {document.content}
                </pre>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex space-x-2 pt-4">
            {document.processing_status === 'completed' && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate(`/documents/${document.id}/quiz`)}
                >
                  Generate Quiz
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate(`/documents/${document.id}/flashcards`)}
                >
                  Generate Flashcards
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
