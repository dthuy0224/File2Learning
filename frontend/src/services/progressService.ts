import { api } from './api'

// Types for API responses
export interface UserStats {
  study_streak: number
  words_mastered: number
  avg_accuracy: number
  total_study_time: number
  total_quizzes_completed: number
  total_flashcards_reviewed: number
  documents_processed: number
}

export interface ActivityHeatmapPoint {
  date: string
  count: number
}

export interface PerformanceHistoryPoint {
  date: string
  accuracy: number
  quizzes_completed: number
  avg_score: number
}

export interface SkillBreakdownPoint {
  level: string
  accuracy: number
  quizzes_completed: number
  total_questions: number
}

export interface RecentActivityItem {
  id: number
  type: string
  title: string
  score?: string
  time_ago: string
  created_at: string
}

export interface ProgressResponse {
  stats: UserStats
  activity_heatmap: ActivityHeatmapPoint[]
  performance_history: PerformanceHistoryPoint[]
  skill_breakdown: SkillBreakdownPoint[]
  recent_activities: RecentActivityItem[]
}

// API service functions
export const progressService = {
  // Get user statistics and KPIs
  getUserStats: async (rangeDays: number = 30): Promise<UserStats> => {
    const response = await api.get(`/v1/users/me/stats?range_days=${rangeDays}`)
    return response.data
  },

  // Get activity heatmap data
  getActivityHeatmap: async (rangeDays: number = 90): Promise<ActivityHeatmapPoint[]> => {
    const response = await api.get(`/v1/users/me/activity-heatmap?range_days=${rangeDays}`)
    return response.data
  },

  // Get performance history
  getPerformanceHistory: async (rangeDays: number = 30): Promise<PerformanceHistoryPoint[]> => {
    const response = await api.get(`/v1/users/me/performance-history?range_days=${rangeDays}`)
    return response.data
  },

  // Get skill breakdown by difficulty
  getSkillBreakdown: async (rangeDays: number = 30): Promise<SkillBreakdownPoint[]> => {
    const response = await api.get(`/v1/users/me/skill-breakdown?range_days=${rangeDays}`)
    return response.data
  },

  // Get recent activities
  getRecentActivities: async (limit: number = 10): Promise<RecentActivityItem[]> => {
    const response = await api.get(`/v1/users/me/recent-activities?limit=${limit}`)
    return response.data
  },

  // Get complete progress data
  getFullProgress: async (rangeDays: number = 30): Promise<ProgressResponse> => {
    const response = await api.get(`/v1/users/me/progress?range_days=${rangeDays}`)
    return response.data
  }
}

export default progressService
