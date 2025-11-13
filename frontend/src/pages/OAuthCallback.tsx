import { useEffect, useState, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { userService } from '../services/userService'
import toast from 'react-hot-toast'
import { Loader2 } from 'lucide-react'

export default function OAuthCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [, setIsProcessing] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const hasProcessed = useRef(false)

  useEffect(() => {
    // Prevent infinite loop - only process once
    if (hasProcessed.current) return

    const handleOAuthCallback = async () => {
      hasProcessed.current = true

      try {
        const errorParam = searchParams.get('error')

        // Check for errors from backend
        if (errorParam) {
          setError(`Authentication failed: ${errorParam}`)
          toast.error(`Authentication failed: ${errorParam}`)
          setTimeout(() => navigate('/login'), 3000)
          return
        }

        // Wait a bit for cookie to be set by browser after redirect
        await new Promise(resolve => setTimeout(resolve, 500))

        // Fetch user info using userService (which uses axios with credentials: 'include')
        // Retry up to 3 times in case cookie hasn't propagated yet
        let userData = null
        let retries = 3
        while (retries > 0 && !userData) {
          try {
            userData = await userService.getProfile()
            break
          } catch (err: any) {
            retries--
            if (retries > 0) {
              console.log(`Retrying user fetch... (${retries} attempts left)`)
              await new Promise(resolve => setTimeout(resolve, 500))
            } else {
              throw err
            }
          }
        }

        if (!userData) {
          throw new Error('Failed to get user data after retries')
        }

        // Login user into store (không cần token nữa vì cookie giữ token)
        login(null, userData)
        toast.success('Welcome! Successfully signed in.')

        // Redirect to dashboard
        navigate('/dashboard')

      } catch (err: any) {
        console.error('OAuth callback error:', err)
        setError(err.message || 'Authentication failed')
        toast.error(`Authentication failed: ${err.message || 'Unknown error'}`)
        setTimeout(() => navigate('/login'), 3000)
      } finally {
        setIsProcessing(false)
      }
    }

    handleOAuthCallback()
  }, [searchParams, navigate, login])

if (error) {
return ( <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-red-50 flex items-center justify-center p-6"> <div className="w-full max-w-md"> <div className="text-center"> <div className="mb-6"> <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4"> <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"> <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /> </svg> </div> <h1 className="text-2xl font-bold text-gray-900 mb-2">Authentication Failed</h1> <p className="text-gray-600">{error}</p> </div> <p className="text-sm text-gray-500">
You will be redirected to the login page in a few seconds... </p> </div> </div> </div>
)
}

return ( <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-6"> <div className="w-full max-w-md"> <div className="text-center"> <div className="mb-6"> <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4"> <Loader2 className="w-8 h-8 text-blue-600 animate-spin" /> </div> <h1 className="text-2xl font-bold text-gray-900 mb-2">Completing Sign In</h1> <p className="text-gray-600">Please wait while we finish setting up your account...</p> </div> </div> </div> </div>
)
}
