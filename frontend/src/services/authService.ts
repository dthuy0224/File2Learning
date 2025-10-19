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
    console.log('Login attempt:', { username: data.username, hasPassword: !!data.password })

    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)

    console.log('Form data:', formData.toString())

    try {
      const response = await api.post('/v1/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })
      console.log('Login success:', response.status, response.data)
      return response.data
    } catch (error: any) {
      console.error('Login error details:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
        config: error.config
      })
      throw error
    }
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
