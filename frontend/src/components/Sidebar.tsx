import { Link, useLocation } from 'react-router-dom'
import { cn } from '../lib/utils'
import { 
  LayoutDashboard, 
  FileText, 
  CreditCard, 
  Brain,
  BarChart3,
  Calendar,
  Target,
  Sparkles
} from 'lucide-react'
import { LucideIcon } from 'lucide-react'

type NavigationItem = {
  name: string
  href: string
  icon: LucideIcon
  badge?: string
}

const navigation: NavigationItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'Learning Goals',
    href: '/learning-goals',
    icon: Target,
  },
  {
    name: 'Recommendations',
    href: '/recommendations',
    icon: Sparkles,
  },
  {
    name: 'Study Plan',
    href: '/study-schedule',
    icon: Calendar,
  },
  {
    name: 'Documents',
    href: '/documents',
    icon: FileText,
  },
  {
    name: 'Flashcards',
    href: '/flashcards',
    icon: CreditCard,
  },
  {
    name: 'Quizzes',
    href: '/quizzes',
    icon: Brain,
  },
  {
    name: 'Progress',
    href: '/progress',
    icon: BarChart3,
  },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-[calc(100vh-73px)]">
      <nav className="p-4">
        <ul className="space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <li key={item.name}>
                <Link
                  to={item.href}
                  className={cn(
                    'flex items-center justify-between px-4 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                  )}
                >
                  <div className="flex items-center">
                    <item.icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </div>
                  {'badge' in item && item.badge && (
                    <span className="px-2 py-0.5 text-[10px] font-bold bg-green-500 text-white rounded-full">
                      {item.badge}
                    </span>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
    </aside>
  )
}
