import { useState, useEffect } from 'react'
import AIService, { DocumentStatus } from '../services/aiService'

export function useDocumentStatus(documentId: number) {
  const [status, setStatus] = useState<DocumentStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchStatus = async () => {
    try {
      setLoading(true)
      setError(null)
      const statusData = await AIService.getDocumentStatus(documentId)
      setStatus(statusData)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch document status')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()

    // Poll for status updates every 2 seconds if processing
    const interval = setInterval(() => {
      if (status?.status === 'processing') {
        fetchStatus()
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [documentId, status?.status])

  return {
    status,
    loading,
    error,
    refetch: fetchStatus
  }
}
