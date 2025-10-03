import { useQuery } from '@tanstack/react-query'
import FlashcardService from '@/services/flashcardService'

// Custom hook for all flashcards using React Query
export const useFlashcards = (skip: number = 0, limit: number = 100) => {
  return useQuery({
    queryKey: ['flashcards', skip, limit],
    queryFn: () => FlashcardService.getFlashcards(skip, limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true, // Refetch when user returns to tab
  })
}

// Custom hook for due flashcards (cards that need review)
export const useDueFlashcards = (limit: number = 50) => {
  return useQuery({
    queryKey: ['dueFlashcards', limit],
    queryFn: () => FlashcardService.getDueFlashcards(limit),
    staleTime: 2 * 60 * 1000, // 2 minutes - more frequent for due cards
    refetchOnWindowFocus: true,
    refetchInterval: 30 * 1000, // Refetch every 30 seconds for due cards
  })
}

// Hook for a single flashcard
export const useFlashcard = (flashcardId: number) => {
  return useQuery({
    queryKey: ['flashcard', flashcardId],
    queryFn: () => FlashcardService.getFlashcard(flashcardId),
    enabled: !!flashcardId, // Only run if flashcardId is provided
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: true,
  })
}
