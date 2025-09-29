import { Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { cn } from '../lib/utils'

interface ProgressIndicatorProps {
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress?: number
  message?: string
  error?: string
  className?: string
}

export default function ProgressIndicator({
  status,
  progress,
  message,
  error,
  className
}: ProgressIndicatorProps) {
  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'processing':
        return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-600" />
      default:
        return <Loader2 className="h-5 w-5 text-gray-600 animate-spin" />
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'processing':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'completed':
        return 'Completed'
      case 'processing':
        return 'Processing...'
      case 'failed':
        return 'Failed'
      default:
        return 'Pending...'
    }
  }

  return (
    <div className={cn(
      'flex items-center space-x-3 p-3 rounded-lg border',
      getStatusColor(),
      className
    )}>
      {getStatusIcon()}
      <div className="flex-1">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">{getStatusText()}</span>
          {progress !== undefined && (
            <span className="text-sm">{Math.round(progress)}%</span>
          )}
        </div>
        {message && (
          <p className="text-xs mt-1 opacity-80">{message}</p>
        )}
        {error && (
          <p className="text-xs mt-1 text-red-600">{error}</p>
        )}
        {status === 'processing' && progress !== undefined && (
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>
    </div>
  )
}
