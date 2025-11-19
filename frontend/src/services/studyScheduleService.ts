/**
 * Study Schedule Service
 * API calls for study schedules (Thời Khóa Biểu)
 */

import api from './api'

export interface ScheduleConfig {
  daily_minutes: number
  days_per_week: number
  preferred_times?: string[]
  activity_distribution?: Record<string, number>
  difficulty_curve?: string
  focus_areas?: string[]
}

export interface Milestone {
  week: number
  target: string
  status: 'pending' | 'in_progress' | 'completed'
  completed_date?: string
}

export interface StudySchedule {
  id: number
  user_id: number
  goal_id?: number
  schedule_name: string
  schedule_type: 'goal_based' | 'time_based' | 'exam_prep' | 'maintenance' | 'custom'
  schedule_config: ScheduleConfig
  milestones?: Milestone[]
  adaptation_mode: 'strict' | 'moderate' | 'flexible' | 'highly_adaptive'
  max_daily_load: number
  min_daily_load: number
  catch_up_strategy: 'skip' | 'gradual' | 'intensive'
  is_active: boolean
  effectiveness_score?: number
  total_days_scheduled: number
  days_completed: number
  days_missed: number
  days_partially_completed: number
  avg_adherence_rate: number
  last_adjusted_at?: string
  adjustment_reason?: string
  adjustment_count: number
  created_at: string
  updated_at: string
  deactivated_at?: string
}

export interface StudyScheduleCreate {
  schedule_name: string
  schedule_type: 'goal_based' | 'time_based' | 'exam_prep' | 'maintenance' | 'custom'
  schedule_config: ScheduleConfig
  goal_id?: number
  milestones?: Milestone[]
  adaptation_mode?: 'strict' | 'moderate' | 'flexible' | 'highly_adaptive'
  max_daily_load?: number
  min_daily_load?: number
  catch_up_strategy?: 'skip' | 'gradual' | 'intensive'
}

export interface StudyScheduleUpdate {
  schedule_name?: string
  schedule_type?: 'goal_based' | 'time_based' | 'exam_prep' | 'maintenance' | 'custom'
  schedule_config?: ScheduleConfig
  goal_id?: number
  milestones?: Milestone[]
  adaptation_mode?: 'strict' | 'moderate' | 'flexible' | 'highly_adaptive'
  max_daily_load?: number
  min_daily_load?: number
  catch_up_strategy?: 'skip' | 'gradual' | 'intensive'
  is_active?: boolean
}

class StudyScheduleService {
  private baseUrl = '/schedules'

  /**
   * Get all study schedules
   */
  async getSchedules(params?: {
    active_only?: boolean
    goal_id?: number
    skip?: number
    limit?: number
  }): Promise<StudySchedule[]> {
    const response = await api.get<StudySchedule[]>(this.baseUrl, { params })
    return response.data
  }

  /**
   * Get active study schedule
   */
  async getActiveSchedule(): Promise<StudySchedule> {
    const response = await api.get<StudySchedule>(`${this.baseUrl}/active`)
    return response.data
  }

  /**
   * Get schedule by ID
   */
  async getSchedule(scheduleId: number): Promise<StudySchedule> {
    const response = await api.get<StudySchedule>(`${this.baseUrl}/${scheduleId}`)
    return response.data
  }

  /**
   * Create new study schedule
   */
  async createSchedule(schedule: StudyScheduleCreate): Promise<StudySchedule> {
    const response = await api.post<StudySchedule>(this.baseUrl, schedule)
    return response.data
  }

  /**
   * Update study schedule
   */
  async updateSchedule(
    scheduleId: number,
    update: StudyScheduleUpdate
  ): Promise<StudySchedule> {
    const response = await api.put<StudySchedule>(
      `${this.baseUrl}/${scheduleId}`,
      update
    )
    return response.data
  }

  /**
   * Activate schedule (deactivates other active schedules)
   */
  async activateSchedule(scheduleId: number): Promise<StudySchedule> {
    const response = await api.post<StudySchedule>(
      `${this.baseUrl}/${scheduleId}/activate`
    )
    return response.data
  }

  /**
   * Deactivate schedule
   */
  async deactivateSchedule(scheduleId: number): Promise<StudySchedule> {
    const response = await api.post<StudySchedule>(
      `${this.baseUrl}/${scheduleId}/deactivate`
    )
    return response.data
  }

  /**
   * Delete schedule
   */
  async deleteSchedule(scheduleId: number): Promise<void> {
    await api.delete(`${this.baseUrl}/${scheduleId}`)
  }

  /**
   * Get plans for a schedule
   */
  async getSchedulePlans(
    scheduleId: number,
    params?: {
      start_date?: string
      end_date?: string
    }
  ) {
    const response = await api.get(`${this.baseUrl}/${scheduleId}/plans`, { params })
    return response.data
  }

  /**
   * Get upcoming plans for a schedule
   */
  async getUpcomingPlans(scheduleId: number, days: number = 7) {
    const response = await api.get(`${this.baseUrl}/${scheduleId}/upcoming`, {
      params: { days }
    })
    return response.data
  }

  /**
   * Update schedule statistics
   */
  async updateStats(scheduleId: number): Promise<StudySchedule> {
    const response = await api.post<StudySchedule>(
      `${this.baseUrl}/${scheduleId}/update-stats`
    )
    return response.data
  }

  /**
   * Adjust schedule automatically based on performance
   */
  async adjustSchedule(scheduleId: number): Promise<{
    adjusted: boolean
    reason?: string
    adjustment?: any
    analysis?: any
    schedule?: StudySchedule
  }> {
    const response = await api.post(`${this.baseUrl}/${scheduleId}/adjust`)
    return response.data
  }
}

export default new StudyScheduleService()

