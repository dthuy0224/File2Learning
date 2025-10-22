import api from './api'
import { User } from '../store/authStore'

export interface LoginRequest {
  username: string // email (backend dùng "username" field)
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
  full_name?: string
  learning_goals?: string[]
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export const authService = {
  // 🚀 Login
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const params = new URLSearchParams()
    params.append('username', data.username)
    params.append('password', data.password)

    const response = await api.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      withCredentials: true,
    })
    return response.data
  },

  // 🚀 Register
  register: async (data: RegisterRequest): Promise<User> => {
    const response = await api.post('/users/', data)
    return response.data
  },

  // 🚀 Get current user
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/users/me', { withCredentials: true })
    return response.data
  },

  // 🚀 Test token
  testToken: async (): Promise<User> => {
    const response = await api.post('/auth/test-token')
    return response.data
  },

  // 🚀 Forgot password
forgotPassword: async (email: string) => {
  return api.post('/auth/forgot-password', { email })
},


  // 🚀 Reset password
  resetPassword: async (token: string, newPassword: string) => {
    const response = await api.post('/auth/reset-password', null, {
      params: { token, new_password: newPassword },
    })
    return response.data
  },

  // 🚀 Alias fetchUser
  fetchUser: async (): Promise<User> => {
    const response = await api.get('/users/me', { withCredentials: true })
    return response.data
  },


}

