/**
 * Daily Plan Service
 * API calls for daily study plans
 */

import api from './api'

export interface RecommendedTask {
  type: string
  entity_ids?: number[]
  entity_id?: number
  count?: number
  title?: string
  estimated_minutes: number
  priority: string
  reason?: string
  topic?: string
  difficulty?: string
}

export interface DailyStudyPlan {
  id: number
  user_id: number
  schedule_id?: number
  plan_date: string
  plan_summary?: string
  recommended_tasks: RecommendedTask[]
  total_estimated_minutes: number
  actual_minutes_spent: number
  priority_level: string
  difficulty_level: string
  is_completed: boolean
  completion_percentage: number
  completed_tasks_count: number
  total_tasks_count: number
  actual_performance?: Record<string, any>
  status: string
  skip_reason?: string
  ai_feedback?: string
  effectiveness_rating?: number
  user_notes?: string
  created_at: string
  started_at?: string
  completed_at?: string
  updated_at: string
}

export interface TodayPlanResponse {
  plan?: DailyStudyPlan
  has_plan: boolean
  is_new: boolean
  message: string
  user_streak?: number
  total_study_time_this_week?: number
  goals_progress?: any[]
}

export interface CompletePlanData {
  actual_minutes_spent: number
  completed_tasks_count: number
  actual_performance?: Record<string, any>
  effectiveness_rating?: number
  user_notes?: string
}

class DailyPlanService {
  private baseUrl = '/plans'  // ✅ api.ts already has baseURL: '/api', proxy rewrites to '/api/v1'

  /**
   * ⭐ Get today's plan (most important!)
   * Auto-generates if not exists
   */
  async getTodayPlan(): Promise<TodayPlanResponse> {
    const response = await api.get<TodayPlanResponse>(`${this.baseUrl}/today`)
    return response.data
  }

  /**
   * Get plan for specific date
   */
  async getPlanByDate(date: string): Promise<DailyStudyPlan> {
    const response = await api.get<DailyStudyPlan>(`${this.baseUrl}/${date}`)
    return response.data
  }

  /**
   * Get plans with filters
   */
  async getPlans(params?: {
    start_date?: string
    end_date?: string
    status?: string
    skip?: number
    limit?: number
  }): Promise<DailyStudyPlan[]> {
    const response = await api.get<DailyStudyPlan[]>(this.baseUrl, { params })
    return response.data
  }

  /**
   * Start a plan
   */
  async startPlan(planId: number): Promise<DailyStudyPlan> {
    const response = await api.post<DailyStudyPlan>(`${this.baseUrl}/${planId}/start`)
    return response.data
  }

  /**
   * Complete a plan with performance data
   */
  async completePlan(planId: number, data: CompletePlanData): Promise<DailyStudyPlan> {
    const response = await api.post<DailyStudyPlan>(`${this.baseUrl}/${planId}/complete`, data)
    return response.data
  }

  /**
   * Skip a plan
   */
  async skipPlan(planId: number, skipReason?: string): Promise<DailyStudyPlan> {
    const response = await api.post<DailyStudyPlan>(
      `${this.baseUrl}/${planId}/skip`,
      null,
      { params: { skip_reason: skipReason } }
    )
    return response.data
  }

  /**
   * Get completion rate stats
   */
  async getCompletionRate(days: number = 7): Promise<{ completion_rate: number; days: number }> {
    const response = await api.get(`${this.baseUrl}/stats/completion-rate`, {
      params: { days }
    })
    return response.data
  }

  /**
   * Get adherence stats
   */
  async getAdherenceStats(days: number = 30): Promise<{
    total_plans: number
    completed: number
    skipped: number
    pending: number
    completion_rate: number
    avg_completion_percentage: number
    total_study_minutes: number
    avg_daily_minutes: number
  }> {
    const response = await api.get(`${this.baseUrl}/stats/adherence`, {
      params: { days }
    })
    return response.data
  }
}

export default new DailyPlanService()

