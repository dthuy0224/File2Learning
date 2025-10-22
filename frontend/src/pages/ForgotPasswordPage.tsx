import { useForm } from 'react-hook-form'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'

import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Mail, Loader2 } from 'lucide-react'
import { authService } from '../services/authService'

interface ForgotPasswordForm {
  email: string
}

export default function ForgotPasswordPage() {
  const navigate = useNavigate()
  const { register, handleSubmit, formState: { errors } } = useForm<ForgotPasswordForm>()

  const forgotPasswordMutation = useMutation({
    mutationFn: (data: ForgotPasswordForm) => authService.forgotPassword(data.email),
    onSuccess: () => {
      toast.success('Password reset link sent! Check your email.')
      navigate('/login')
    },
    onError: (error: any) => {
  console.error('Forgot password error:', error)

  let errMsg = 'Failed to send reset link'

  const data = error.response?.data

  if (typeof data === 'string') {
    errMsg = data
  } else if (Array.isArray(data)) {
    // FastAPI validation errors
    errMsg = data[0]?.msg || errMsg
  } else if (data?.detail) {
    if (typeof data.detail === 'string') {
      errMsg = data.detail
    } else if (Array.isArray(data.detail)) {
      errMsg = data.detail[0]?.msg || errMsg
    }
  }

  toast.error(errMsg)
}

  })

  const onSubmit = (data: ForgotPasswordForm) => {
    forgotPasswordMutation.mutate(data)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <Card className="shadow-xl border-0">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Forgot Password</CardTitle>
            <CardDescription>
              Enter your email to receive a password reset link
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type="email"
                    placeholder="Enter your email"
                    className="pl-10"
                    {...register('email', {
                      required: 'Email is required',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Invalid email address'
                      }
                    })}
                  />
                </div>
                {errors.email && (
                  <p className="text-sm text-red-600">{errors.email.message}</p>
                )}
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={forgotPasswordMutation.isPending}
              >
                {forgotPasswordMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Sending...
                  </>
                ) : (
                  'Send Reset Link'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Remembered your password?{' '}
                <span
                  className="text-blue-600 hover:underline cursor-pointer"
                  onClick={() => navigate('/login')}
                >
                  Back to login
                </span>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
