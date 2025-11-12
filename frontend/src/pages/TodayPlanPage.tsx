import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { 
  CheckCircle2, Clock, Play, SkipForward, 
  Star, Target, BookOpen, Brain, CreditCard
} from 'lucide-react'
import { toast } from 'react-hot-toast'
import dailyPlanService, { CompletePlanData } from '@/services/dailyPlanService'

// Helper function (instead of date-fns)
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  })
}

export default function TodayPlanPage() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [isCompleteDialogOpen, setIsCompleteDialogOpen] = useState(false)
  const [completionData, setCompletionData] = useState<Partial<CompletePlanData>>({})

  // Fetch today's plan
  const { data: todayPlan, isLoading } = useQuery({
    queryKey: ['todayPlan'],
    queryFn: () => dailyPlanService.getTodayPlan(),
    refetchOnWindowFocus: false
  })

  // Start plan mutation
  const startMutation = useMutation({
    mutationFn: (planId: number) => dailyPlanService.startPlan(planId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todayPlan'] })
      toast.success('Plan started! Good luck! 💪')
    }
  })

  // Complete plan mutation
  const completeMutation = useMutation({
    mutationFn: ({ planId, data }: { planId: number; data: CompletePlanData }) =>
      dailyPlanService.completePlan(planId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todayPlan'] })
      queryClient.invalidateQueries({ queryKey: ['userStats'] })
      toast.success('Awesome! Plan completed! 🎉')
      setIsCompleteDialogOpen(false)
      setCompletionData({})
    }
  })

  // Skip plan mutation
  const skipMutation = useMutation({
    mutationFn: ({ planId, reason }: { planId: number; reason?: string }) =>
      dailyPlanService.skipPlan(planId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todayPlan'] })
      toast.success('Plan skipped')
    }
  })

  const handleStartPlan = () => {
    if (todayPlan?.plan) {
      startMutation.mutate(todayPlan.plan.id)
    }
  }

  const handleCompletePlan = () => {
    if (!todayPlan?.plan) return

    if (!completionData.actual_minutes_spent || !completionData.completed_tasks_count) {
      toast.error('Please fill in time spent and tasks completed')
      return
    }

    completeMutation.mutate({
      planId: todayPlan.plan.id,
      data: completionData as CompletePlanData
    })
  }

  const handleSkipPlan = () => {
    if (!todayPlan?.plan) return

    const reason = prompt('Why are you skipping today? (optional)')
    skipMutation.mutate({
      planId: todayPlan.plan.id,
      reason: reason || undefined
    })
  }

  const getTaskIcon = (type: string) => {
    switch (type) {
      case 'flashcard_review': return CreditCard
      case 'quiz': return Brain
      case 'document_reading': return BookOpen
      default: return Target
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-600 bg-red-50'
      case 'high': return 'text-orange-600 bg-orange-50'
      case 'normal': return 'text-blue-600 bg-blue-50'
      case 'low': return 'text-gray-600 bg-gray-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Loading today's plan...</p>
      </div>
    )
  }

  if (!todayPlan?.has_plan || !todayPlan.plan) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>No Plan for Today</CardTitle>
            <CardDescription>
              Unable to generate a plan. Try uploading documents or creating flashcards first.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => navigate('/documents')}>
              Go to Documents
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const plan = todayPlan.plan
  const isCompleted = plan.status === 'completed'
  const isInProgress = plan.status === 'in_progress'
  const isPending = plan.status === 'pending'

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Today's Study Plan 📚</h1>
            <p className="text-blue-100">{formatDate(plan.plan_date)}</p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">{plan.total_estimated_minutes}</div>
            <div className="text-sm text-blue-100">minutes</div>
          </div>
        </div>
      </div>

      {/* New Plan Notice */}
      {todayPlan.is_new && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <p className="text-green-800 font-medium">✨ {todayPlan.message}</p>
          </CardContent>
        </Card>
      )}

      {/* AI Summary */}
      {plan.plan_summary && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700">{plan.plan_summary}</p>
          </CardContent>
        </Card>
      )}

      {/* Plan Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Status</CardTitle>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              isCompleted ? 'bg-green-100 text-green-800' :
              isInProgress ? 'bg-blue-100 text-blue-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {plan.status}
            </span>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Progress Bar */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Progress</span>
              <span className="text-sm font-bold">{plan.completion_percentage.toFixed(0)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-green-500 h-3 rounded-full transition-all"
                style={{ width: `${plan.completion_percentage}%` }}
              />
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-sm text-gray-600">Tasks</p>
              <p className="text-2xl font-bold">
                {plan.completed_tasks_count}/{plan.total_tasks_count}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Time Spent</p>
              <p className="text-2xl font-bold">{plan.actual_minutes_spent}m</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Priority</p>
              <p className="text-2xl font-bold capitalize">{plan.priority_level}</p>
            </div>
          </div>

          {/* Action Buttons */}
          {!isCompleted && (
            <div className="flex gap-3">
              {isPending && (
                <Button onClick={handleStartPlan} className="flex-1" disabled={startMutation.isPending}>
                  <Play className="h-4 w-4 mr-2" />
                  Start Plan
                </Button>
              )}
              {isInProgress && (
                <Button onClick={() => setIsCompleteDialogOpen(true)} className="flex-1">
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                  Mark Complete
                </Button>
              )}
              <Button variant="outline" onClick={handleSkipPlan} disabled={skipMutation.isPending}>
                <SkipForward className="h-4 w-4 mr-2" />
                Skip
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recommended Tasks */}
      <div className="space-y-3">
        <h2 className="text-xl font-bold text-gray-900">Your Tasks for Today</h2>
        {plan.recommended_tasks.map((task, index) => {
          const TaskIcon = getTaskIcon(task.type)
          const priorityClass = getPriorityColor(task.priority)

          return (
            <Card key={index} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  {/* Task Icon */}
                  <div className={`p-3 rounded-lg ${priorityClass}`}>
                    <TaskIcon className="h-6 w-6" />
                  </div>

                  {/* Task Details */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-semibold text-lg text-gray-900">
                          {task.title || task.type.replace('_', ' ')}
                        </h3>
                        {task.reason && (
                          <p className="text-sm text-gray-600 mt-1">{task.reason}</p>
                        )}
                      </div>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${priorityClass}`}>
                        {task.priority}
                      </span>
                    </div>

                    {/* Task Stats */}
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        <span>{task.estimated_minutes} min</span>
                      </div>
                      {task.topic && (
                        <div className="flex items-center gap-1">
                          <Target className="h-4 w-4" />
                          <span>{task.topic}</span>
                        </div>
                      )}
                      {task.count && (
                        <div className="flex items-center gap-1">
                          <span>{task.count} items</span>
                        </div>
                      )}
                    </div>

                    {/* Action Button */}
                    <div className="mt-3">
                      {task.type === 'flashcard_review' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => navigate('/flashcards/review')}
                        >
                          Start Review
                        </Button>
                      )}
                      {task.type === 'quiz' && task.entity_id && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => navigate(`/quizzes/${task.entity_id}/take`)}
                        >
                          Take Quiz
                        </Button>
                      )}
                      {task.type === 'free_practice' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => navigate('/documents')}
                        >
                          Get Started
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* AI Feedback (if completed) */}
      {isCompleted && plan.ai_feedback && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="text-green-800">AI Feedback</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-green-700">{plan.ai_feedback}</p>
          </CardContent>
        </Card>
      )}

      {/* Complete Plan Dialog */}
      <Dialog open={isCompleteDialogOpen} onOpenChange={setIsCompleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Complete Today's Plan 🎉</DialogTitle>
            <DialogDescription>
              How did you do? Share your progress!
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Time Spent */}
            <div>
              <Label htmlFor="minutes">Time Spent (minutes) *</Label>
              <input
                id="minutes"
                type="number"
                min="0"
                className="w-full px-3 py-2 border rounded-md"
                placeholder="25"
                value={completionData.actual_minutes_spent || ''}
                onChange={(e) => setCompletionData({
                  ...completionData,
                  actual_minutes_spent: parseInt(e.target.value)
                })}
              />
            </div>

            {/* Tasks Completed */}
            <div>
              <Label htmlFor="tasks">Tasks Completed *</Label>
              <input
                id="tasks"
                type="number"
                min="0"
                max={plan.total_tasks_count}
                className="w-full px-3 py-2 border rounded-md"
                placeholder={`0 - ${plan.total_tasks_count}`}
                value={completionData.completed_tasks_count || ''}
                onChange={(e) => setCompletionData({
                  ...completionData,
                  completed_tasks_count: parseInt(e.target.value)
                })}
              />
            </div>

            {/* Effectiveness Rating */}
            <div>
              <Label>How helpful was this plan?</Label>
              <div className="flex gap-2 mt-2">
                {[1, 2, 3, 4, 5].map((rating) => (
                  <Button
                    key={rating}
                    variant={completionData.effectiveness_rating === rating ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setCompletionData({
                      ...completionData,
                      effectiveness_rating: rating
                    })}
                  >
                    <Star className={`h-4 w-4 ${
                      completionData.effectiveness_rating && rating <= completionData.effectiveness_rating
                        ? 'fill-yellow-400 text-yellow-400'
                        : ''
                    }`} />
                  </Button>
                ))}
              </div>
            </div>

            {/* Notes */}
            <div>
              <Label htmlFor="notes">Notes (optional)</Label>
              <Textarea
                id="notes"
                placeholder="How did it go? Any thoughts?"
                value={completionData.user_notes || ''}
                onChange={(e) => setCompletionData({
                  ...completionData,
                  user_notes: e.target.value
                })}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCompleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleCompletePlan}
              disabled={completeMutation.isPending}
            >
              {completeMutation.isPending ? 'Saving...' : 'Complete Plan'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

