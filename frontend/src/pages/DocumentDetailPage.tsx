import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { 
  ArrowLeft, FileText, Loader2, CheckCircle, AlertCircle, MessageCircle, 
  Copy, Maximize2, Minimize2, BookOpen, Sparkles, Brain, Clock, 
  BarChart3, Target, Zap
} from 'lucide-react'
import { toast } from 'react-hot-toast'
import AIService, { Document } from '../services/aiService'
import ChatbotModal from '../components/ChatbotModal'

export default function DocumentDetailPage() {
  const { documentId } = useParams<{ documentId: string }>()
  const navigate = useNavigate()
  const [document, setDocument] = useState<Document | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isChatModalOpen, setIsChatModalOpen] = useState(false)
  const [generatingSummary, setGeneratingSummary] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [scrollProgress, setScrollProgress] = useState(0)
  const [activeTab, setActiveTab] = useState('content')
  const contentRef = useRef<HTMLDivElement>(null)
  const contentContainerRef = useRef<HTMLDivElement>(null)

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

  const handleGenerateSummary = async () => {
    if (!documentId || !document) return

    try {
      setGeneratingSummary(true)
      const docId = parseInt(documentId)
      
      toast.loading('Generating summary with AI...', { id: 'summary-gen' })
      
      const result = await AIService.generateSummary(docId, 300)
      
      setDocument({
        ...document,
        summary: result.summary
      })
      
      toast.success(
        `Summary generated successfully using ${result.model_used}!`,
        { id: 'summary-gen' }
      )
      
    } catch (error: any) {
      console.error('Error generating summary:', error)
      toast.error(
        error.response?.data?.detail || 'Failed to generate summary',
        { id: 'summary-gen' }
      )
    } finally {
      setGeneratingSummary(false)
    }
  }

  const handleCopyContent = async () => {
    if (!document?.content) return
    
    try {
      await navigator.clipboard.writeText(document.content)
      toast.success('Content copied to clipboard!')
    } catch (error) {
      console.error('Failed to copy:', error)
      toast.error('Failed to copy content')
    }
  }

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
  }

  const handleScroll = () => {
    if (!contentContainerRef.current) return
    
    const container = contentContainerRef.current
    const scrollTop = container.scrollTop
    const scrollHeight = container.scrollHeight - container.clientHeight
    const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0
    setScrollProgress(progress)
  }

  useEffect(() => {
    const container = contentContainerRef.current
    if (container) {
      container.addEventListener('scroll', handleScroll)
      return () => container.removeEventListener('scroll', handleScroll)
    }
  }, [document])

  const getWordCount = (text: string) => {
    if (!text) return 0
    return text.trim().split(/\s+/).filter(word => word.length > 0).length
  }

  const getReadingTime = (wordCount: number) => {
    const wordsPerMinute = 200
    return Math.ceil(wordCount / wordsPerMinute)
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

  const stats = [
    { 
      icon: Clock, 
      label: 'Reading Time', 
      value: `${getReadingTime(getWordCount(document.content || ''))} min`, 
      color: 'text-blue-600' 
    },
    { 
      icon: BookOpen, 
      label: 'Word Count', 
      value: document.word_count.toLocaleString(), 
      color: 'text-green-600' 
    },
    { 
      icon: BarChart3, 
      label: 'Difficulty', 
      value: document.difficulty_level ? document.difficulty_level.charAt(0).toUpperCase() + document.difficulty_level.slice(1) : 'N/A', 
      color: 'text-orange-600' 
    },
    { 
      icon: Target, 
      label: 'Quality', 
      value: document.quality_score ? `${document.quality_score}/100` : 'N/A', 
      color: 'text-purple-600' 
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Fixed Header */}
      <div className="sticky top-0 z-10 bg-white/90 backdrop-blur-sm border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/documents')}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Documents</span>
            </Button>
            
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopyContent}
                className="h-8 w-8 p-0"
                title="Copy content"
              >
                <Copy className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleFullscreen}
                className="h-8 w-8 p-0"
                title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
              >
                {isFullscreen ? (
                  <Minimize2 className="h-4 w-4" />
                ) : (
                  <Maximize2 className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          {/* Reading Progress */}
          <div className="mt-3 h-1 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
              style={{ width: `${scrollProgress}%` }}
            />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Sidebar - Stats */}
          <div className="lg:col-span-3 space-y-4">
            <div className="sticky top-24 space-y-4">
              {/* Quick Stats */}
              <Card className="shadow-sm">
                <CardHeader>
                  <CardTitle className="text-lg">Quick Stats</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {stats.map((stat, idx) => (
                    <div key={idx} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <stat.icon className={`w-4 h-4 ${stat.color}`} />
                        <span className="text-sm text-gray-600">{stat.label}</span>
                      </div>
                      <span className="text-sm font-semibold text-gray-900">{stat.value}</span>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Document Info Card */}
              <Card className="shadow-sm">
                <CardHeader>
                  <CardTitle className="text-lg">Document Info</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm">
                  <div>
                    <span className="text-gray-500">Upload Date</span>
                    <p className="font-medium mt-1">{new Date(document.created_at).toLocaleDateString()}</p>
                  </div>
                  {document.language_detected && (
                    <div>
                      <span className="text-gray-500">Language</span>
                      <p className="font-medium mt-1 capitalize">{document.language_detected}</p>
                    </div>
                  )}
                  {document.content_quality && (
                    <div>
                      <span className="text-gray-500">Content Quality</span>
                      <p className="font-medium mt-1">{document.content_quality}</p>
                    </div>
                  )}
                  <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm ${getStatusColor(document.processing_status)}`}>
                    {getStatusIcon(document.processing_status)}
                    <span className="capitalize">{document.processing_status}</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-9 space-y-6">
            
            {/* Document Header */}
            <Card className="shadow-sm">
              <CardHeader>
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl">
                    <FileText className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="text-2xl font-bold mb-2">
                      {document.title || document.original_filename}
                    </CardTitle>
                    <CardDescription className="flex flex-wrap items-center gap-2">
                      <span className="flex items-center gap-1">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        {document.processing_status === 'completed' ? 'Processed' : document.processing_status}
                      </span>
                      <span>•</span>
                      <span>{new Date(document.created_at).toLocaleDateString()}</span>
                      <span>•</span>
                      <span>{document.original_filename}</span>
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>

            {/* Tabs Navigation */}
            <Card className="shadow-sm">
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="w-full grid grid-cols-2 h-auto p-1">
                  <TabsTrigger value="content" className="flex items-center gap-2">
                    <BookOpen className="w-4 h-4" />
                    Content
                  </TabsTrigger>
                  <TabsTrigger value="summary" className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    AI Summary
                  </TabsTrigger>
                </TabsList>

                {/* Content Tab */}
                <TabsContent value="content" className="mt-0">
                  {document.content ? (
                    <div className="space-y-4">
                      <div className={`relative bg-gradient-to-br from-white via-gray-50/50 to-white border border-gray-200 rounded-xl shadow-lg overflow-hidden transition-all duration-300 ${isFullscreen ? 'fixed inset-4 z-50' : ''}`}>
                        {/* Reading Progress Bar */}
                        <div className="absolute top-0 left-0 right-0 h-1 bg-gray-200 z-10">
                          <div 
                            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-150"
                            style={{ width: `${scrollProgress}%` }}
                          />
                        </div>

                        {/* Header Bar */}
                        <div className="flex items-center justify-between px-4 py-3 bg-white/80 backdrop-blur-sm border-b border-gray-200/50">
                          <div className="flex items-center gap-3 text-xs text-gray-600">
                            <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded-md font-medium">
                              {Math.round(scrollProgress)}% read
                            </span>
                          </div>
                        </div>

                        {/* Content Area with Paper-like Effect */}
                        <div 
                          ref={contentContainerRef}
                          className={`relative overflow-y-auto custom-scrollbar paper-texture ${isFullscreen ? 'h-[calc(100vh-8rem)]' : 'max-h-[600px]'}`}
                        >
                          {/* Fade Edges */}
                          <div className="sticky top-0 h-8 bg-gradient-to-b from-white via-white/80 to-transparent pointer-events-none z-10" />
                          <div className="sticky bottom-0 h-8 bg-gradient-to-t from-white via-white/80 to-transparent pointer-events-none z-10" />
                          
                          <div 
                            ref={contentRef}
                            className="px-8 py-8 whitespace-pre-wrap text-base text-gray-800 leading-8 font-sans selection:bg-blue-200 selection:text-blue-900"
                          >
                            {document.content}
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="p-8 text-center text-gray-500">
                      <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                      <p>No content available for this document.</p>
                    </div>
                  )}
                </TabsContent>

                {/* Summary Tab */}
                <TabsContent value="summary" className="mt-0">
                  <div className="space-y-4">
                    {document.summary ? (
                      <div className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-xl p-6">
                        <div className="flex items-start gap-3 mb-4">
                          <div className="p-2 bg-blue-500 rounded-lg">
                            <Sparkles className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900 mb-1">AI-Generated Summary</h3>
                            <p className="text-sm text-gray-600">Comprehensive overview of the document</p>
                          </div>
                        </div>
                        <p className="text-gray-800 leading-relaxed">
                          {document.summary}
                        </p>
                      </div>
                    ) : (
                      <div className="p-8 bg-yellow-50 rounded-xl border-2 border-yellow-200 text-center">
                        <Sparkles className="w-12 h-12 mx-auto mb-4 text-yellow-600" />
                        <p className="text-yellow-800 mb-4">No summary available for this document yet.</p>
                        <Button
                          onClick={handleGenerateSummary}
                          disabled={generatingSummary}
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          {generatingSummary ? (
                            <>
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              Generating...
                            </>
                          ) : (
                            <>
                              <Sparkles className="h-4 w-4 mr-2" />
                              Generate Summary with AI
                            </>
                          )}
                        </Button>
                      </div>
                    )}

                    {/* Action Cards */}
                    {document.processing_status === 'completed' && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <button 
                          onClick={() => navigate(`/documents/${document.id}/quiz`)}
                          className="p-4 bg-white border-2 border-gray-200 rounded-xl hover:border-blue-400 transition-all text-left group"
                        >
                          <Brain className="w-5 h-5 text-blue-600 mb-2 group-hover:scale-110 transition-transform" />
                          <h4 className="font-semibold text-gray-900 mb-1">Generate Quiz</h4>
                          <p className="text-sm text-gray-600">Test your understanding</p>
                        </button>
                        <button 
                          onClick={() => navigate(`/documents/${document.id}/flashcards`)}
                          className="p-4 bg-white border-2 border-gray-200 rounded-xl hover:border-purple-400 transition-all text-left group"
                        >
                          <Zap className="w-5 h-5 text-purple-600 mb-2 group-hover:scale-110 transition-transform" />
                          <h4 className="font-semibold text-gray-900 mb-1">Create Flashcards</h4>
                          <p className="text-sm text-gray-600">Learn key concepts</p>
                        </button>
                      </div>
                    )}
                  </div>
                </TabsContent>
              </Tabs>
            </Card>

            {/* Action Cards */}
            {document.processing_status === 'completed' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
                  <MessageCircle className="w-8 h-8 mb-3" />
                  <h3 className="text-xl font-bold mb-2">Chat with AI</h3>
                  <p className="text-blue-100 text-sm mb-4">
                    Ask questions about this document and get instant answers
                  </p>
                  <Button 
                    onClick={() => setIsChatModalOpen(true)}
                    className="bg-white text-blue-600 hover:bg-blue-50 font-semibold"
                  >
                    Start Chat
                  </Button>
                </div>

                <div className="bg-gradient-to-br from-green-500 to-teal-600 rounded-2xl p-6 text-white shadow-lg">
                  <Target className="w-8 h-8 mb-3" />
                  <h3 className="text-xl font-bold mb-2">Study Tools</h3>
                  <p className="text-green-100 text-sm mb-4">
                    Generate quizzes and flashcards to enhance your learning
                  </p>
                  <div className="flex gap-2">
                    <Button 
                      onClick={() => navigate(`/documents/${document.id}/quiz`)}
                      variant="outline"
                      className="bg-white/20 text-white border-white/30 hover:bg-white/30"
                    >
                      Quiz
                    </Button>
                    <Button 
                      onClick={() => navigate(`/documents/${document.id}/flashcards`)}
                      variant="outline"
                      className="bg-white/20 text-white border-white/30 hover:bg-white/30"
                    >
                      Flashcards
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Chatbot Modal */}
      <ChatbotModal
        isOpen={isChatModalOpen}
        onClose={() => setIsChatModalOpen(false)}
        documentId={document.id}
        documentTitle={document.title || document.original_filename}
      />
    </div>
  )
}
