import { useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { useAuthStore } from "../store/authStore"
import { BookOpen, FileText, CreditCard, Brain, TrendingUp, Loader2, Target, Calendar, Clock, ArrowRight, Sparkles } from "lucide-react"
import { useUserStats } from "../hooks/useProgress"
import { useRecentActivities } from "../hooks/useProgress"
import dailyPlanService from "../services/dailyPlanService"
import recommendationService from "../services/recommendationService"

export default function DashboardPage() {
  const { user } = useAuthStore()
  const navigate = useNavigate()

  // Use React Query hooks to get real data
  const { data: userStats, isLoading: statsLoading } = useUserStats(30)
  const { data: recentActivities = [] } = useRecentActivities(5)
  
  // ⭐ NEW: Fetch today's plan
  const { data: todayPlan } = useQuery({
    queryKey: ['todayPlan'],
    queryFn: () => dailyPlanService.getTodayPlan(),
    refetchOnWindowFocus: false
  })

  // ⭐ NEW: Fetch active recommendations
  const { data: recommendations = [] } = useQuery({
    queryKey: ['activeRecommendations'],
    queryFn: () => recommendationService.getActiveRecommendations(3),
    refetchOnWindowFocus: false
  })

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
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Today's Study Plan 📚</CardTitle>
                <CardDescription>Your personalized plan for today</CardDescription>
              </div>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => navigate('/today-plan')}
              >
                View Full <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {todayPlan?.has_plan && todayPlan.plan ? (
              <div className="space-y-4">
                {/* Summary */}
                <div className="bg-blue-50 rounded-lg p-3">
                  <p className="text-sm text-gray-700">
                    {todayPlan.plan.plan_summary || 'Your plan is ready!'}
                  </p>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="bg-gray-50 rounded p-2">
                    <Target className="h-4 w-4 mx-auto text-gray-400 mb-1" />
                    <p className="text-xs text-gray-600">Tasks</p>
                    <p className="text-sm font-bold">{todayPlan.plan.total_tasks_count}</p>
                  </div>
                  <div className="bg-gray-50 rounded p-2">
                    <Clock className="h-4 w-4 mx-auto text-gray-400 mb-1" />
                    <p className="text-xs text-gray-600">Time</p>
                    <p className="text-sm font-bold">{todayPlan.plan.total_estimated_minutes}m</p>
                  </div>
                  <div className="bg-gray-50 rounded p-2">
                    <TrendingUp className="h-4 w-4 mx-auto text-gray-400 mb-1" />
                    <p className="text-xs text-gray-600">Progress</p>
                    <p className="text-sm font-bold">{Number(todayPlan.plan.completion_percentage).toFixed(0)}%</p>
                  </div>
                </div>

                {/* Action Button */}
                {todayPlan.plan.status === 'pending' && (
                  <Button
                    className="w-full"
                    onClick={() => navigate('/today-plan')}
                  >
                    Start Today's Plan 🚀
                  </Button>
                )}
                {todayPlan.plan.status === 'in_progress' && (
                  <Button
                    className="w-full"
                    variant="outline"
                    onClick={() => navigate('/today-plan')}
                  >
                    Continue Plan ({todayPlan.plan.completed_tasks_count}/{todayPlan.plan.total_tasks_count} done)
                  </Button>
                )}
                {todayPlan.plan.status === 'completed' && (
                  <div className="bg-green-50 rounded-lg p-3 text-center">
                    <p className="text-sm text-green-700 font-medium">
                      ✅ Today's plan completed! Great job!
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-6">
                <Calendar className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-sm text-gray-500 mb-3">No plan for today yet</p>
                <Button size="sm" onClick={() => navigate('/today-plan')}>
                  Generate Plan
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recommendations Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-indigo-600" />
                  Smart Recommendations
                </CardTitle>
                <CardDescription>Personalized suggestions for you</CardDescription>
              </div>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => navigate('/recommendations')}
              >
                View All <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {recommendations.length > 0 ? (
              <div className="space-y-3">
                {recommendations.map((rec) => {
                  const typeDisplay = recommendationService.getTypeDisplay(rec.type);
                  const priorityColor = recommendationService.getPriorityColor(rec.priority);
                  
                  return (
                    <div
                      key={rec.id}
                      className={`p-3 rounded-lg border-l-4 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors border-${priorityColor}-500`}
                      onClick={() => navigate('/recommendations')}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-lg">{typeDisplay.icon}</span>
                            <h4 className="text-sm font-semibold text-gray-900">{rec.title}</h4>
                          </div>
                          {rec.description && (
                            <p className="text-xs text-gray-600 line-clamp-2">{rec.description}</p>
                          )}
                        </div>
                        <span className={`ml-2 px-2 py-1 text-xs font-semibold rounded bg-${priorityColor}-100 text-${priorityColor}-800`}>
                          {rec.priority}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-6">
                <Sparkles className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-sm text-gray-500 mb-3">No recommendations available</p>
                <Button size="sm" onClick={() => navigate('/recommendations')}>
                  Generate Recommendations
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
