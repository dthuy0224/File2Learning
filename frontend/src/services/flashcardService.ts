import api from './api'

// Types for Flashcard API responses
export interface Flashcard {
  id: number
  front_text: string
  back_text: string
  example_sentence?: string
  pronunciation?: string
  word_type?: string
  difficulty_level: string
  tags?: string
  ease_factor: number
  interval: number
  repetitions: number
  next_review_date?: string
  times_reviewed: number
  times_correct: number
  last_review_quality?: number
  owner_id: number
  document_id?: number
  created_at: string
  updated_at: string
}

export interface FlashcardSet {
  id: number
  title?: string
  original_filename: string
  card_count: number
  created_at: string
}

export interface FlashcardCreate {
  front_text: string
  back_text: string
  example_sentence?: string
  pronunciation?: string
  word_type?: string
  difficulty_level?: string
  tags?: string
  document_id?: number
}

export interface FlashcardUpdate {
  front_text?: string
  back_text?: string
  example_sentence?: string
  pronunciation?: string
  word_type?: string
  difficulty_level?: string
  tags?: string
}

export interface FlashcardReview {
  quality: number  // 0-5 rating
  response_time?: number  // milliseconds
}

export class FlashcardService {
  // Get all flashcards for current user
  static async getFlashcards(skip: number = 0, limit: number = 100): Promise<Flashcard[]> {
    const response = await api.get('/flashcards/', {
      params: { skip, limit }
    })
    return response.data
  }

  // Get flashcards due for review
  static async getDueFlashcards(limit: number = 50): Promise<Flashcard[]> {
    const response = await api.get('/flashcards/due', {
      params: { limit }
    })
    return response.data
  }

  // Create a new flashcard
  static async createFlashcard(flashcardData: FlashcardCreate): Promise<Flashcard> {
    const response = await api.post('/flashcards/', flashcardData)
    return response.data
  }

  // Get a specific flashcard by ID
  static async getFlashcard(flashcardId: number): Promise<Flashcard> {
    const response = await api.get(`/flashcards/${flashcardId}`)
    return response.data
  }

  // Update a flashcard
  static async updateFlashcard(flashcardId: number, updateData: FlashcardUpdate): Promise<Flashcard> {
    const response = await api.put(`/flashcards/${flashcardId}`, updateData)
    return response.data
  }

  // Review a flashcard (update SRS data)
  static async reviewFlashcard(flashcardId: number, reviewData: FlashcardReview): Promise<Flashcard> {
    const response = await api.post(`/flashcards/${flashcardId}/review`, reviewData)
    return response.data
  }

  // Delete a flashcard
  static async deleteFlashcard(flashcardId: number): Promise<{ message: string }> {
    const response = await api.delete(`/flashcards/${flashcardId}`)
    return response.data
  }

  // Helper method to create multiple flashcards (calls createFlashcard multiple times)
  static async createMultipleFlashcards(flashcards: FlashcardCreate[]): Promise<Flashcard[]> {
    const results = await Promise.all(
      flashcards.map(flashcardData => this.createFlashcard(flashcardData))
    )
    return results
  }

  // Get all flashcard sets (documents with flashcards)
  static async getFlashcardSets(): Promise<FlashcardSet[]> {
    const response = await api.get('/flashcard-sets/')
    return response.data
  }

  // Get all flashcards in a specific set
  static async getFlashcardsInSet(setId: number): Promise<Flashcard[]> {
    const response = await api.get(`/flashcard-sets/${setId}/cards`)
    return response.data
  }

  // Helper method to get flashcard statistics from the list
  static getFlashcardStatsFromList(flashcards: Flashcard[]): {
    total_cards: number
    due_today: number
    due_this_week: number
    mastered: number
    learning: number
    new: number
  } {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)

    return flashcards.reduce((stats, card) => {
      stats.total_cards++

      if (card.next_review_date) {
        const reviewDate = new Date(card.next_review_date)
        if (reviewDate <= today) {
          stats.due_today++
        } else if (reviewDate <= weekFromNow) {
          stats.due_this_week++
        }
      }

      // Match backend logic: ease_factor >= 2.0 AND repetitions >= 2
      // This ensures consistency with Dashboard, Progress, and Analytics pages
      if (card.ease_factor >= 2.0 && card.repetitions >= 2) {
        stats.mastered++
      } else if (card.repetitions > 0) {
        stats.learning++
      } else {
        stats.new++
      }

      return stats
    }, {
      total_cards: 0,
      due_today: 0,
      due_this_week: 0,
      mastered: 0,
      learning: 0,
      new: 0
    })
  }
}

export default FlashcardService