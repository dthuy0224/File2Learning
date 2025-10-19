import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Upload, FileText, Calendar, Loader2, X, Bot } from 'lucide-react'
import { toast } from 'react-hot-toast'
import AIService, { Document } from '@/services/aiService'
import ProgressIndicator from '@/components/ProgressIndicator'

export default function DocumentsPage() {
  const navigate = useNavigate()
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [topic, setTopic] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      const data = await AIService.getDocuments()
      setDocuments(data)
    } catch (error) {
      console.error('Error fetching documents:', error)
      toast.error('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (file: File) => {
    try {
      setUploading(true)
      const result = await AIService.uploadDocument(file)
      toast.success(`Document uploaded successfully! ID: ${result.document_id}`)

      // Refresh documents list
      await fetchDocuments()

      // Set up polling for status updates
      pollDocumentStatus(result.document_id)
    } catch (error: any) {
      console.error('Error uploading document:', error)
      toast.error(error.response?.data?.detail || 'Failed to upload document')
    } finally {
      setUploading(false)
    }
  }

  const pollDocumentStatus = (documentId: number) => {
    const interval = setInterval(async () => {
      try {
        const status = await AIService.getDocumentStatus(documentId)

        // Update document in list
        setDocuments(prev => prev.map(doc =>
          doc.id === documentId
            ? {
                ...doc,
                processing_status: status.status as any,
                content_quality: status.content_quality,
                quality_score: status.quality_score,
                processed_at: status.processed_at
              }
            : doc
        ))

        // Stop polling when processing is complete
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval)
          if (status.status === 'completed') {
            toast.success('Document processing completed!')
          } else if (status.status === 'failed') {
            toast.error(`Document processing failed: ${status.processing_error}`)
          }
        }
      } catch (error) {
        console.error('Error polling document status:', error)
        clearInterval(interval)
      }
    }, 2000) // Poll every 2 seconds

    // Stop polling after 5 minutes
    setTimeout(() => clearInterval(interval), 300000)
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0])
    }
  }

  const handleDeleteDocument = async (documentId: number) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      await AIService.deleteDocument(documentId)
      toast.success('Document deleted successfully')
      await fetchDocuments()
    } catch (error) {
      console.error('Error deleting document:', error)
      toast.error('Failed to delete document')
    }
  }

  const handleGenerateFromTopic = async () => {
    if (!topic.trim()) {
      toast.error('Please enter a topic.')
      return
    }
    setIsGenerating(true)
    try {
      const newDocument = await AIService.createDocumentFromTopic(topic)
      toast.success(`Document "${newDocument.title || newDocument.original_filename}" is being generated.`)
      setTopic("")
      await fetchDocuments()
    } catch (error: any) {
      console.error('Error generating document from topic:', error)
      toast.error(error.response?.data?.detail || 'Could not generate document from topic.')
    } finally {
      setIsGenerating(false)
    }
  }


  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading documents...</span>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">My Documents</h1>

      <Tabs defaultValue="upload" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="upload" className="flex items-center space-x-2">
            <Upload className="h-4 w-4" />
            <span>Upload File</span>
          </TabsTrigger>
          <TabsTrigger value="topic" className="flex items-center space-x-2">
            <Bot className="h-4 w-4" />
            <span>Generate from Topic</span>
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Upload File */}
        <TabsContent value="upload" className="space-y-6">
          {/* Header */}
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Upload Documents</h2>
              <p className="text-gray-600 mt-1">Upload and manage your learning materials</p>
            </div>
            <Button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="flex items-center space-x-2"
            >
              {uploading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Upload className="h-4 w-4" />
              )}
              <span>{uploading ? 'Uploading...' : 'Upload Document'}</span>
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.doc,.txt"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {/* Upload Area */}
          <Card
            className={`border-2 border-dashed transition-colors cursor-pointer ${
              dragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Upload className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {uploading ? 'Uploading document...' : 'Upload your documents'}
              </h3>
              <p className="text-gray-600 text-center max-w-sm">
                Drag and drop your PDF, Word documents, or text files here to generate learning materials
              </p>
              <Button
                className="mt-4"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
              >
                {uploading ? 'Uploading...' : 'Choose Files'}
              </Button>
            </CardContent>
          </Card>

          {/* Documents List */}
          <div className="grid gap-4">
            {documents.length === 0 ? (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <FileText className="h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No documents yet</h3>
                  <p className="text-gray-600 text-center">
                    Upload your first document to get started with AI-powered learning materials
                  </p>
                </CardContent>
              </Card>
            ) : (
              documents.map((doc) => (
                <Card key={doc.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        <div className="p-2 bg-blue-100 rounded-lg">
                          <FileText className="h-5 w-5 text-blue-600" />
                        </div>
                        <div className="flex-1">
                          <CardTitle className="text-lg">{doc.title || doc.original_filename}</CardTitle>
                          <CardDescription className="mt-1">
                            {doc.original_filename} • {doc.word_count.toLocaleString()} words
                            {doc.content_quality && (
                              <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs">
                                Quality: {doc.content_quality}
                              </span>
                            )}
                          </CardDescription>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <ProgressIndicator
                          status={doc.processing_status as any}
                          progress={doc.processing_status === 'processing' ? 75 : undefined}
                          error={doc.processing_error}
                        />
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDeleteDocument(doc.id)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <div className="flex items-center space-x-1">
                          <Calendar className="h-4 w-4" />
                          <span>Uploaded {new Date(doc.created_at).toLocaleDateString()}</span>
                        </div>
                        {doc.quality_score && (
                          <span>Score: {doc.quality_score}/100</span>
                        )}
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate(`/documents/${doc.id}`)}
                        >
                          View Content
                        </Button>
                        {doc.processing_status === 'completed' && (
                          <>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => window.open(`/documents/${doc.id}/quiz`, '_blank')}
                            >
                              Generate Quiz
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => window.open(`/documents/${doc.id}/flashcards`, '_blank')}
                            >
                              Generate Flashcards
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                    {doc.processing_error && (
                      <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-sm text-red-800">
                          <strong>Error:</strong> {doc.processing_error}
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        {/* Tab 2: Generate from Topic */}
        <TabsContent value="topic" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bot className="h-5 w-5" />
                <span>Create Learning Material from a Topic</span>
              </CardTitle>
              <CardDescription>
                Enter a topic, and our AI will generate a reading passage for you to learn from.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="topic" className="text-sm font-medium">
                  Topic
                </label>
                <Input
                  id="topic"
                  placeholder="e.g., 'Business English for Meetings' or 'IELTS Reading: Space Exploration'"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  disabled={isGenerating}
                  className="w-full"
                />
              </div>
              <Button
                onClick={handleGenerateFromTopic}
                disabled={isGenerating || !topic.trim()}
                className="w-full flex items-center space-x-2"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Bot className="h-4 w-4" />
                    <span>Generate Material</span>
                  </>
                )}
              </Button>
              <p className="text-sm text-gray-600">
                The AI will create an educational reading passage (400-500 words) in English based on your topic.
                This content can then be used to generate quizzes and flashcards.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
