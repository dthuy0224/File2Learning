import { useSearchParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'

import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Lock, Loader2 } from 'lucide-react'
import { authService } from '../services/authService'

interface ResetPasswordForm {
  new_password: string
  confirm_password: string
}

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token') || ''

  const { register, handleSubmit, watch, formState: { errors } } = useForm<ResetPasswordForm>()

  const resetPasswordMutation = useMutation({
    mutationFn: (data: ResetPasswordForm) =>
      authService.resetPassword(token, data.new_password),
    onSuccess: () => {
      toast.success('Password reset successfully! You can now log in.')
      navigate('/login')
    },
    onError: (error: any) => {
      console.error('Reset password error:', error)
      toast.error(error.response?.data?.detail || 'Failed to reset password')
    }
  })

  const onSubmit = (data: ResetPasswordForm) => {
    if (data.new_password !== data.confirm_password) {
      toast.error('Passwords do not match')
      return
    }
    resetPasswordMutation.mutate(data)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <Card className="shadow-xl border-0">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Reset Password</CardTitle>
            <CardDescription>
              Enter your new password below
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">New Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type="password"
                    placeholder="Enter new password"
                    className="pl-10"
                    {...register('new_password', {
                      required: 'New password is required',
                      minLength: { value: 6, message: 'Password must be at least 6 characters' }
                    })}
                  />
                </div>
                {errors.new_password && (
                  <p className="text-sm text-red-600">{errors.new_password.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type="password"
                    placeholder="Confirm new password"
                    className="pl-10"
                    {...register('confirm_password', {
                      required: 'Please confirm your password'
                    })}
                  />
                </div>
                {errors.confirm_password && (
                  <p className="text-sm text-red-600">{errors.confirm_password.message}</p>
                )}
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={resetPasswordMutation.isPending}
              >
                {resetPasswordMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Resetting...
                  </>
                ) : (
                  'Reset Password'
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
