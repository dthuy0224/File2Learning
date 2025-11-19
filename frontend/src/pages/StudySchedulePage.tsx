import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { 
  Calendar, Plus, Edit, Trash2, CheckCircle2, 
  Clock, Target, TrendingUp, Settings, PlayCircle, RefreshCw, AlertTriangle,
  BookOpen, Brain, CreditCard, Pause, Flame, Award, BarChart3, Sparkles, Star
} from 'lucide-react'
import { toast } from 'react-hot-toast'
import { Button } from '@/components/ui/button' 
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import studyScheduleService, { 
  StudySchedule, 
  StudyScheduleCreate, 
  StudyScheduleUpdate 
} from '@/services/studyScheduleService'
import dailyPlanService, { CompletePlanData } from '@/services/dailyPlanService'
import { invalidateProgressQueries } from '@/utils/progressInvalidation'

export default function StudySchedulePage() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<'today' | 'week' | 'all'>('today')
  const [selectedSchedule, setSelectedSchedule] = useState<StudySchedule | null>(null)
  const [isCompleteDialogOpen, setIsCompleteDialogOpen] = useState(false)
  const [isSkipDialogOpen, setIsSkipDialogOpen] = useState(false)
  const [completionData, setCompletionData] = useState<Partial<CompletePlanData>>({})
  const [skipReason, setSkipReason] = useState('')
  const [formData, setFormData] = useState<Partial<StudyScheduleCreate>>({
    schedule_name: '',
    schedule_type: 'time_based',
    schedule_config: {
      daily_minutes: 30,
      days_per_week: 5,
      preferred_times: [],
      activity_distribution: {
        flashcards: 0.4,
        quizzes: 0.3,
        reading: 0.3
      }
    },
    max_daily_load: 60,
    min_daily_load: 15,
    adaptation_mode: 'moderate',
    catch_up_strategy: 'gradual'
  })

  // Fetch all schedules
  const { data: schedules = [], isLoading } = useQuery({
    queryKey: ['study-schedules'],
    queryFn: () => studyScheduleService.getSchedules({ active_only: false })
  })

  // Fetch active schedule
  const { data: activeSchedule } = useQuery({
    queryKey: ['active-schedule'],
    queryFn: () => studyScheduleService.getActiveSchedule(),
    retry: false
  })

  // Fetch today's plan (for Today View section)
  const { data: todayPlan } = useQuery({
    queryKey: ['todayPlan'],
    queryFn: () => dailyPlanService.getTodayPlan(),
    refetchOnWindowFocus: false
  })

  const { data: linkedSchedule } = useQuery({
    queryKey: ['linked-schedule', todayPlan?.plan?.schedule_id],
    queryFn: () => studyScheduleService.getSchedule(todayPlan!.plan!.schedule_id!),
    enabled: !!todayPlan?.plan?.schedule_id,
    retry: false
  })

  // Create schedule mutation
  const createMutation = useMutation({
    mutationFn: (data: StudyScheduleCreate) => studyScheduleService.createSchedule(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['study-schedules'] })
      queryClient.invalidateQueries({ queryKey: ['active-schedule'] })
      toast.success('Schedule created successfully! 🎉')
      setIsCreateDialogOpen(false)
      resetForm()
    },
    onError: () => {
      toast.error('Failed to create schedule')
    }
  })

  // Update schedule mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: StudyScheduleUpdate }) =>
      studyScheduleService.updateSchedule(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['study-schedules'] })
      queryClient.invalidateQueries({ queryKey: ['active-schedule'] })
      toast.success('Schedule updated successfully! ✅')
      setIsEditDialogOpen(false)
      setSelectedSchedule(null)
    },
    onError: () => {
      toast.error('Failed to update schedule')
    }
  })

  // Activate schedule mutation
  const activateMutation = useMutation({
    mutationFn: (id: number) => studyScheduleService.activateSchedule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['study-schedules'] })
      queryClient.invalidateQueries({ queryKey: ['active-schedule'] })
      queryClient.invalidateQueries({ queryKey: ['todayPlan'] })
      toast.success('Schedule activated! 🚀')
    }
  })

  // Deactivate schedule mutation
  const deactivateMutation = useMutation({
    mutationFn: (id: number) => studyScheduleService.deactivateSchedule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['study-schedules'] })
      queryClient.invalidateQueries({ queryKey: ['active-schedule'] })
      toast.success('Schedule deactivated')
    }
  })

  // Delete schedule mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => studyScheduleService.deleteSchedule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['study-schedules'] })
      queryClient.invalidateQueries({ queryKey: ['active-schedule'] })
      toast.success('Schedule deleted')
    }
  })

  // Adjust schedule mutation
  const adjustMutation = useMutation({
    mutationFn: (id: number) => studyScheduleService.adjustSchedule(id),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['study-schedules'] })
      queryClient.invalidateQueries({ queryKey: ['active-schedule'] })
      if (result.adjusted) {
        toast.success(`Schedule adjusted! ${result.adjustment?.reason || ''}`)
      } else {
        toast(result.reason || 'No adjustment needed', { icon: 'ℹ️' })
      }
    },
    onError: () => {
      toast.error('Failed to adjust schedule')
    }
  })

  // Today plan mutations
  const startMutation = useMutation({
    mutationFn: (planId: number) => dailyPlanService.startPlan(planId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todayPlan'] })
      invalidateProgressQueries(queryClient)
      toast.success('Plan started! Good luck! 💪')
    }
  })

  const completeMutation = useMutation({
    mutationFn: ({ planId, data }: { planId: number; data: CompletePlanData }) =>
      dailyPlanService.completePlan(planId, data),
    onSuccess: () => {
      invalidateProgressQueries(queryClient, { includeTodayPlan: true })
      toast.success('Awesome! Plan completed! 🎉')
      setIsCompleteDialogOpen(false)
      setCompletionData({})
    }
  })

  const skipMutation = useMutation({
    mutationFn: ({ planId, reason }: { planId: number; reason?: string }) =>
      dailyPlanService.skipPlan(planId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todayPlan'] })
      invalidateProgressQueries(queryClient)
      toast.success('Plan skipped')
    }
  })

  const resetForm = () => {
    setFormData({
      schedule_name: '',
      schedule_type: 'time_based',
      schedule_config: {
        daily_minutes: 30,
        days_per_week: 5,
        preferred_times: [],
        activity_distribution: {
          flashcards: 0.4,
          quizzes: 0.3,
          reading: 0.3
        }
      },
      max_daily_load: 60,
      min_daily_load: 15,
      adaptation_mode: 'moderate',
      catch_up_strategy: 'gradual'
    })
  }

  const handleCreate = () => {
    if (!formData.schedule_name || !formData.schedule_config) {
      toast.error('Please fill in all required fields')
      return
    }
    createMutation.mutate(formData as StudyScheduleCreate)
  }

  const handleEdit = (schedule: StudySchedule) => {
    setSelectedSchedule(schedule)
    setFormData({
      schedule_name: schedule.schedule_name,
      schedule_type: schedule.schedule_type,
      schedule_config: schedule.schedule_config,
      max_daily_load: schedule.max_daily_load,
      min_daily_load: schedule.min_daily_load,
      adaptation_mode: schedule.adaptation_mode,
      catch_up_strategy: schedule.catch_up_strategy,
      goal_id: schedule.goal_id
    })
    setIsEditDialogOpen(true)
  }

  const handleUpdate = () => {
    if (!selectedSchedule) return
    updateMutation.mutate({
      id: selectedSchedule.id,
      data: formData as StudyScheduleUpdate
    })
  }

  const handleDelete = (schedule: StudySchedule) => {
    if (window.confirm(`Are you sure you want to delete "${schedule.schedule_name}"?`)) {
      deleteMutation.mutate(schedule.id)
    }
  }

  const getScheduleTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      goal_based: 'Goal-Based',
      time_based: 'Time-Based',
      exam_prep: 'Exam Prep',
      maintenance: 'Maintenance',
      custom: 'Custom'
    }
    return labels[type] || type
  }

  const getAdaptationModeLabel = (mode: string) => {
    const labels: Record<string, string> = {
      strict: 'Strict',
      moderate: 'Moderate',
      flexible: 'Flexible',
      highly_adaptive: 'Highly Adaptive'
    }
    return labels[mode] || mode
  }

  // Get schedule type visual identity (icons + colors)
  const getScheduleTypeVisual = (type: string) => {
    const visuals: Record<string, { icon: any, color: string, bg: string }> = {
      goal_based: { icon: Target, color: 'text-blue-600', bg: 'bg-blue-100' },
      time_based: { icon: Clock, color: 'text-green-600', bg: 'bg-green-100' },
      exam_prep: { icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-100' },
      maintenance: { icon: RefreshCw, color: 'text-purple-600', bg: 'bg-purple-100' },
      custom: { icon: Settings, color: 'text-gray-600', bg: 'bg-gray-100' }
    }
    return visuals[type] || visuals.custom
  }

  const getTaskIcon = (type: string) => {
    switch (type) {
      case 'flashcard_review': return CreditCard
      case 'quiz': return Brain
      case 'document_reading': return BookOpen
      default: return Target
    }
  }

  const getTaskAccent = (type: string) => {
    const mapping: Record<string, string> = {
      flashcard_review: 'bg-green-100 text-green-700 border-green-300',
      quiz: 'bg-purple-100 text-purple-700 border-purple-300',
      document_reading: 'bg-orange-100 text-orange-700 border-orange-300',
      free_practice: 'bg-blue-100 text-blue-700 border-blue-300'
    }
    return mapping[type] || 'bg-gray-100 text-gray-700 border-gray-300'
  }

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
    setIsSkipDialogOpen(true)
  }

  const confirmSkipPlan = () => {
    if (!todayPlan?.plan) return
    skipMutation.mutate(
      {
        planId: todayPlan.plan.id,
        reason: skipReason.trim() || undefined
      },
      {
        onSuccess: () => {
          setIsSkipDialogOpen(false)
          setSkipReason('')
        }
      }
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  const todayPlanHasTasks = Boolean(todayPlan?.plan?.recommended_tasks?.length)
  const todayTasks = todayPlan?.plan?.recommended_tasks || []
  const todayPlanStats = todayPlan?.plan

  const renderTodayView = () => {
    if (!todayPlan?.has_plan || !todayPlanStats) {
      return (
        <Card className="p-8 text-center border-dashed border-2 border-gray-200">
          <CardContent className="space-y-4">
            <Target className="w-12 h-12 text-gray-300 mx-auto" />
            <h3 className="text-xl font-semibold text-gray-900">No plan available today</h3>
            <p className="text-gray-600">
              Generate a plan to start tracking your progress and keep the streak going.
            </p>
            <Button variant="outline" onClick={() => setActiveTab('all')}>
              Manage schedules
            </Button>
          </CardContent>
        </Card>
      )
    }

    const plan = todayPlanStats
    const isCompleted = plan.status === 'completed'
    const isInProgress = plan.status === 'in_progress'
    const isPending = plan.status === 'pending'
    const completionPercent = Number(plan.completion_percentage || 0).toFixed(0)
    const minutesSpent = plan.actual_minutes_spent || 0
    const remainingMinutes = Math.max(plan.total_estimated_minutes - minutesSpent, 0)

    return (
      <div className="space-y-6">
        <Card className="bg-gradient-to-r from-blue-500 to-purple-600 text-white border-0 shadow-lg">
          <CardContent className="p-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-blue-100 text-sm">
                {new Date(plan.plan_date).toLocaleDateString('en-US', {
                  weekday: 'long',
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric'
                })}
              </p>
              <h2 className="text-2xl font-bold mt-2">Today&apos;s Study Plan</h2>
            </div>
            <div className="text-right">
              <p className="text-sm text-blue-100">Estimated time</p>
              <p className="text-3xl font-bold">{plan.total_estimated_minutes} min</p>
            </div>
          </CardContent>
        </Card>

        {todayPlan.is_new && (
          <Card className="border-green-200 bg-green-50">
            <CardContent className="pt-6">
              <p className="text-green-800 font-medium">✨ {todayPlan.message}</p>
            </CardContent>
          </Card>
        )}

        {linkedSchedule && (
          <Card className="border-indigo-200 bg-indigo-50">
            <CardContent className="pt-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-indigo-600" />
                <div>
                  <p className="font-semibold text-indigo-900">From schedule: {linkedSchedule.schedule_name}</p>
                  <p className="text-sm text-indigo-700">
                    {linkedSchedule.schedule_config.daily_minutes} min/day • {linkedSchedule.schedule_config.days_per_week} days/week
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

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
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Progress</span>
                <span className="text-sm font-bold">{completionPercent}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-green-500 h-3 rounded-full transition-all"
                  style={{ width: `${plan.completion_percentage}%` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-sm text-gray-600">Tasks</p>
                <p className="text-2xl font-bold">{plan.completed_tasks_count}/{plan.total_tasks_count}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Time Spent</p>
                <p className="text-2xl font-bold">{minutesSpent}m</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Priority</p>
                <p className="text-2xl font-bold capitalize">{plan.priority_level}</p>
              </div>
            </div>

            {!isCompleted && (
              <div className="flex flex-col gap-3 md:flex-row">
                {isPending && (
                  <Button className="flex-1" onClick={handleStartPlan} disabled={startMutation.isPending}>
                    <PlayCircle className="h-4 w-4 mr-2" />
                    {startMutation.isPending ? 'Starting...' : 'Start Plan'}
                  </Button>
                )}
                {isInProgress && (
                  <Button className="flex-1" onClick={() => setIsCompleteDialogOpen(true)}>
                    <CheckCircle2 className="h-4 w-4 mr-2" />
                    Mark Complete
                  </Button>
                )}
                <Button
                  variant="outline"
                  onClick={handleSkipPlan}
                  disabled={skipMutation.isPending}
                >
                  Skip
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {todayPlanHasTasks && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Today&apos;s Tasks</h2>
                <div className="text-sm text-gray-600">
                  {plan.completed_tasks_count}/{plan.total_tasks_count} completed
                </div>
              </div>

              {todayTasks.map((task, idx) => {
                const TaskIcon = getTaskIcon(task.type)
                const accent = getTaskAccent(task.type)

                return (
                  <div
                    key={idx}
                    className="border-2 rounded-2xl p-5 transition-all hover:shadow-md bg-white"
                  >
                    <div className="flex items-start gap-4">
                      <div className={`p-4 rounded-xl border ${accent}`}>
                        <TaskIcon className="w-6 h-6" />
                      </div>
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {task.title || task.type.replace(/_/g, ' ')}
                          </h3>
                          {task.recommendation_id && (
                            <span className="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800 border border-purple-300 flex items-center gap-1">
                              <Sparkles className="w-3 h-3" />
                              AI Recommended
                            </span>
                          )}
                        </div>
                        {task.reason && <p className="text-sm text-gray-600">{task.reason}</p>}
                        <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {task.estimated_minutes} min
                          </span>
                          {task.topic && (
                            <span className="flex items-center gap-1">
                              <Target className="w-3 h-3" />
                              {task.topic}
                            </span>
                          )}
                          {task.count && (
                            <span>{task.count} items</span>
                          )}
                          {task.priority && (
                            <span className="px-2 py-1 rounded text-xs font-medium capitalize bg-gray-100 text-gray-700">
                              {task.priority}
                            </span>
                          )}
                        </div>

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
                  </div>
                )
              })}
            </div>

            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Today&apos;s Stats</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 text-sm">Completed</span>
                    <span className="font-bold text-green-600 text-lg">
                      {plan.completed_tasks_count}/{plan.total_tasks_count}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 text-sm">Time Spent</span>
                    <span className="font-bold text-blue-600 text-lg">
                      {minutesSpent} min
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 text-sm">Remaining</span>
                    <span className="font-bold text-orange-600 text-lg">
                      {remainingMinutes} min
                    </span>
                  </div>

                  <div className="pt-4 border-t border-gray-200 text-center">
                    <div className="text-3xl font-bold text-indigo-600 mb-1">
                      {completionPercent}%
                    </div>
                    <p className="text-xs text-gray-500">Daily Goal Progress</p>
                  </div>
                </CardContent>
              </Card>

              {todayPlan?.user_streak !== undefined && (
                <div className="bg-gradient-to-br from-orange-500 to-red-500 rounded-xl p-5 text-white shadow-lg">
                  <div className="flex items-center justify-between mb-3">
                    <Flame className="w-8 h-8" />
                    <span className="text-2xl font-bold">{todayPlan.user_streak} Days</span>
                  </div>
                  <h3 className="font-semibold mb-1">Keep the streak!</h3>
                  <p className="text-sm text-orange-100">
                    Complete today&apos;s plan to extend your streak.
                  </p>
                </div>
              )}

              <div className="bg-gradient-to-br from-purple-100 to-pink-100 border-2 border-purple-200 rounded-xl p-5">
                <div className="flex items-start gap-3">
                  <Award className="w-6 h-6 text-purple-600 flex-shrink-0 mt-1" />
                  <div>
                    <h4 className="font-semibold text-purple-900 mb-1">You&apos;re doing great!</h4>
                    <p className="text-sm text-purple-700">
                      Complete all tasks today to earn extra XP and stay on track.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

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
      </div>
    )
  }

  const renderWeekView = () => {
    if (!activeSchedule) {
      return (
        <Card className="p-8 text-center">
          <CardContent>
            <h3 className="text-xl font-semibold text-gray-900">No active schedule</h3>
            <p className="text-gray-600 mt-2">Activate a schedule to see weekly insights.</p>
            <Button className="mt-4" onClick={() => setActiveTab('all')}>
              Browse schedules
            </Button>
          </CardContent>
        </Card>
      )
    }

    const completionRate = activeSchedule.total_days_scheduled
      ? Math.round((activeSchedule.days_completed / activeSchedule.total_days_scheduled) * 100)
      : 0

    return (
      <Card className="rounded-2xl border border-gray-200 shadow-sm">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>This Week&apos;s Progress</CardTitle>
              <CardDescription>
                Track adherence and completion across your active schedule
              </CardDescription>
            </div>
            <div className="text-sm text-gray-600">
              {activeSchedule.days_completed} / {activeSchedule.total_days_scheduled} days
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Overall completion</span>
              <span>{completionRate}%</span>
            </div>
            <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all"
                style={{ width: `${completionRate}%` }}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-xl">
              <div className="text-2xl font-bold text-green-600">
                {activeSchedule.days_completed}
              </div>
              <p className="text-sm text-gray-600">Days completed</p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-xl">
              <div className="text-2xl font-bold text-blue-600">
                {activeSchedule.days_missed}
              </div>
              <p className="text-sm text-gray-600">Days missed</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-xl">
              <div className="text-2xl font-bold text-purple-600">
                {Number(activeSchedule.avg_adherence_rate || 0).toFixed(0)}%
              </div>
              <p className="text-sm text-gray-600">Average adherence</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="border-dashed border-gray-200">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold">Adaptation</CardTitle>
                <CardDescription>Latest adjustments</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-gray-600">
                <p>Mode: {getAdaptationModeLabel(activeSchedule.adaptation_mode)}</p>
                {activeSchedule.last_adjusted_at ? (
                  <p>Last adjusted: {new Date(activeSchedule.last_adjusted_at).toLocaleDateString()}</p>
                ) : (
                  <p>No adjustments yet</p>
                )}
                {activeSchedule.adjustment_reason && (
                  <p className="italic text-gray-500">{activeSchedule.adjustment_reason}</p>
                )}
              </CardContent>
            </Card>

            <Card className="border-dashed border-gray-200">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold">Workload</CardTitle>
                <CardDescription>Configured intensity</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-gray-600">
                <p>{activeSchedule.schedule_config.daily_minutes} min/day target</p>
                <p>{activeSchedule.schedule_config.days_per_week} days/week</p>
                <p>Range: {activeSchedule.min_daily_load}-{activeSchedule.max_daily_load} min</p>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>
    )
  }

  const renderScheduleCard = (schedule: StudySchedule) => {
    const Icon = getScheduleTypeVisual(schedule.schedule_type).icon
    const progress = schedule.total_days_scheduled
      ? Math.round((schedule.days_completed / schedule.total_days_scheduled) * 100)
      : 0

    return (
      <div
        key={schedule.id}
        className={`bg-white rounded-2xl border-2 p-6 transition-all hover:shadow-lg ${
          schedule.is_active ? 'border-green-500 ring-2 ring-green-200' : 'border-gray-200'
        }`}
      >
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 rounded-xl ${getScheduleTypeVisual(schedule.schedule_type).bg}`}>
            <Icon className={`w-6 h-6 ${getScheduleTypeVisual(schedule.schedule_type).color}`} />
          </div>
          {schedule.is_active && (
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
              Active
            </span>
          )}
        </div>

        <h3 className="text-xl font-bold text-gray-900 mb-1">{schedule.schedule_name}</h3>
        <p className="text-sm text-gray-600 mb-4">{getScheduleTypeLabel(schedule.schedule_type)}</p>

        <div className="space-y-2 text-sm text-gray-600 mb-4">
          <div className="flex items-center justify-between">
            <span>Daily time</span>
            <span className="font-semibold">{schedule.schedule_config.daily_minutes} min</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Frequency</span>
            <span className="font-semibold">{schedule.schedule_config.days_per_week}x/week</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Progress</span>
            <span className="font-semibold">
              {schedule.days_completed}/{schedule.total_days_scheduled}
            </span>
          </div>
        </div>

        <div className="mb-4">
          <div className="flex justify-between text-xs text-gray-600 mb-1">
            <span>Completion</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="flex gap-2">
          {schedule.is_active ? (
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => deactivateMutation.mutate(schedule.id)}
              disabled={deactivateMutation.isPending}
            >
              <Pause className="w-4 h-4 mr-1" />
              Pause
            </Button>
          ) : (
            <Button
              className="flex-1"
              onClick={() => activateMutation.mutate(schedule.id)}
              disabled={activateMutation.isPending}
            >
              <PlayCircle className="w-4 h-4 mr-1" />
              Activate
            </Button>
          )}
          <Button variant="outline" size="icon" onClick={() => handleEdit(schedule)}>
            <Edit className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={() => handleDelete(schedule)}
            disabled={deleteMutation.isPending}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Calendar className="w-8 h-8 text-indigo-600" />
              Study Schedule
            </h1>
            <p className="mt-2 text-gray-600">
              Manage your learning journey and stay on track every day
            </p>
          </div>
          <Button
            onClick={() => setIsCreateDialogOpen(true)}
            className="flex items-center gap-2 shadow-lg hover:shadow-xl"
          >
            <Plus className="w-4 h-4" />
            Create Schedule
          </Button>
        </div>

        {activeSchedule ? (
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 mb-8 text-white shadow-xl">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
              <div className="flex items-center gap-4">
                <div className="p-4 bg-white/20 backdrop-blur rounded-xl">
                  <Target className="w-8 h-8" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold mb-1">{activeSchedule.schedule_name}</h2>
                  <p className="text-indigo-100 capitalize">{getScheduleTypeLabel(activeSchedule.schedule_type)}</p>
                  <div className="flex items-center gap-4 mt-2 text-sm">
                    <span className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {activeSchedule.schedule_config.daily_minutes} min/day
                    </span>
                    <span>•</span>
                    <span>{activeSchedule.schedule_config.days_per_week} days/week</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="bg-white/20 backdrop-blur px-6 py-3 rounded-xl text-center">
                  <div className="text-3xl font-bold">{todayPlan?.user_streak ?? activeSchedule.days_completed}</div>
                  <div className="text-xs opacity-90">Day Streak 🔥</div>
                </div>
                <div className="flex flex-col gap-2">
                  <span className="px-4 py-1 bg-green-400 text-green-900 rounded-full text-sm font-semibold">
                    Active
                  </span>
                  {activeSchedule.avg_adherence_rate >= 80 && (
                    <span className="px-4 py-1 bg-yellow-400 text-yellow-900 rounded-full text-sm font-semibold flex items-center gap-1">
                      <TrendingUp className="w-3 h-3" />
                      On Track
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="space-y-2 mt-6">
              <div className="flex justify-between text-sm">
                <span>
                  Overall Progress: {activeSchedule.days_completed}/{activeSchedule.total_days_scheduled} days
                </span>
                <span>
                  {activeSchedule.total_days_scheduled
                    ? Math.round((activeSchedule.days_completed / activeSchedule.total_days_scheduled) * 100)
                    : 0
                  }% Complete
                </span>
              </div>
              <div className="w-full bg-white/20 rounded-full h-4 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-green-400 to-emerald-400 h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${activeSchedule.total_days_scheduled
                      ? (activeSchedule.days_completed / activeSchedule.total_days_scheduled) * 100
                      : 0
                    }%`
                  }}
                />
              </div>
              <div className="flex justify-between text-xs text-indigo-100 mt-1">
                <span>{Number(activeSchedule.avg_adherence_rate || 0).toFixed(0)}% adherence rate</span>
                <span>
                  Last adjusted:{' '}
                  {activeSchedule.last_adjusted_at
                    ? new Date(activeSchedule.last_adjusted_at).toLocaleDateString()
                    : 'N/A'}
                </span>
              </div>
            </div>

            <div className="flex flex-col gap-3 mt-6 lg:flex-row">
              <Button
                variant="outline"
                className="flex-1 bg-white/20 hover:bg-white/30 backdrop-blur border-white/30 text-white"
                onClick={() => adjustMutation.mutate(activeSchedule.id)}
                disabled={adjustMutation.isPending}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${adjustMutation.isPending ? 'animate-spin' : ''}`} />
                Auto-Adjust
              </Button>
              <Button
                variant="outline"
                className="flex-1 bg-white/20 hover:bg-white/30 backdrop-blur border-white/30 text-white"
                onClick={() => handleEdit(activeSchedule)}
              >
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
              <Button
                variant="outline"
                className="flex-1 bg-white/20 hover:bg-white/30 backdrop-blur border-white/30 text-white"
                onClick={() => setActiveTab('week')}
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                View Analytics
              </Button>
            </div>
          </div>
        ) : (
          <Card className="mb-8 border-dashed border-2 border-indigo-200 bg-white/70">
            <CardContent className="py-8 text-center space-y-4">
              <Target className="w-12 h-12 text-indigo-500 mx-auto" />
              <h3 className="text-xl font-semibold text-gray-900">No active schedule yet</h3>
              <p className="text-gray-600">
                Create or activate a schedule to start receiving personalized plans.
              </p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>Create Schedule</Button>
            </CardContent>
          </Card>
        )}

        <div className="bg-white rounded-xl p-2 mb-8 shadow-sm border border-gray-200 flex gap-2">
          {(['today', 'week', 'all'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
                activeTab === tab ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              {tab === 'today' && "Today's Plan"}
              {tab === 'week' && 'This Week'}
              {tab === 'all' && 'All Schedules'}
            </button>
          ))}
        </div>

        {activeTab === 'today' && renderTodayView()}
        {activeTab === 'week' && renderWeekView()}
        {activeTab === 'all' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {schedules.map(renderScheduleCard)}
            <button
              onClick={() => setIsCreateDialogOpen(true)}
              className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-2xl p-6 hover:border-indigo-400 hover:bg-indigo-50 transition-all flex flex-col items-center justify-center gap-4 min-h-[300px]"
            >
              <div className="p-4 bg-indigo-100 rounded-xl">
                <Plus className="w-8 h-8 text-indigo-600" />
              </div>
              <div className="text-center">
                <h3 className="font-semibold text-gray-900 mb-1">Create New Schedule</h3>
                <p className="text-sm text-gray-600">Set up a custom study plan</p>
              </div>
            </button>
          </div>
        )}

        {schedules.length === 0 && activeTab === 'all' && (
          <Card className="text-center py-16 bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-dashed border-indigo-200 mt-6">
            <CardContent>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Let&apos;s create your first schedule! 🎯
              </h3>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                Tell us your goal and we&apos;ll create a personalized study plan that adapts to your pace.
              </p>
              <Button size="lg" onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="w-5 h-5 mr-2" />
                Create my schedule
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Complete Plan Dialog */}
      <Dialog open={isCompleteDialogOpen} onOpenChange={setIsCompleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Complete Today&apos;s Plan 🎉</DialogTitle>
            <DialogDescription>
              How did you do? Share your progress!
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label htmlFor="minutes">Time Spent (minutes) *</Label>
              <input
                id="minutes"
                type="number"
                min="0"
                className="w-full px-3 py-2 border rounded-md"
                placeholder="25"
                value={completionData.actual_minutes_spent ?? ''}
                onChange={(e) => {
                  const value = parseInt(e.target.value, 10)
                  setCompletionData({
                    ...completionData,
                    actual_minutes_spent: Number.isNaN(value) ? undefined : value
                  })
                }}
              />
            </div>

            <div>
              <Label htmlFor="tasks">Tasks Completed *</Label>
              <input
                id="tasks"
                type="number"
                min="0"
                max={todayPlan?.plan?.total_tasks_count}
                className="w-full px-3 py-2 border rounded-md"
                placeholder={`0 - ${todayPlan?.plan?.total_tasks_count ?? ''}`}
                value={completionData.completed_tasks_count ?? ''}
                onChange={(e) => {
                  const value = parseInt(e.target.value, 10)
                  setCompletionData({
                    ...completionData,
                    completed_tasks_count: Number.isNaN(value) ? undefined : value
                  })
                }}
              />
            </div>

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

      {/* Skip Plan Dialog */}
      <Dialog open={isSkipDialogOpen} onOpenChange={(open) => {
        setIsSkipDialogOpen(open)
        if (!open) setSkipReason('')
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Skip Today&apos;s Plan?</DialogTitle>
            <DialogDescription>
              Let us know why you&apos;re skipping (optional). This helps the AI adapt future plans.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="skip-reason">Reason (optional)</Label>
              <Textarea
                id="skip-reason"
                placeholder="Too busy today, not feeling well, etc."
                value={skipReason}
                onChange={(e) => setSkipReason(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setIsSkipDialogOpen(false)
              setSkipReason('')
            }}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={confirmSkipPlan}
              disabled={skipMutation.isPending}
            >
              {skipMutation.isPending ? 'Skipping...' : 'Confirm Skip'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create Schedule Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create Study Schedule</DialogTitle>
            <DialogDescription>
              Set up your weekly study schedule with time preferences and goals
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="schedule_name">Schedule Name *</Label>
              <Input
                id="schedule_name"
                value={formData.schedule_name}
                onChange={(e) => setFormData({ ...formData, schedule_name: e.target.value })}
                placeholder="e.g., IELTS Preparation"
              />
            </div>
            <div>
              <Label htmlFor="schedule_type">Schedule Type *</Label>
              <select
                id="schedule_type"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                value={formData.schedule_type}
                onChange={(e) => setFormData({ ...formData, schedule_type: e.target.value as any })}
              >
                <option value="goal_based">Goal-Based</option>
                <option value="time_based">Time-Based</option>
                <option value="exam_prep">Exam Prep</option>
                <option value="maintenance">Maintenance</option>
                <option value="custom">Custom</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="daily_minutes">Daily Minutes *</Label>
                <Input
                  id="daily_minutes"
                  type="number"
                  min="15"
                  max="300"
                  value={formData.schedule_config?.daily_minutes}
                  onChange={(e) => setFormData({
                    ...formData,
                    schedule_config: {
                      ...formData.schedule_config!,
                      daily_minutes: parseInt(e.target.value) || 30
                    }
                  })}
                />
              </div>
              <div>
                <Label htmlFor="days_per_week">Days Per Week *</Label>
                <Input
                  id="days_per_week"
                  type="number"
                  min="1"
                  max="7"
                  value={formData.schedule_config?.days_per_week}
                  onChange={(e) => setFormData({
                    ...formData,
                    schedule_config: {
                      ...formData.schedule_config!,
                      days_per_week: parseInt(e.target.value) || 5
                    }
                  })}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="min_daily_load">Min Daily Load (min)</Label>
                <Input
                  id="min_daily_load"
                  type="number"
                  min="5"
                  value={formData.min_daily_load}
                  onChange={(e) => setFormData({ ...formData, min_daily_load: parseInt(e.target.value) || 15 })}
                />
              </div>
              <div>
                <Label htmlFor="max_daily_load">Max Daily Load (min)</Label>
                <Input
                  id="max_daily_load"
                  type="number"
                  min="15"
                  value={formData.max_daily_load}
                  onChange={(e) => setFormData({ ...formData, max_daily_load: parseInt(e.target.value) || 60 })}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="adaptation_mode">Adaptation Mode</Label>
              <select
                id="adaptation_mode"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                value={formData.adaptation_mode}
                onChange={(e) => setFormData({ ...formData, adaptation_mode: e.target.value as any })}
              >
                <option value="strict">Strict</option>
                <option value="moderate">Moderate</option>
                <option value="flexible">Flexible</option>
                <option value="highly_adaptive">Highly Adaptive</option>
              </select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Schedule'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Schedule Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Study Schedule</DialogTitle>
            <DialogDescription>
              Update your study schedule settings
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit_schedule_name">Schedule Name *</Label>
              <Input
                id="edit_schedule_name"
                value={formData.schedule_name}
                onChange={(e) => setFormData({ ...formData, schedule_name: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit_daily_minutes">Daily Minutes *</Label>
                <Input
                  id="edit_daily_minutes"
                  type="number"
                  min="15"
                  max="300"
                  value={formData.schedule_config?.daily_minutes}
                  onChange={(e) => setFormData({
                    ...formData,
                    schedule_config: {
                      ...formData.schedule_config!,
                      daily_minutes: parseInt(e.target.value) || 30
                    }
                  })}
                />
              </div>
              <div>
                <Label htmlFor="edit_days_per_week">Days Per Week *</Label>
                <Input
                  id="edit_days_per_week"
                  type="number"
                  min="1"
                  max="7"
                  value={formData.schedule_config?.days_per_week}
                  onChange={(e) => setFormData({
                    ...formData,
                    schedule_config: {
                      ...formData.schedule_config!,
                      days_per_week: parseInt(e.target.value) || 5
                    }
                  })}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit_min_daily_load">Min Daily Load (min)</Label>
                <Input
                  id="edit_min_daily_load"
                  type="number"
                  min="5"
                  value={formData.min_daily_load}
                  onChange={(e) => setFormData({ ...formData, min_daily_load: parseInt(e.target.value) || 15 })}
                />
              </div>
              <div>
                <Label htmlFor="edit_max_daily_load">Max Daily Load (min)</Label>
                <Input
                  id="edit_max_daily_load"
                  type="number"
                  min="15"
                  value={formData.max_daily_load}
                  onChange={(e) => setFormData({ ...formData, max_daily_load: parseInt(e.target.value) || 60 })}
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdate} disabled={updateMutation.isPending}>
              {updateMutation.isPending ? 'Updating...' : 'Update Schedule'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

