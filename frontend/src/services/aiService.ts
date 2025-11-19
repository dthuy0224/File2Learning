import api from './api'

// Types for AI responses
export interface QuizQuestion {
  question: string
  options?: string[]
  correct_answer: string
  question_type: 'multiple_choice' | 'fill_blank'
}

// Extended interface for frontend use with additional fields
export interface QuizQuestionExtended extends QuizQuestion {
  id: number
  question_text: string
  explanation?: string
  points: number
  order_index: number
  quiz_id: number
  created_at: string
}

export interface Flashcard {
  front_text: string
  back_text: string
  example_sentence?: string
}

export interface Document {
  id: number
  title: string
  filename: string
  original_filename: string
  document_type: string
  word_count: number
  processing_status: 'pending' | 'processing' | 'completed' | 'failed'
  processing_error?: string
  content_quality?: string
  quality_score?: number
  created_at: string
  processed_at?: string
  content?: string
  summary?: string
  difficulty_level?: string
  language_detected?: string
}

export interface QuizResponse {
  quiz: QuizQuestion[]
  document_id: number
  model_used: string
  generated_by: string
}

export interface FlashcardResponse {
  flashcards: Flashcard[]
  document_id: number
  model_used: string
}

export interface SummaryResponse {
  summary: string
  document_id: number
  model_used: string
  original_length: number
  summary_length: number
}

export interface DocumentStatus {
  document_id: number
  status: string
  filename: string
  document_type: string
  word_count: number
  difficulty_level: string
  content_quality?: string
  quality_score?: number
  created_at: string
  processed_at?: string
  processing_error?: string
  progress: {
    percentage: number
    stage: string
    estimated_completion?: string
    elapsed_time_seconds?: number
  }
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export interface ChatResponse {
  answer: string
  document_id: number
  ai_model: string
  success: boolean
  message?: string
  error?: string
}

export class AIService {
  // Document operations
  static async getDocuments(): Promise<Document[]> {
    const response = await api.get('/documents/')
    return response.data
  }

  static async getDocument(documentId: number): Promise<Document> {
    const response = await api.get(`/documents/${documentId}`)
    return response.data
  }

  static async getDocumentStatus(documentId: number): Promise<DocumentStatus> {
    const response = await api.get(`/documents/${documentId}/status`)
    return response.data
  }

  static async getDocumentsStatusBatch(documentIds: string): Promise<{documents: Record<string, DocumentStatus>}> {
    const response = await api.get(`/documents/status/batch?document_ids=${documentIds}`)
    return response.data
  }

  static async uploadDocument(file: File): Promise<{document_id: number, status: string}> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  // AI Generation operations
  static async generateQuiz(
    documentId: number,
    quizType: 'mcq' | 'fill_blank' | 'mixed' = 'mixed',
    numQuestions: number = 5
  ): Promise<QuizResponse> {
    const response = await api.post(`/ai/${documentId}/generate-quiz`, null, {
      params: {
        quiz_type: quizType,
        num_questions: numQuestions,
      },
    })
    return response.data
  }

  static async generateFlashcards(
    documentId: number,
    numCards: number = 10
  ): Promise<FlashcardResponse> {
    const response = await api.post(`/ai/${documentId}/generate-flashcards`, null, {
      params: {
        num_cards: numCards,
      },
    })
    return response.data
  }

  static async generateSummary(
    documentId: number,
    maxLength: number = 300
  ): Promise<SummaryResponse> {
    const response = await api.post(`/ai/${documentId}/generate-summary`, null, {
      params: {
        max_length: maxLength,
      },
    })
    return response.data
  }

  // Utility functions
  static async getAvailableModels(): Promise<{models: Array<{name: string, description: string, size: string}>, default_model: string}> {
    const response = await api.get('/ai/models')
    return response.data
  }

  static async testAIConnection(): Promise<{status: string, message: string, model?: string}> {
    const response = await api.post('/ai/test-connection')
    return response.data
  }

  // Document management
  static async getDocumentContent(documentId: number): Promise<{document_id: number, title: string, content: string, word_count: number, document_type: string, created_at: string}> {
    const response = await api.get(`/documents/${documentId}/content`)
    return response.data
  }

  static async deleteDocument(documentId: number): Promise<{message: string}> {
    const response = await api.delete(`/documents/${documentId}`)
    return response.data
  }

  // Quiz operations
  static async saveQuiz(quizData: {
    title: string
    description?: string
    quiz_type: string
    difficulty_level?: string
    document_id?: number
    questions: {
      question: string
      options?: string[]
      correct_answer: string
      question_type: 'multiple_choice' | 'fill_blank' | 'true_false'
      explanation?: string
      points?: number
    }[]
  }): Promise<any> {
    // Use the quiz service to create the quiz
    const { QuizService } = await import('./quizService')
    return QuizService.createQuizFromAI(quizData)
  }

  // Chat operations
  static async chatWithDocument(
    documentId: number,
    query: string,
    history: ChatMessage[] = []
  ): Promise<ChatResponse> {
    const response = await api.post(`/ai/${documentId}/chat`, {
      query,
      conversation_history: history,
    })
    return response.data
  }

  // Document creation operations
  static async createDocumentFromTopic(topic: string): Promise<Document> {
    const response = await api.post('/documents/from-topic', { topic })
    return response.data
  }
}

export default AIService
