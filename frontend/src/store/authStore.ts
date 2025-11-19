import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { userService } from '@/services/userService'

export interface User {
  needs_setup: any
  id: number
  email: string
  username: string
  full_name?: string
  learning_goals: string[]
  difficulty_preference: string
  daily_study_time: number
  oauth_avatar?: string
  created_at?: string
}

interface AuthState {
  token: string | null
  user: User | null
  isLoading: boolean

  // Actions
  login: (token: string | null, user?: User | null) => Promise<void>
  logout: () => void
  updateUser: (user: Partial<User>) => void
  setLoading: (loading: boolean) => void
  reset: () => void
  fetchUser: () => Promise<void> // Added
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isLoading: false,

      // When login → set token and fetch user from backend
    login: async (token: string | null, user: User | null = null) => {
  if (token) {
    localStorage.setItem('ai-learning-auth-token', token) // Save directly
  } else {
    localStorage.removeItem('ai-learning-auth-token')
  }

  set({ token, isLoading: true })

  try {
    if (!user) {
      await get().fetchUser()
    } else {
      set({ user })
    }
  } finally {
    set({ isLoading: false })
  }
},


      logout: () => {
        set({ token: null, user: null, isLoading: false })
        localStorage.removeItem('ai-learning-auth')
      },

      updateUser: (user: Partial<User>) => {
  set((state) => ({
    ...state,
    user: state.user ? { ...state.user, ...user } : (user as User),
  }))
},

      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      },

      reset: () => {
        set({ token: null, user: null, isLoading: false })
      },

      // Sync user data from backend
      fetchUser: async () => {
        try {
          const data = await userService.getProfile()
          if (data?.email) set({ user: data })
        } catch (error) {
          console.error('Failed to fetch user:', error)
        }
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
