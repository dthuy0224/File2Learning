import { useQuery } from '@tanstack/react-query'
import { progressService } from '@/services/progressService'

// Custom hooks for progress data using React Query
export const useUserStats = (rangeDays: number = 30) => {
  return useQuery({
    queryKey: ['userStats', rangeDays],
    queryFn: () => progressService.getUserStats(rangeDays),
    staleTime: 60 * 1000, // 1 minute - more real-time
    refetchOnWindowFocus: true, // Refresh when user returns to tab
    refetchInterval: 5 * 60 * 1000, // Auto-refresh every 5 minutes
  })
}

export const useActivityHeatmap = (rangeDays: number = 90) => {
  return useQuery({
    queryKey: ['activityHeatmap', rangeDays],
    queryFn: () => progressService.getActivityHeatmap(rangeDays),
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchOnWindowFocus: true,
    refetchInterval: 10 * 60 * 1000, // Auto-refresh every 10 minutes
  })
}

export const usePerformanceHistory = (rangeDays: number = 30) => {
  return useQuery({
    queryKey: ['performanceHistory', rangeDays],
    queryFn: () => progressService.getPerformanceHistory(rangeDays),
    staleTime: 60 * 1000, // 1 minute
    refetchOnWindowFocus: true,
    refetchInterval: 5 * 60 * 1000, // Auto-refresh every 5 minutes
  })
}

export const useSkillBreakdown = (rangeDays: number = 30) => {
  return useQuery({
    queryKey: ['skillBreakdown', rangeDays],
    queryFn: () => progressService.getSkillBreakdown(rangeDays),
    staleTime: 60 * 1000, // 1 minute
    refetchOnWindowFocus: true,
    refetchInterval: 5 * 60 * 1000, // Auto-refresh every 5 minutes
  })
}

export const useRecentActivities = (limit: number = 10) => {
  return useQuery({
    queryKey: ['recentActivities', limit],
    queryFn: () => progressService.getRecentActivities(limit),
    staleTime: 30 * 1000, // 30 seconds - most real-time for recent activities
    refetchOnWindowFocus: true,
    refetchInterval: 2 * 60 * 1000, // Auto-refresh every 2 minutes
  })
}

export const useFullProgress = (rangeDays: number = 30) => {
  return useQuery({
    queryKey: ['fullProgress', rangeDays],
    queryFn: () => progressService.getFullProgress(rangeDays),
    staleTime: 60 * 1000, // 1 minute
    refetchOnWindowFocus: true,
    refetchInterval: 5 * 60 * 1000, // Auto-refresh every 5 minutes
  })
}
