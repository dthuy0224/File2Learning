import { useEffect, useState, useRef } from "react"
import { Navigate, useLocation } from "react-router-dom"
import { useAuthStore } from "../store/authStore"

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, login, token, fetchUser } = useAuthStore()
  const [checking, setChecking] = useState(true)
  const location = useLocation()
  const hasChecked = useRef(false)

  useEffect(() => {
    // Prevent infinite loop - only check once
    if (hasChecked.current) {
      setChecking(false)
      return
    }

    const checkAuth = async () => {
      hasChecked.current = true
      
      // If no user but has token → fetch again
      if (!user && token) {
        try {
          await fetchUser()
        } catch (err) {
          console.error("Auth check failed:", err)
        }
      } else if (!user) {
        // Try cookie-based login fallback
        try {
          const res = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/users/me`, {
            method: "GET",
            credentials: "include",
          })
          if (res.ok) {
            const userData = await res.json()
            await login(null, userData)
          }
        } catch (err) {
          console.error("Cookie auth failed:", err)
        }
      }
      setChecking(false)
    }
    checkAuth()
  }, [user, token])

  // Display while checking
  if (checking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Loading...</p>
      </div>
    )
  }

  // If not logged in → redirect to login page
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // If user needs setup → redirect to setup-learning page
  if (user.needs_setup && location.pathname !== "/setup-learning") {
    return <Navigate to="/setup-learning" replace />
  }

  // If user already setup but still on setup-learning page → redirect to dashboard
  if (!user.needs_setup && location.pathname === "/setup-learning") {
    return <Navigate to="/dashboard" replace />
  }

  // Allow rendering protected content
  return <>{children}</>
}
