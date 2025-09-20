import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  learning_goals: string[]
  difficulty_preference: string
  daily_study_time: number
}

interface AuthState {
  token: string | null
  user: User | null
  isLoading: boolean
  login: (token: string, user: User) => void
  logout: () => void
  updateUser: (user: User) => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isLoading: false,
      
      login: (token: string, user: User) => {
        set({ token, user, isLoading: false })
      },
      
      logout: () => {
        set({ token: null, user: null, isLoading: false })
      },
      
      updateUser: (user: User) => {
        set({ user })
      },
      
      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      },
    }),
    {
      name: 'ai-learning-auth',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
      }),
    }
  )
)
