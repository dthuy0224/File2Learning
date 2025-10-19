// import { useState } from 'react'  // Will be used later
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'

import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import SocialLoginButton from '../components/SocialLoginButton'
import { authService, LoginRequest } from '../services/authService'
import { useAuthStore } from '../store/authStore'
import { BookOpen, Mail, Lock, Loader2 } from 'lucide-react'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  // const [isLoading, setIsLoading] = useState(false)  // Will be used later

  const { register, handleSubmit, formState: { errors } } = useForm<LoginRequest>()

  const loginMutation = useMutation({
    mutationFn: authService.login,
    onSuccess: async (tokenData) => {
      // Set token first (user data will be fetched later)
      login(tokenData.access_token, null as any)

      // Wait a bit for token to be persisted, then fetch user data
      setTimeout(async () => {
        try {
          const userData = await authService.fetchUser()
          login(tokenData.access_token, userData)
        } catch (fetchError: any) {
          console.warn('Could not fetch user data:', fetchError)
          // Continue with login even if user data fetch fails
        }
      }, 100)

      toast.success('Welcome back!')
      navigate('/dashboard')
    },
    onError: (error: any) => {
      console.error('Login error:', error)
      console.error('Error response:', error.response)
      console.error('Error status:', error.response?.status)
      console.error('Error data:', error.response?.data)

      if (error.response?.status === 400) {
        toast.error(error.response?.data?.detail || 'Invalid credentials')
      } else if (error.response?.status === 422) {
        toast.error('Invalid request format - please check your input')
      } else if (error.response?.status >= 500) {
        toast.error(`Server error (${error.response?.status}): Please try again later`)
      } else if (!error.response) {
        toast.error('Network error - please check your connection')
      } else {
        toast.error(`Login failed: ${error.response?.data?.detail || error.message || 'Please try again'}`)
      }
    }
  })

  const onSubmit = (data: LoginRequest) => {
    loginMutation.mutate(data)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center space-x-2">
            <BookOpen className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">AI Learning Material</span>
          </Link>
        </div>

        <Card className="shadow-xl border-0">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Welcome Back</CardTitle>
            <CardDescription>
              Sign in to continue your learning journey
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Social Login Buttons */}
            <div className="space-y-3 mb-6">
              <SocialLoginButton
                provider="google"
                onSuccess={(token, user) => {
                  login(token, user)
                  toast.success('Welcome back!')
                  navigate('/dashboard')
                }}
                onError={(error) => {
                  toast.error(`Google login failed: ${error}`)
                }}
                disabled={loginMutation.isPending}
              />

              <SocialLoginButton
                provider="microsoft"
                onSuccess={(token, user) => {
                  login(token, user)
                  toast.success('Welcome back!')
                  navigate('/dashboard')
                }}
                onError={(error) => {
                  toast.error(`Microsoft login failed: ${error}`)
                }}
                disabled={loginMutation.isPending}
              />

              <SocialLoginButton
                provider="github"
                onSuccess={(token, user) => {
                  login(token, user)
                  toast.success('Welcome back!')
                  navigate('/dashboard')
                }}
                onError={(error) => {
                  toast.error(`GitHub login failed: ${error}`)
                }}
                disabled={loginMutation.isPending}
              />
            </div>

            {/* Divider */}
            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">Or continue with</span>
              </div>
            </div>

            {/* Email/Password Form */}
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type="email"
                    placeholder="Enter your email"
                    className="pl-10"
                    {...register('username', {
                      required: 'Email is required',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Invalid email address'
                      }
                    })}
                  />
                </div>
                {errors.username && (
                  <p className="text-sm text-red-600">{errors.username.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type="password"
                    placeholder="Enter your password"
                    className="pl-10"
                    {...register('password', {
                      required: 'Password is required',
                      minLength: {
                        value: 6,
                        message: 'Password must be at least 6 characters'
                      }
                    })}
                  />
                </div>
                {errors.password && (
                  <p className="text-sm text-red-600">{errors.password.message}</p>
                )}
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={loginMutation.isPending}
              >
                {loginMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Don't have an account?{' '}
                <Link to="/register" className="text-blue-600 hover:underline font-medium">
                  Sign up here
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
