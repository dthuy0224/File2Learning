import api from './api'

// Types for AI responses
export interface QuizQuestion {
  question: string
  options?: string[]
  correct_answer: string
  question_type: 'multiple_choice' | 'fill_blank'
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

export class AIService {
  // Document operations
  static async getDocuments(): Promise<Document[]> {
    const response = await api.get('/v1/documents/')
    return response.data
  }

  static async getDocument(documentId: number): Promise<Document> {
    const response = await api.get(`/v1/documents/${documentId}`)
    return response.data
  }

  static async getDocumentStatus(documentId: number): Promise<DocumentStatus> {
    const response = await api.get(`/v1/documents/${documentId}/status`)
    return response.data
  }

  static async getDocumentsStatusBatch(documentIds: string): Promise<{documents: Record<string, DocumentStatus>}> {
    const response = await api.get(`/v1/documents/status/batch?document_ids=${documentIds}`)
    return response.data
  }

  static async uploadDocument(file: File): Promise<{document_id: number, status: string}> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/v1/documents/upload', formData, {
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
    const response = await api.post(`/v1/ai/${documentId}/generate-quiz`, null, {
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
    const response = await api.post(`/v1/ai/${documentId}/generate-flashcards`, null, {
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
    const response = await api.post(`/v1/ai/${documentId}/generate-summary`, null, {
      params: {
        max_length: maxLength,
      },
    })
    return response.data
  }

  // Utility functions
  static async getAvailableModels(): Promise<{models: Array<{name: string, description: string, size: string}>, default_model: string}> {
    const response = await api.get('/v1/ai/models')
    return response.data
  }

  static async testAIConnection(): Promise<{status: string, message: string, model?: string}> {
    const response = await api.post('/v1/ai/test-connection')
    return response.data
  }

  // Document management
  static async getDocumentContent(documentId: number): Promise<{document_id: number, title: string, content: string, word_count: number, document_type: string, created_at: string}> {
    const response = await api.get(`/v1/documents/${documentId}/content`)
    return response.data
  }

  static async deleteDocument(documentId: number): Promise<{message: string}> {
    const response = await api.delete(`/v1/documents/${documentId}`)
    return response.data
  }
}

export default AIService
