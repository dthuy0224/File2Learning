import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { useAuthStore } from '../store/authStore'
import { BookOpen, FileText, CreditCard, Brain, TrendingUp } from 'lucide-react'

export default function DashboardPage() {
  const { user } = useAuthStore()

  const stats = [
    {
      title: 'Documents',
      value: '12',
      description: 'Documents processed',
      icon: FileText,
      color: 'text-blue-600',
      bg: 'bg-blue-50'
    },
    {
      title: 'Flashcards',
      value: '248',
      description: 'Cards created',
      icon: CreditCard,
      color: 'text-green-600',
      bg: 'bg-green-50'
    },
    {
      title: 'Quizzes',
      value: '18',
      description: 'Quizzes completed',
      icon: Brain,
      color: 'text-purple-600',
      bg: 'bg-purple-50'
    },
    {
      title: 'Progress',
      value: '78%',
      description: 'Overall accuracy',
      icon: TrendingUp,
      color: 'text-orange-600',
      bg: 'bg-orange-50'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-blue-100 rounded-full">
            <BookOpen className="h-8 w-8 text-blue-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back, {user?.full_name || user?.username}! 👋
            </h1>
            <p className="text-gray-600 mt-1">
              Ready to continue your English learning journey?
            </p>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className={`p-2 rounded-lg ${stat.bg}`}>
                  <stat.icon className={`h-5 w-5 ${stat.color}`} />
                </div>
                <span className="text-2xl font-bold text-gray-900">{stat.value}</span>
              </div>
            </CardHeader>
            <CardContent>
              <CardTitle className="text-sm font-medium text-gray-600">
                {stat.title}
              </CardTitle>
              <CardDescription className="mt-1">
                {stat.description}
              </CardDescription>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest learning activities</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Completed "Business English" quiz</p>
                  <p className="text-xs text-gray-500">2 hours ago</p>
                </div>
                <span className="text-sm font-semibold text-green-600">92%</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Reviewed 15 flashcards</p>
                  <p className="text-xs text-gray-500">5 hours ago</p>
                </div>
                <span className="text-sm font-semibold text-blue-600">15/15</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Uploaded "IELTS Reading" document</p>
                  <p className="text-xs text-gray-500">1 day ago</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Learning Goals</CardTitle>
            <CardDescription>Your current learning objectives</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {user?.learning_goals?.map((goal, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                    <span className="text-sm font-medium capitalize">{goal}</span>
                  </div>
                  <span className="text-xs text-gray-500">In Progress</span>
                </div>
              )) || (
                <p className="text-sm text-gray-500">No learning goals set</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
