import api from './api'
import { User } from '../store/authStore'

export interface LoginRequest {
  username: string  // email
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
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)

    const response = await api.post('/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  register: async (data: RegisterRequest): Promise<User> => {
    const response = await api.post('/v1/users/', data)
    return response.data
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/v1/users/me')
    return response.data
  },

  testToken: async (): Promise<User> => {
    const response = await api.post('/v1/auth/test-token')
    return response.data
  },

  fetchUser: async (): Promise<User> => {
    const response = await api.get('/v1/users/me')
    return response.data
  },
}
