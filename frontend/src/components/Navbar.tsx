import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Button } from './ui/button'
import { BookOpen, User, LogOut } from 'lucide-react'

export default function Navbar() {
  const { user, logout } = useAuthStore()

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex justify-between items-center">
        <Link to="/dashboard" className="flex items-center space-x-2">
          <BookOpen className="h-8 w-8 text-primary" />
          <span className="text-xl font-bold text-gray-900">
            File2Learning
          </span>
        </Link>

        <Link to="/profile" className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <User className="h-5 w-5 text-gray-600" />
            <span className="text-sm text-gray-700">
              {user?.full_name || user?.username}
            </span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={logout}
            className="flex items-center space-x-2"
          >
            <LogOut className="h-4 w-4" />
            <span>Logout</span>
          </Button>
        </Link>
      </div>
    </nav>
  )
}
