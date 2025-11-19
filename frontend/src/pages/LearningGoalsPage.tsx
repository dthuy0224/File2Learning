import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Target, Plus, Calendar, CheckCircle2, AlertCircle, Clock, Trash2, TrendingUp, Sparkles } from 'lucide-react'
import { toast } from 'react-hot-toast'
import learningGoalService, { CreateLearningGoal, LearningGoal } from '@/services/learningGoalService'
import GoalCreationWizard from '@/components/GoalCreationWizard'

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
      toast.success('Goal created successfully! 🎯 Milestones auto-generated!')
      setIsCreateDialogOpen(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create goal')
    }
  })

  // Generate milestones mutation
  const generateMilestonesMutation = useMutation({
    mutationFn: (goalId: number) => learningGoalService.generateMilestones(goalId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learningGoals'] })
      toast.success('Milestones generated successfully! ✨')
    },
    onError: () => {
      toast.error('Failed to generate milestones')
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

  const handleCreateGoal = async (goal: CreateLearningGoal) => {
    await createMutation.mutateAsync(goal)
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

      {/* Goal Creation Wizard */}
      <GoalCreationWizard
        isOpen={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
        onSubmit={handleCreateGoal}
      />

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

                {/* Milestones Preview */}
                {goal.milestones && goal.milestones.length > 0 && (
                  <div className="mt-4">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-medium text-gray-700">Milestones</p>
                      <span className="text-xs text-gray-500">
                        {goal.milestones.filter((m: any) => m.status === 'completed').length} / {goal.milestones.length} completed
                      </span>
                    </div>
                    <div className="space-y-1">
                      {goal.milestones.slice(0, 3).map((milestone: any, idx: number) => (
                        <div key={idx} className="flex items-center gap-2 text-xs">
                          <div className={`w-2 h-2 rounded-full ${
                            milestone.status === 'completed' ? 'bg-green-500' :
                            milestone.status === 'in_progress' ? 'bg-yellow-500' :
                            'bg-gray-300'
                          }`} />
                          <span className="text-gray-600">
                            Week {milestone.week}: {milestone.target}
                          </span>
                        </div>
                      ))}
                      {goal.milestones.length > 3 && (
                        <p className="text-xs text-gray-500">+{goal.milestones.length - 3} more milestones</p>
                      )}
                    </div>
                  </div>
                )}

                {/* Generate Milestones Button */}
                {(!goal.milestones || goal.milestones.length === 0) && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full mt-2"
                    onClick={() => generateMilestonesMutation.mutate(goal.id)}
                    disabled={generateMilestonesMutation.isPending}
                  >
                    <Sparkles className="w-4 h-4 mr-2" />
                    {generateMilestonesMutation.isPending ? 'Generating...' : 'Generate Milestones'}
                  </Button>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}

