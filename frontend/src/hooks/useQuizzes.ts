import { useQuery } from '@tanstack/react-query'
import QuizService from '@/services/quizService'

// Custom hook for quizzes data using React Query
export const useQuizzes = (skip: number = 0, limit: number = 100) => {
  return useQuery({
    queryKey: ['quizzes', skip, limit],
    queryFn: () => QuizService.getQuizzes(skip, limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true, // Refetch when user returns to tab
  })
}

// Hook for a single quiz
export const useQuiz = (quizId: number) => {
  return useQuery({
    queryKey: ['quiz', quizId],
    queryFn: () => QuizService.getQuiz(quizId),
    enabled: !!quizId, // Only run if quizId is provided
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: true,
  })
}

// Hook for quiz attempts
export const useQuizAttempts = (quizId: number) => {
  return useQuery({
    queryKey: ['quizAttempts', quizId],
    queryFn: () => QuizService.getQuizAttempts(quizId),
    enabled: !!quizId,
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchOnWindowFocus: true,
  })
}
