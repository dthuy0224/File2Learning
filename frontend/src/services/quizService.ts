import api from './api'

// Types for Quiz API responses
export interface QuizQuestion {
  id: number
  quiz_id: number
  question_text: string
  question_type: string  // 'multiple_choice', 'fill_blank', 'true_false'
  correct_answer: string
  options?: string[]
  explanation?: string
  difficulty_level: string
  points: number
  order_index: number
  created_at: string
}

export interface Quiz {
  id: number
  title: string
  description?: string
  quiz_type: string  // 'vocabulary', 'reading_comprehension', 'mixed'
  difficulty_level: string
  time_limit?: number
  document_id?: number
  created_by: number
  created_at: string
  updated_at: string
  questions: QuizQuestion[]
}

export interface QuizCreate {
  title: string
  description?: string
  quiz_type: string
  difficulty_level?: string
  time_limit?: number
  document_id?: number
  questions: QuizQuestionCreate[]
}

export interface QuizQuestionCreate {
  question_text: string
  question_type: string
  correct_answer: string
  options?: string[]
  explanation?: string
  difficulty_level?: string
  points?: number
  order_index: number
}

export interface QuizUpdate {
  title?: string
  description?: string
  difficulty_level?: string
  time_limit?: number
}

export interface QuizAttemptCreate {
  quiz_id: number
}

export interface QuizAnswer {
  question_id: number
  answer: string
  time_taken?: number  // seconds for this question
}

export interface QuizAttemptSubmit {
  quiz_id: number
  answers: { [questionId: number]: string }
  total_time?: number  // total seconds
}

export interface QuizAttempt {
  id: number
  quiz_id: number
  user_id: number
  answers: { [key: string]: any }
  score: number
  max_score: number
  percentage: number
  time_taken?: number
  is_completed: boolean
  started_at: string
  completed_at?: string
}

export class QuizService {
  // Get all quizzes for current user
  static async getQuizzes(skip: number = 0, limit: number = 100): Promise<Quiz[]> {
    const response = await api.get('/v1/quizzes/', {
      params: { skip, limit }
    })
    return response.data
  }

  // Create a new quiz
  static async createQuiz(quizData: QuizCreate): Promise<Quiz> {
    const response = await api.post('/v1/quizzes/', quizData)
    return response.data
  }

  // Get a specific quiz by ID
  static async getQuiz(quizId: number): Promise<Quiz> {
    const response = await api.get(`/v1/quizzes/${quizId}`)
    return response.data
  }

  // Update a quiz
  static async updateQuiz(quizId: number, updateData: QuizUpdate): Promise<Quiz> {
    const response = await api.put(`/v1/quizzes/${quizId}`, updateData)
    return response.data
  }

  // Delete a quiz
  static async deleteQuiz(quizId: number): Promise<{ message: string }> {
    const response = await api.delete(`/v1/quizzes/${quizId}`)
    return response.data
  }

  // Start a quiz attempt
  static async startQuizAttempt(quizId: number): Promise<{ message: string, quiz_id: number }> {
    const response = await api.post(`/v1/quizzes/${quizId}/attempt`)
    return response.data
  }

  // Submit quiz answers
  static async submitQuizAttempt(quizId: number, submission: QuizAttemptSubmit): Promise<QuizAttempt> {
    const response = await api.post(`/v1/quizzes/${quizId}/submit`, submission)
    return response.data
  }

  // Get quiz attempts for a specific quiz
  static async getQuizAttempts(quizId: number): Promise<QuizAttempt[]> {
    const response = await api.get(`/v1/quizzes/${quizId}/attempts`)
    return response.data
  }

  // Helper method to create quiz from AI-generated questions
  static async createQuizFromAI(quizData: {
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
  }): Promise<Quiz> {
    const formattedQuestions: QuizQuestionCreate[] = quizData.questions.map((q, index) => ({
      question_text: q.question,
      question_type: q.question_type,
      correct_answer: q.correct_answer,
      options: q.options,
      explanation: q.explanation,
      points: q.points || 1,
      order_index: index + 1
    }))

    const quizCreateData: QuizCreate = {
      title: quizData.title,
      description: quizData.description,
      quiz_type: quizData.quiz_type,
      difficulty_level: quizData.difficulty_level || 'medium',
      document_id: quizData.document_id,
      questions: formattedQuestions
    }

    return this.createQuiz(quizCreateData)
  }

  // Get quiz statistics
  static getQuizStatsFromAttempts(attempts: QuizAttempt[]): {
    total_attempts: number
    average_score: number
    highest_score: number
    completion_rate: number
    average_time: number
  } {
    if (attempts.length === 0) {
      return {
        total_attempts: 0,
        average_score: 0,
        highest_score: 0,
        completion_rate: 0,
        average_time: 0
      }
    }

    const completed = attempts.filter(a => a.is_completed).length
    const totalScore = attempts.reduce((sum, a) => sum + a.score, 0)
    const maxScore = Math.max(...attempts.map(a => a.score))
    const totalTime = attempts.reduce((sum, a) => sum + (a.time_taken || 0), 0)

    return {
      total_attempts: attempts.length,
      average_score: Math.round(totalScore / attempts.length),
      highest_score: maxScore,
      completion_rate: Math.round((completed / attempts.length) * 100),
      average_time: Math.round(totalTime / attempts.length)
    }
  }
}

export default QuizService
