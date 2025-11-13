import api from './api';

// Types
export enum RecommendationType {
  REVIEW_FLASHCARD = 'review_flashcard',
  STUDY_TOPIC = 'study_topic',
  TAKE_QUIZ = 'take_quiz',
  READ_DOCUMENT = 'read_document',
  FOCUS_WEAK_AREA = 'focus_weak_area',
  REINFORCE_STRENGTH = 'reinforce_strength',
}

export enum RecommendationPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
}

export interface Recommendation {
  id: number;
  user_id: number;
  type: RecommendationType;
  priority: RecommendationPriority;
  title: string;
  description: string | null;
  reason: string | null;
  target_resource_type: string | null;
  target_resource_id: number | null;
  relevance_score: number;
  confidence_score: number;
  expected_impact: number;
  extra_data: Record<string, any> | null;
  expires_at: string | null;
  is_viewed: boolean;
  is_accepted: boolean;
  is_dismissed: boolean;
  viewed_at: string | null;
  accepted_at: string | null;
  dismissed_at: string | null;
  created_at: string;
  updated_at: string;
  is_expired: boolean;
  is_active: boolean;
}

export interface RecommendationListResponse {
  total: number;
  active_count: number;
  recommendations: Recommendation[];
}

export interface RecommendationStats {
  total_generated: number;
  active_recommendations: number;
  viewed_count: number;
  accepted_count: number;
  dismissed_count: number;
  expired_count: number;
  acceptance_rate: number;
  by_type: Record<string, number>;
  by_priority: Record<string, number>;
}

// Service functions
class RecommendationService {
  /**
   * Get all recommendations for the current user
   */
  async getRecommendations(params?: {
    skip?: number;
    limit?: number;
    active_only?: boolean;
    type_filter?: RecommendationType;
    priority_filter?: RecommendationPriority;
  }): Promise<RecommendationListResponse> {
    const response = await api.get('/recommendations', { params });
    return response.data;
  }

  /**
   * Get active recommendations (not dismissed/accepted/expired)
   */
  async getActiveRecommendations(limit: number = 10): Promise<Recommendation[]> {
    const response = await api.get('/recommendations/active', {
      params: { limit },
    });
    return response.data;
  }

  /**
   * Get recommendation statistics
   */
  async getStats(): Promise<RecommendationStats> {
    const response = await api.get('/recommendations/stats');
    return response.data;
  }

  /**
   * Generate new recommendations
   */
  async generateRecommendations(maxRecommendations: number = 10): Promise<{ message: string; count: number }> {
    const response = await api.post('/recommendations/generate', null, {
      params: { max_recommendations: maxRecommendations },
    });
    return response.data;
  }

  /**
   * Get a specific recommendation by ID
   */
  async getRecommendation(id: number): Promise<Recommendation> {
    const response = await api.get(`/recommendations/${id}`);
    return response.data;
  }

  /**
   * Mark recommendation as viewed
   */
  async markViewed(id: number): Promise<Recommendation> {
    const response = await api.put(`/recommendations/${id}/viewed`);
    return response.data;
  }

  /**
   * Mark recommendation as accepted (user acted on it)
   */
  async markAccepted(id: number): Promise<Recommendation> {
    const response = await api.put(`/recommendations/${id}/accepted`);
    return response.data;
  }

  /**
   * Mark recommendation as dismissed
   */
  async markDismissed(id: number): Promise<Recommendation> {
    const response = await api.put(`/recommendations/${id}/dismissed`);
    return response.data;
  }

  /**
   * Delete a recommendation
   */
  async deleteRecommendation(id: number): Promise<void> {
    await api.delete(`/recommendations/${id}`);
  }

  /**
   * Get icon and color for recommendation type
   */
  getTypeDisplay(type: RecommendationType): { icon: string; color: string; label: string } {
    const displays: Record<RecommendationType, { icon: string; color: string; label: string }> = {
      [RecommendationType.REVIEW_FLASHCARD]: {
        icon: '📇',
        color: 'blue',
        label: 'Review Flashcards',
      },
      [RecommendationType.STUDY_TOPIC]: {
        icon: '📚',
        color: 'purple',
        label: 'Study Topic',
      },
      [RecommendationType.TAKE_QUIZ]: {
        icon: '✍️',
        color: 'green',
        label: 'Take Quiz',
      },
      [RecommendationType.READ_DOCUMENT]: {
        icon: '📄',
        color: 'indigo',
        label: 'Read Document',
      },
      [RecommendationType.FOCUS_WEAK_AREA]: {
        icon: '🎯',
        color: 'red',
        label: 'Focus on Weak Area',
      },
      [RecommendationType.REINFORCE_STRENGTH]: {
        icon: '💪',
        color: 'yellow',
        label: 'Reinforce Strength',
      },
    };
    return displays[type];
  }

  /**
   * Get color for priority level
   */
  getPriorityColor(priority: RecommendationPriority): string {
    const colors: Record<RecommendationPriority, string> = {
      [RecommendationPriority.URGENT]: 'red',
      [RecommendationPriority.HIGH]: 'orange',
      [RecommendationPriority.MEDIUM]: 'yellow',
      [RecommendationPriority.LOW]: 'gray',
    };
    return colors[priority];
  }
}

export const recommendationService = new RecommendationService();
export default recommendationService;

