import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { 
  Calendar, Plus, Edit, Trash2, CheckCircle2, 
  Clock, Target, TrendingUp, Settings, PlayCircle, RefreshCw, AlertTriangle,
  BookOpen, Brain, CreditCard, ArrowRight, Info
} from 'lucide-react'
import { toast } from 'react-hot-toast'
import { Button } from '@/components/ui/button' 
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import studyScheduleService, { 
  StudySchedule, 
  StudyScheduleCreate, 
  StudyScheduleUpdate 
} from '@/services/studyScheduleService'
import dailyPlanService from '@/services/dailyPlanService'

export default function StudySchedulePage() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [selectedSchedule, setSelectedSchedule] = useState<StudySchedule | null>(null)
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
    enabled: !!activeSchedule,
    refetchOnWindowFocus: false
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Calendar className="w-8 h-8 text-indigo-600" />
              Study Schedule
            </h1>
            <p className="mt-2 text-gray-600">
              Manage your weekly study schedule and track your progress
            </p>
          </div>
          <Button
            onClick={() => setIsCreateDialogOpen(true)}
            className="flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Create Schedule
          </Button>
        </div>
      </div>

      {/* Today's Plan Section - Priority 1 */}
      {activeSchedule && todayPlan?.has_plan && todayPlan.plan && (
        <Card className="mb-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white border-0 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold mb-1">📚 Today's Study Plan</h2>
                <p className="text-blue-100 text-sm">
                  {new Date(todayPlan.plan.plan_date).toLocaleDateString('en-US', {
                    weekday: 'long',
                    month: 'long',
                    day: 'numeric'
                  })}
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/today-plan')}
                className="bg-white/20 hover:bg-white/30 border-white/30 text-white"
              >
                View Full Plan
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>

            {/* Tasks Preview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {todayPlan.plan.recommended_tasks.slice(0, 3).map((task: any, idx: number) => {
                const TaskIcon = getTaskIcon(task.type)
                return (
                  <div key={idx} className="bg-white/10 backdrop-blur rounded-lg p-4 border border-white/20">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <TaskIcon className="w-5 h-5" />
                        <span className="text-sm opacity-90 capitalize">
                          {task.type.replace('_', ' ')}
                        </span>
                      </div>
                      <span className="text-xs bg-white/20 px-2 py-1 rounded">
                        {task.estimated_minutes}min
                      </span>
                    </div>
                    <h3 className="font-semibold mb-2 text-sm">
                      {task.title || task.type.replace('_', ' ')}
                    </h3>
                    <Button
                      size="sm"
                      variant="outline"
                      className="w-full bg-white/20 hover:bg-white/30 border-white/30 text-white text-xs"
                      onClick={() => {
                        if (task.type === 'flashcard_review') navigate('/flashcards/review')
                        else if (task.type === 'quiz' && task.entity_id) navigate(`/quizzes/${task.entity_id}/take`)
                        else navigate('/today-plan')
                      }}
                    >
                      Start Now →
                    </Button>
                  </div>
                )
              })}
            </div>

            {/* Progress Indicator */}
            <div className="mt-4 pt-4 border-t border-white/20">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="opacity-90">Today's Progress</span>
                <span className="font-semibold">
                  {Number(todayPlan.plan.completion_percentage).toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-white/20 rounded-full h-2">
                <div
                  className="bg-white h-2 rounded-full transition-all"
                  style={{ width: `${Number(todayPlan.plan.completion_percentage)}%` }}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Active Schedule Banner */}
      {activeSchedule && (
        <Card className="mb-6 border-green-500 bg-green-50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-6 h-6 text-green-600" />
                <div>
                  <h3 className="font-semibold text-lg text-gray-900">
                    Active Schedule: {activeSchedule.schedule_name}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {activeSchedule.schedule_config.daily_minutes} min/day • 
                    {activeSchedule.schedule_config.days_per_week} days/week • 
                    {activeSchedule.days_completed} days completed
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                  Active
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => deactivateMutation.mutate(activeSchedule.id)}
                  disabled={deactivateMutation.isPending}
                >
                  Deactivate
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Schedules List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {schedules.map((schedule) => (
          <Card
            key={schedule.id}
            className={`hover:shadow-lg transition-shadow ${
              schedule.is_active ? 'border-green-500 bg-green-50' : ''
            }`}
          >
            <CardHeader>
              <div className="flex items-start gap-3 mb-4">
                {/* Schedule Type Icon */}
                <div className={`p-3 rounded-xl ${getScheduleTypeVisual(schedule.schedule_type).bg}`}>
                  {(() => {
                    const Icon = getScheduleTypeVisual(schedule.schedule_type).icon
                    return <Icon className={`w-6 h-6 ${getScheduleTypeVisual(schedule.schedule_type).color}`} />
                  })()}
                </div>
                <div className="flex-1">
                  <CardTitle className="text-lg">{schedule.schedule_name}</CardTitle>
                  <CardDescription>
                    {getScheduleTypeLabel(schedule.schedule_type)}
                  </CardDescription>
                </div>
                {schedule.is_active && (
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
                    Active
                  </span>
                )}
              </div>

              {/* Progress Bar - Priority 1 */}
              {schedule.total_days_scheduled > 0 && (
                <div className="mt-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-indigo-600">Progress</span>
                    <span className="text-xs font-semibold text-indigo-600">
                      {Math.round((schedule.days_completed / schedule.total_days_scheduled) * 100)}%
                    </span>
                  </div>
                  <div className="overflow-hidden h-2 mb-2 text-xs flex rounded bg-indigo-200">
                    <div
                      style={{
                        width: `${(schedule.days_completed / schedule.total_days_scheduled) * 100}%`
                      }}
                      className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-500 transition-all duration-500"
                    />
                  </div>
                  <div className="text-xs text-gray-500">
                    {schedule.days_completed} of {schedule.total_days_scheduled} days completed
                  </div>
                </div>
              )}
            </CardHeader>
            <CardContent>
              {/* Stats */}
              <div className="space-y-3 mb-4">
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <span>{schedule.schedule_config.daily_minutes} min/day</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Calendar className="w-4 h-4 text-gray-500" />
                  <span>{schedule.schedule_config.days_per_week} days/week</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Target className="w-4 h-4 text-gray-500" />
                  <span>{schedule.days_completed}/{schedule.total_days_scheduled} days completed</span>
                </div>
                {schedule.avg_adherence_rate > 0 && (
                  <div className="flex items-center gap-2 text-sm">
                    <TrendingUp className="w-4 h-4 text-gray-500" />
                    <span>{Number(schedule.avg_adherence_rate).toFixed(0)}% adherence</span>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="space-y-2">
                <div className="flex gap-2">
                  {!schedule.is_active && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => activateMutation.mutate(schedule.id)}
                      disabled={activateMutation.isPending}
                      className="flex-1"
                    >
                      <PlayCircle className="w-4 h-4 mr-1" />
                      Activate
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(schedule)}
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(schedule)}
                    disabled={deleteMutation.isPending}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
                
                {/* Auto-adjust button with tooltip */}
                {schedule.is_active && (
                  <div className="relative group">
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full"
                      onClick={() => adjustMutation.mutate(schedule.id)}
                      disabled={adjustMutation.isPending}
                    >
                      <RefreshCw className={`w-4 h-4 mr-2 ${adjustMutation.isPending ? 'animate-spin' : ''}`} />
                      Auto-Adjust Schedule
                    </Button>
                    {/* Tooltip */}
                    <div className="absolute bottom-full mb-2 left-0 hidden group-hover:block z-10">
                      <div className="bg-gray-900 text-white text-xs rounded py-2 px-3 w-64 shadow-lg">
                        <div className="flex items-start gap-2">
                          <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="font-semibold mb-1">AI Schedule Adjustment</p>
                            <p className="text-gray-300">
                              Analyzes your performance and automatically adjusts your schedule to keep you on track 🤖
                            </p>
                          </div>
                        </div>
                        <div className="absolute bottom-0 left-4 transform translate-y-full">
                          <div className="border-4 border-transparent border-t-gray-900"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Adjustment info */}
                {schedule.last_adjusted_at && (
                  <div className="text-xs text-gray-500 mt-2">
                    <p>Last adjusted: {new Date(schedule.last_adjusted_at).toLocaleDateString()}</p>
                    {schedule.adjustment_reason && (
                      <p className="text-gray-400 italic">{schedule.adjustment_reason}</p>
                    )}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Improved Empty State - Priority 1 */}
      {schedules.length === 0 && (
        <Card className="text-center py-16 bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-dashed border-indigo-200">
          <CardContent>
            {/* Illustration */}
            <div className="mb-6">
              <div className="inline-flex items-center justify-center w-24 h-24 bg-indigo-100 rounded-full mb-4">
                <Calendar className="w-12 h-12 text-indigo-600" />
              </div>
            </div>

            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              Let's Create Your First Schedule! 🎯
            </h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Tell us your goal and we'll create a personalized study plan that adapts to your pace
            </p>

            {/* Quick Start Templates */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto mb-6">
              <button
                onClick={() => {
                  setFormData({
                    ...formData,
                    schedule_name: 'IELTS 6.5 Preparation',
                    schedule_type: 'exam_prep',
                    schedule_config: {
                      ...formData.schedule_config!,
                      daily_minutes: 45,
                      days_per_week: 6
                    }
                  })
                  setIsCreateDialogOpen(true)
                }}
                className="p-4 border-2 border-dashed rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-all text-left"
              >
                <Target className="w-8 h-8 text-indigo-600 mx-auto mb-2" />
                <div className="font-semibold">IELTS 6.5</div>
                <div className="text-sm text-gray-500">3 months intensive</div>
              </button>
              <button
                onClick={() => {
                  setFormData({
                    ...formData,
                    schedule_name: 'Daily Practice',
                    schedule_type: 'time_based',
                    schedule_config: {
                      ...formData.schedule_config!,
                      daily_minutes: 30,
                      days_per_week: 5
                    }
                  })
                  setIsCreateDialogOpen(true)
                }}
                className="p-4 border-2 border-dashed rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-all text-left"
              >
                <Clock className="w-8 h-8 text-indigo-600 mx-auto mb-2" />
                <div className="font-semibold">30 min/day</div>
                <div className="text-sm text-gray-500">Flexible schedule</div>
              </button>
              <button
                onClick={() => setIsCreateDialogOpen(true)}
                className="p-4 border-2 border-dashed rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-all text-left"
              >
                <Settings className="w-8 h-8 text-indigo-600 mx-auto mb-2" />
                <div className="font-semibold">Custom</div>
                <div className="text-sm text-gray-500">Advanced options</div>
              </button>
            </div>

            <Button size="lg" onClick={() => setIsCreateDialogOpen(true)}>
              <Plus className="w-5 h-5 mr-2" />
              Create My Schedule
            </Button>
          </CardContent>
        </Card>
      )}

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

