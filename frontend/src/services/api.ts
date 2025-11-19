import axios from 'axios'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

// Create axios instance
export const api = axios.create({
  baseURL: '/api',  // Correct backend URL
  withCredentials: true,
})


// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('ai-learning-auth-token') || useAuthStore.getState().token
  // Don't add Authorization header to auth endpoints
  if (token && !config.url?.includes('/auth/')) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      useAuthStore.getState().logout()
      toast.error('Session expired. Please login again.')
    }
    // Temporarily disable 500+ error toast to see actual errors
    // else if (error.response?.status >= 500) {
    //   toast.error('Server error. Please try again later.')
    // }
    return Promise.reject(error)
  }
)

// ----- Notifications API -----
export const fetchNotifications = (userId: number) =>
  api.get(`/v1/notifications/${userId}`).then(res => res.data)

export const markNotificationAsRead = (notificationId: number) =>
  api.post(`/v1/notifications/${notificationId}/read`).then(res => res.data)

export const markAllNotificationsAsRead = (userId: number) =>
  api.post(`/v1/notifications/read-all/${userId}`).then(res => res.data)

export default api