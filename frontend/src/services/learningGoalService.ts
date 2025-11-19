/**
 * Learning Goal Service
 * API calls for managing learning goals
 */

import api from './api'

export interface LearningGoal {
  id: number
  user_id: number
  goal_type: string
  goal_title: string
  description?: string
  target_metrics: Record<string, any>
  current_progress?: Record<string, any>
  start_date: string
  target_date: string
  actual_completion_date?: string
  status: string
  priority: string
  is_on_track: boolean
  days_behind: number
  estimated_completion_date?: string
  completion_percentage: number
  milestones?: any[]
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface CreateLearningGoal {
  goal_type: string
  goal_title: string
  description?: string
  target_metrics: Record<string, any>
  start_date: string
  target_date: string
  priority?: string
}

export interface UpdateLearningGoal {
  goal_type?: string
  goal_title?: string
  description?: string
  target_metrics?: Record<string, any>
  start_date?: string
  target_date?: string
  priority?: string
  status?: string
  milestones?: any[]
}

class LearningGoalService {
  private baseUrl = '/goals'  // ✅ api.ts already has baseURL: '/api', proxy rewrites to '/api/v1'

  /**
   * Get all learning goals
   */
  async getGoals(status?: string): Promise<LearningGoal[]> {
    const params = status ? { status } : {}
    const response = await api.get<LearningGoal[]>(this.baseUrl, { params })
    return response.data
  }

  /**
   * Get active goals only
   */
  async getActiveGoals(): Promise<LearningGoal[]> {
    const response = await api.get<LearningGoal[]>(`${this.baseUrl}/active`)
    return response.data
  }

  /**
   * Get goals summary
   */
  async getGoalsSummary(): Promise<{
    total: number
    active: number
    completed: number
    paused: number
    on_track: number
    behind: number
  }> {
    const response = await api.get(`${this.baseUrl}/summary`)
    return response.data
  }

  /**
   * Get single goal by ID
   */
  async getGoal(goalId: number): Promise<LearningGoal> {
    const response = await api.get<LearningGoal>(`${this.baseUrl}/${goalId}`)
    return response.data
  }

  /**
   * Create new learning goal
   */
  async createGoal(goal: CreateLearningGoal): Promise<LearningGoal> {
    const response = await api.post<LearningGoal>(this.baseUrl, goal)
    return response.data
  }

  /**
   * Update learning goal
   */
  async updateGoal(goalId: number, updates: UpdateLearningGoal): Promise<LearningGoal> {
    const response = await api.put<LearningGoal>(`${this.baseUrl}/${goalId}`, updates)
    return response.data
  }

  /**
   * Delete learning goal
   */
  async deleteGoal(goalId: number): Promise<void> {
    await api.delete(`${this.baseUrl}/${goalId}`)
  }

  /**
   * Generate milestones for a goal
   */
  async generateMilestones(goalId: number): Promise<LearningGoal> {
    const response = await api.post<LearningGoal>(`${this.baseUrl}/${goalId}/generate-milestones`)
    return response.data
  }
}

export default new LearningGoalService()

