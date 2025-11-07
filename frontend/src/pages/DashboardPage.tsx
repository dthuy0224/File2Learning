import { useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { useAuthStore } from "../store/authStore"
import { BookOpen, FileText, CreditCard, Brain, TrendingUp, Loader2 } from "lucide-react"
import { useUserStats } from "../hooks/useProgress"
import { useRecentActivities } from "../hooks/useProgress"

export default function DashboardPage() {
  const { user } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    if (!user?.learning_goals || user.learning_goals.length === 0) {
      navigate("/setup-learning")
    }
  }, [user, navigate])

  // Use React Query hooks to get real data
  const { data: userStats, isLoading: statsLoading } = useUserStats(30)
  const { data: recentActivities = [] } = useRecentActivities(5)

  // Transform user stats into dashboard format
  const stats = [
    {
      title: "Documents",
      value: userStats?.documents_processed?.toString() || "0",
      description: "Documents processed",
      icon: FileText,
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
    {
      title: "Flashcards",
      value: userStats?.words_mastered?.toString() || "0",
      description: "Cards mastered",
      icon: CreditCard,
      color: "text-green-600",
      bg: "bg-green-50",
    },
    {
      title: "Quizzes",
      value: userStats?.total_quizzes_completed?.toString() || "0",
      description: "Quizzes completed",
      icon: Brain,
      color: "text-purple-600",
      bg: "bg-purple-50",
    },
    {
      title: "Progress",
      value: `${userStats?.avg_accuracy?.toFixed(0) || "0"}%`,
      description: "Overall accuracy",
      icon: TrendingUp,
      color: "text-orange-600",
      bg: "bg-orange-50",
    },
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
        {statsLoading ? (
          <div className="col-span-full flex justify-center items-center py-12">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        ) : (
          stats.map((stat, index) => (
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
          ))
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest learning activities</CardDescription>
          </CardHeader>
          <CardContent>
            {recentActivities.length > 0 ? (
              <div className="space-y-4">
                {recentActivities.slice(0, 5).map((activity) => {
                  const getActivityColor = (type: string) => {
                    switch (type) {
                      case 'quiz': return 'bg-blue-500'
                      case 'flashcard': return 'bg-green-500'
                      case 'document': return 'bg-purple-500'
                      default: return 'bg-gray-500'
                    }
                  }

                  const getScoreDisplay = (activity: any) => {
                    if (activity.type === 'quiz' && activity.score) {
                      return <span className="text-sm font-semibold text-green-600">{activity.score}</span>
                    } else if (activity.type === 'flashcard') {
                      return <span className="text-sm font-semibold text-blue-600">Reviewed</span>
                    }
                    return null
                  }

                  return (
                    <div key={activity.id} className="flex items-center space-x-3">
                      <div className={`w-2 h-2 rounded-full ${getActivityColor(activity.type)}`}></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{activity.title}</p>
                        <p className="text-xs text-gray-500">{activity.time_ago}</p>
                      </div>
                      {getScoreDisplay(activity)}
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-4">
                <p className="text-sm">No recent activities</p>
                <p className="text-xs">Start learning to see your activities here</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Learning Goals</CardTitle>
            <CardDescription>Your current learning objectives</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {user?.learning_goals?.length ? (
                user.learning_goals.map((goal, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                      <span className="text-sm font-medium capitalize">{goal}</span>
                    </div>
                    <span className="text-xs text-gray-500">In Progress</span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">No learning goals set</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
