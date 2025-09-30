import { useQuery } from '@tanstack/react-query'
import { progressService } from '@/services/progressService'

// Custom hooks for progress data using React Query
export const useUserStats = (rangeDays: number = 30) => {
  return useQuery({
    queryKey: ['userStats', rangeDays],
    queryFn: () => progressService.getUserStats(rangeDays),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  })
}

export const useActivityHeatmap = (rangeDays: number = 90) => {
  return useQuery({
    queryKey: ['activityHeatmap', rangeDays],
    queryFn: () => progressService.getActivityHeatmap(rangeDays),
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
  })
}

export const usePerformanceHistory = (rangeDays: number = 30) => {
  return useQuery({
    queryKey: ['performanceHistory', rangeDays],
    queryFn: () => progressService.getPerformanceHistory(rangeDays),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  })
}

export const useSkillBreakdown = (rangeDays: number = 30) => {
  return useQuery({
    queryKey: ['skillBreakdown', rangeDays],
    queryFn: () => progressService.getSkillBreakdown(rangeDays),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  })
}

export const useRecentActivities = (limit: number = 10) => {
  return useQuery({
    queryKey: ['recentActivities', limit],
    queryFn: () => progressService.getRecentActivities(limit),
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchOnWindowFocus: false,
  })
}

export const useFullProgress = (rangeDays: number = 30) => {
  return useQuery({
    queryKey: ['fullProgress', rangeDays],
    queryFn: () => progressService.getFullProgress(rangeDays),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  })
}
