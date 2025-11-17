import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Calendar, Plus, Edit, Trash2, CheckCircle2, XCircle, 
  Clock, Target, TrendingUp, BarChart3, Settings, PlayCircle, RefreshCw, AlertTriangle
} from 'lucide-react'
import { toast } from 'react-hot-toast'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import studyScheduleService, { 
  StudySchedule, 
  StudyScheduleCreate, 
  StudyScheduleUpdate 
} from '@/services/studyScheduleService'

export default function StudySchedulePage() {
  const queryClient = useQueryClient()
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
        toast.info(result.reason || 'No adjustment needed')
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
              <div className="flex items-start justify-between">
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
                
                {/* Auto-adjust button */}
                {schedule.is_active && (
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

      {schedules.length === 0 && (
        <Card className="text-center py-12">
          <CardContent>
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No schedules yet</h3>
            <p className="text-gray-600 mb-6">
              Create your first study schedule to start tracking your learning journey
            </p>
            <Button onClick={() => setIsCreateDialogOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Schedule
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

