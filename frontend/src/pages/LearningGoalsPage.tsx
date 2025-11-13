import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Target, Plus, Calendar, CheckCircle2, AlertCircle, Clock, Trash2 } from 'lucide-react'
import { toast } from 'react-hot-toast'
import learningGoalService, { CreateLearningGoal } from '@/services/learningGoalService'

// Helper functions (instead of date-fns)
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const getDaysDifference = (targetDate: string) => {
  const target = new Date(targetDate)
  const today = new Date()
  const diffTime = target.getTime() - today.getTime()
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

export default function LearningGoalsPage() {
  const queryClient = useQueryClient()
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [newGoal, setNewGoal] = useState<Partial<CreateLearningGoal>>({
    goal_type: 'vocabulary_count',
    priority: 'medium',
    target_metrics: {}
  })

  // Fetch goals
  const { data: goals = [], isLoading } = useQuery({
    queryKey: ['learningGoals'],
    queryFn: () => learningGoalService.getGoals()
  })

  // Fetch summary
  const { data: summary } = useQuery({
    queryKey: ['goalsSummary'],
    queryFn: () => learningGoalService.getGoalsSummary()
  })

  // Create goal mutation
  const createMutation = useMutation({
    mutationFn: (goal: CreateLearningGoal) => learningGoalService.createGoal(goal),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learningGoals'] })
      queryClient.invalidateQueries({ queryKey: ['goalsSummary'] })
      toast.success('Goal created successfully! 🎯')
      setIsCreateDialogOpen(false)
      resetNewGoal()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create goal')
    }
  })

  // Delete goal mutation
  const deleteMutation = useMutation({
    mutationFn: (goalId: number) => learningGoalService.deleteGoal(goalId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learningGoals'] })
      queryClient.invalidateQueries({ queryKey: ['goalsSummary'] })
      toast.success('Goal deleted')
    }
  })

  const resetNewGoal = () => {
    setNewGoal({
      goal_type: 'vocabulary_count',
      priority: 'medium',
      target_metrics: {}
    })
  }

  const handleCreateGoal = () => {
    if (!newGoal.goal_title || !newGoal.start_date || !newGoal.target_date) {
      toast.error('Please fill in all required fields')
      return
    }

    createMutation.mutate(newGoal as CreateLearningGoal)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'completed': return 'bg-blue-100 text-blue-800'
      case 'paused': return 'bg-yellow-100 text-yellow-800'
      case 'abandoned': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-red-600'
      case 'high': return 'text-orange-600'
      case 'medium': return 'text-blue-600'
      case 'low': return 'text-gray-600'
      default: return 'text-gray-600'
    }
  }


  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Learning Goals 🎯</h1>
          <p className="text-gray-600 mt-1">Track your learning objectives and progress</p>
        </div>
        <Button onClick={() => setIsCreateDialogOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create Goal
        </Button>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-green-600">Active</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{summary.active}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-blue-600">Completed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{summary.completed}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-green-600">On Track</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{summary.on_track}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-red-600">Behind</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{summary.behind}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-yellow-600">Paused</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{summary.paused}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Goals List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {isLoading ? (
          <div className="col-span-full text-center py-12">
            <p className="text-gray-500">Loading goals...</p>
          </div>
        ) : goals.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <Target className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No learning goals yet</h3>
            <p className="text-gray-600 mb-4">Create your first goal to start tracking progress!</p>
            <Button onClick={() => setIsCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create First Goal
            </Button>
          </div>
        ) : (
          goals.map((goal) => (
            <Card key={goal.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(goal.status)}`}>
                        {goal.status}
                      </span>
                      <span className={`text-sm font-medium ${getPriorityColor(goal.priority)}`}>
                        {goal.priority}
                      </span>
                    </div>
                    <CardTitle className="text-lg">{goal.goal_title}</CardTitle>
                    <CardDescription className="mt-1">{goal.description}</CardDescription>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      if (confirm('Delete this goal?')) {
                        deleteMutation.mutate(goal.id)
                      }
                    }}
                  >
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Progress Bar */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Progress</span>
                    <span className="text-sm font-bold text-gray-900">{goal.completion_percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        goal.is_on_track ? 'bg-green-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${goal.completion_percentage}%` }}
                    />
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-gray-400" />
                    <div>
                      <p className="text-gray-600">Target Date</p>
                      <p className="font-medium">{formatDate(goal.target_date)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-gray-400" />
                    <div>
                      <p className="text-gray-600">Days Remaining</p>
                      <p className="font-medium">{getDaysDifference(goal.target_date)} days</p>
                    </div>
                  </div>
                </div>

                {/* On Track Status */}
                <div className="flex items-center gap-2">
                  {goal.is_on_track ? (
                    <>
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                      <span className="text-sm text-green-700 font-medium">On track!</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="h-5 w-5 text-red-500" />
                      <span className="text-sm text-red-700 font-medium">
                        {goal.days_behind} days behind
                      </span>
                    </>
                  )}
                </div>

                {/* Target Metrics */}
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Target</p>
                  <p className="text-sm font-medium">
                    {JSON.stringify(goal.target_metrics)}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Create Goal Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create New Learning Goal 🎯</DialogTitle>
            <DialogDescription>
              Set a clear objective to track your progress
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Goal Title */}
            <div>
              <Label htmlFor="title">Goal Title *</Label>
              <Input
                id="title"
                placeholder="e.g., Learn 500 Business Words"
                value={newGoal.goal_title || ''}
                onChange={(e) => setNewGoal({ ...newGoal, goal_title: e.target.value })}
              />
            </div>

            {/* Goal Type */}
            <div>
              <Label htmlFor="type">Goal Type *</Label>
              <Select
                value={newGoal.goal_type}
                onValueChange={(value) => setNewGoal({ ...newGoal, goal_type: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="vocabulary_count">Vocabulary Count</SelectItem>
                  <SelectItem value="quiz_score">Quiz Score Target</SelectItem>
                  <SelectItem value="exam_preparation">Exam Preparation</SelectItem>
                  <SelectItem value="time_based">Time-Based Practice</SelectItem>
                  <SelectItem value="topic_mastery">Topic Mastery</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Description */}
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Describe your goal..."
                value={newGoal.description || ''}
                onChange={(e) => setNewGoal({ ...newGoal, description: e.target.value })}
              />
            </div>

            {/* Target Metrics (Dynamic based on goal_type) */}
            <div>
              <Label>Target Metrics *</Label>
              {newGoal.goal_type === 'vocabulary_count' && (
                <div className="flex gap-2">
                  <Input
                    type="number"
                    placeholder="500"
                    onChange={(e) => setNewGoal({
                      ...newGoal,
                      target_metrics: { vocabulary: parseInt(e.target.value), unit: 'words' }
                    })}
                  />
                  <span className="flex items-center text-sm text-gray-600">words</span>
                </div>
              )}
              {newGoal.goal_type === 'quiz_score' && (
                <Input
                  type="number"
                  placeholder="85"
                  onChange={(e) => setNewGoal({
                    ...newGoal,
                    target_metrics: { target_score: parseInt(e.target.value), unit: 'percentage' }
                  })}
                />
              )}
              {newGoal.goal_type === 'exam_preparation' && (
                <div className="space-y-2">
                  <Input
                    placeholder="Exam name (e.g., IELTS)"
                    onChange={(e) => setNewGoal({
                      ...newGoal,
                      target_metrics: {
                        ...newGoal.target_metrics,
                        exam: e.target.value
                      }
                    })}
                  />
                  <Input
                    type="number"
                    step="0.5"
                    placeholder="Target score (e.g., 6.5)"
                    onChange={(e) => setNewGoal({
                      ...newGoal,
                      target_metrics: {
                        ...newGoal.target_metrics,
                        target_score: parseFloat(e.target.value)
                      }
                    })}
                  />
                </div>
              )}
            </div>

            {/* Dates */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="start_date">Start Date *</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={newGoal.start_date || ''}
                  onChange={(e) => setNewGoal({ ...newGoal, start_date: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="target_date">Target Date *</Label>
                <Input
                  id="target_date"
                  type="date"
                  value={newGoal.target_date || ''}
                  onChange={(e) => setNewGoal({ ...newGoal, target_date: e.target.value })}
                />
              </div>
            </div>

            {/* Priority */}
            <div>
              <Label htmlFor="priority">Priority</Label>
              <Select
                value={newGoal.priority}
                onValueChange={(value) => setNewGoal({ ...newGoal, priority: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="urgent">Urgent</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateGoal} disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Goal'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

