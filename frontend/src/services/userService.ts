import axios from 'axios'
import { User } from '../store/authStore'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  withCredentials: true,
})

// ✅ Thêm interceptor để tự động gửi token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const userService = {
  async getProfile(): Promise<User> {
    const res = await api.get('/users/me')
    return res.data
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const res = await api.put('/users/me', data)
    return res.data
  },

  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await api.post('/users/me/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
  },

  async uploadAvatar(file: File): Promise<User> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post('/users/me/upload-avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

  // ✅ Trả về object user đầy đủ
  return res.data;
},


  async updateLearningGoal(goal: string): Promise<User> {
    const res = await api.patch('/users/me/goal', { learning_goal: goal })
    return res.data
  },

  async updateStudyPreference(level: string, dailyTime: number): Promise<User> {
    const res = await api.patch('/users/me/study-preference', {
      difficulty_preference: level,
      daily_study_time: dailyTime,
    })
    return res.data
  },

  async getLearningStats(): Promise<any> {
    const res = await api.get('/analytics/learning-stats')
    return res.data
  },

  async deleteAccount(): Promise<void> {
    await api.delete('/users/me')
  },

  // 🚀 Reset password
  resetPassword: async (token: string, newPassword: string) => {
    return api.post('/auth/reset-password', { token, new_password: newPassword })
  }

}