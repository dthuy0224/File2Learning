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
      
      // ✅ Nếu chưa có user mà có token → fetch lại
      if (!user && token) {
        try {
          await fetchUser()
        } catch (err) {
          console.error("Auth check failed:", err)
        }
      } else if (!user) {
        // ✅ Thử check cookie-based login fallback
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

  // 🔄 Hiển thị khi đang kiểm tra
  if (checking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Loading...</p>
      </div>
    )
  }

  // 🔐 Nếu chưa đăng nhập → về trang login
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // ⚙️ Nếu user cần setup → ép sang trang setup-learning
  if (user.needs_setup && location.pathname !== "/setup-learning") {
    return <Navigate to="/setup-learning" replace />
  }

  // ✅ Nếu user đã setup mà vẫn ở trang setup-learning → đẩy sang dashboard
  if (!user.needs_setup && location.pathname === "/setup-learning") {
    return <Navigate to="/dashboard" replace />
  }

  // ✅ Cho phép render nội dung bảo vệ
  return <>{children}</>
}
