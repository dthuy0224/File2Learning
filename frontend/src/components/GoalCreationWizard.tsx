import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle2, ArrowRight, ArrowLeft, Target, Calendar, TrendingUp } from 'lucide-react'
import { CreateLearningGoal } from '@/services/learningGoalService'

interface GoalCreationWizardProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (goal: CreateLearningGoal) => Promise<void>
}

type WizardStep = 1 | 2 | 3 | 4

export default function GoalCreationWizard({ isOpen, onClose, onSubmit }: GoalCreationWizardProps) {
  const [currentStep, setCurrentStep] = useState<WizardStep>(1)
  const [goalData, setGoalData] = useState<Partial<CreateLearningGoal>>({
    goal_type: 'vocabulary_count',
    priority: 'medium',
    target_metrics: {}
  })

  const handleNext = () => {
    if (currentStep < 4) {
      setCurrentStep((prev) => (prev + 1) as WizardStep)
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => (prev - 1) as WizardStep)
    }
  }

  const handleSubmit = async () => {
    if (!goalData.goal_title || !goalData.start_date || !goalData.target_date) {
      return
    }
    await onSubmit(goalData as CreateLearningGoal)
    // Reset wizard
    setCurrentStep(1)
    setGoalData({
      goal_type: 'vocabulary_count',
      priority: 'medium',
      target_metrics: {}
    })
  }

  const updateGoalData = (field: keyof CreateLearningGoal, value: any) => {
    setGoalData(prev => ({ ...prev, [field]: value }))
  }

  const updateTargetMetrics = (field: string, value: any) => {
    setGoalData(prev => ({
      ...prev,
      target_metrics: { ...prev.target_metrics, [field]: value }
    }))
  }

  const getStepTitle = () => {
    switch (currentStep) {
      case 1: return 'Choose Goal Type'
      case 2: return 'Set Target'
      case 3: return 'Timeline'
      case 4: return 'Review & Create'
      default: return ''
    }
  }

  const isStepValid = () => {
    switch (currentStep) {
      case 1:
        return !!goalData.goal_type
      case 2:
        if (goalData.goal_type === 'vocabulary_count') {
          return !!goalData.target_metrics?.vocabulary
        } else if (goalData.goal_type === 'exam_preparation') {
          return !!goalData.target_metrics?.exam && !!goalData.target_metrics?.target_score
        } else if (goalData.goal_type === 'quiz_score') {
          return !!goalData.target_metrics?.target_score
        } else if (goalData.goal_type === 'time_based') {
          return !!goalData.target_metrics?.study_time
        }
        return true
      case 3:
        return !!goalData.start_date && !!goalData.target_date
      case 4:
        return !!goalData.goal_title
      default:
        return false
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Target className="w-6 h-6 text-indigo-600" />
            Create Learning Goal - Step {currentStep} of 4
          </DialogTitle>
          <DialogDescription>{getStepTitle()}</DialogDescription>
        </DialogHeader>

        {/* Progress Steps */}
        <div className="flex items-center justify-between mb-6">
          {[1, 2, 3, 4].map((step) => (
            <div key={step} className="flex items-center flex-1">
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    step <= currentStep
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {step < currentStep ? (
                    <CheckCircle2 className="w-6 h-6" />
                  ) : (
                    <span>{step}</span>
                  )}
                </div>
                <span className="text-xs mt-1 text-gray-600">
                  {step === 1 && 'Type'}
                  {step === 2 && 'Target'}
                  {step === 3 && 'Timeline'}
                  {step === 4 && 'Review'}
                </span>
              </div>
              {step < 4 && (
                <div
                  className={`flex-1 h-1 mx-2 ${
                    step < currentStep ? 'bg-indigo-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step Content */}
        <div className="space-y-4">
          {/* Step 1: Goal Type */}
          {currentStep === 1 && (
            <div className="space-y-4">
              <Label>What type of goal do you want to achieve?</Label>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { value: 'vocabulary_count', label: 'Vocabulary Count', icon: '📚' },
                  { value: 'exam_preparation', label: 'Exam Preparation', icon: '📝' },
                  { value: 'quiz_score', label: 'Quiz Score Target', icon: '🎯' },
                  { value: 'time_based', label: 'Time-Based Practice', icon: '⏰' },
                  { value: 'topic_mastery', label: 'Topic Mastery', icon: '🌟' },
                  { value: 'fluency', label: 'Fluency', icon: '💬' }
                ].map((type) => (
                  <Card
                    key={type.value}
                    className={`cursor-pointer transition-all ${
                      goalData.goal_type === type.value
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'hover:border-gray-300'
                    }`}
                    onClick={() => updateGoalData('goal_type', type.value)}
                  >
                    <CardContent className="p-4 text-center">
                      <div className="text-3xl mb-2">{type.icon}</div>
                      <div className="font-medium">{type.label}</div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: Target Metrics */}
          {currentStep === 2 && (
            <div className="space-y-4">
              {goalData.goal_type === 'vocabulary_count' && (
                <div>
                  <Label>How many words do you want to learn?</Label>
                  <div className="flex gap-2 mt-2">
                    <Input
                      type="number"
                      placeholder="500"
                      value={goalData.target_metrics?.vocabulary || ''}
                      onChange={(e) => updateTargetMetrics('vocabulary', parseInt(e.target.value))}
                    />
                    <span className="flex items-center text-sm text-gray-600">words</span>
                  </div>
                </div>
              )}

              {goalData.goal_type === 'exam_preparation' && (
                <div className="space-y-4">
                  <div>
                    <Label>Exam Name</Label>
                    <Input
                      placeholder="e.g., IELTS, TOEIC, TOEFL"
                      value={goalData.target_metrics?.exam || ''}
                      onChange={(e) => updateTargetMetrics('exam', e.target.value)}
                    />
                  </div>
                  <div>
                    <Label>Target Score</Label>
                    <Input
                      type="number"
                      step="0.5"
                      placeholder="6.5"
                      value={goalData.target_metrics?.target_score || ''}
                      onChange={(e) => updateTargetMetrics('target_score', parseFloat(e.target.value))}
                    />
                  </div>
                </div>
              )}

              {goalData.goal_type === 'quiz_score' && (
                <div>
                  <Label>Target Average Score (%)</Label>
                  <Input
                    type="number"
                    placeholder="85"
                    value={goalData.target_metrics?.target_score || ''}
                    onChange={(e) => updateTargetMetrics('target_score', parseInt(e.target.value))}
                  />
                </div>
              )}

              {goalData.goal_type === 'time_based' && (
                <div>
                  <Label>Total Study Hours</Label>
                  <Input
                    type="number"
                    placeholder="50"
                    value={goalData.target_metrics?.study_time || ''}
                    onChange={(e) => updateTargetMetrics('study_time', parseInt(e.target.value))}
                  />
                </div>
              )}

              {goalData.goal_type === 'topic_mastery' && (
                <div className="space-y-4">
                  <div>
                    <Label>Topic</Label>
                    <Input
                      placeholder="e.g., Grammar, Business English"
                      value={goalData.target_metrics?.topic || ''}
                      onChange={(e) => updateTargetMetrics('topic', e.target.value)}
                    />
                  </div>
                  <div>
                    <Label>Target Accuracy (%)</Label>
                    <Input
                      type="number"
                      placeholder="85"
                      value={goalData.target_metrics?.target_accuracy || ''}
                      onChange={(e) => updateTargetMetrics('target_accuracy', parseInt(e.target.value))}
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 3: Timeline */}
          {currentStep === 3 && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="start_date">Start Date *</Label>
                  <Input
                    id="start_date"
                    type="date"
                    value={goalData.start_date || ''}
                    onChange={(e) => updateGoalData('start_date', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="target_date">Target Date *</Label>
                  <Input
                    id="target_date"
                    type="date"
                    value={goalData.target_date || ''}
                    onChange={(e) => updateGoalData('target_date', e.target.value)}
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="priority">Priority</Label>
                <Select
                  value={goalData.priority}
                  onValueChange={(value) => updateGoalData('priority', value)}
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
          )}

          {/* Step 4: Review */}
          {currentStep === 4 && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="goal_title">Goal Title *</Label>
                <Input
                  id="goal_title"
                  placeholder="e.g., Learn 500 Business Words"
                  value={goalData.goal_title || ''}
                  onChange={(e) => updateGoalData('goal_title', e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Add more details about your goal..."
                  value={goalData.description || ''}
                  onChange={(e) => updateGoalData('description', e.target.value)}
                />
              </div>

              {/* Summary Card */}
              <Card className="bg-gray-50">
                <CardHeader>
                  <CardTitle className="text-lg">Goal Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-medium">{goalData.goal_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Target:</span>
                    <span className="font-medium">
                      {JSON.stringify(goalData.target_metrics)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Start:</span>
                    <span className="font-medium">{goalData.start_date}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Target Date:</span>
                    <span className="font-medium">{goalData.target_date}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Priority:</span>
                    <span className="font-medium">{goalData.priority}</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-6">
          <Button
            variant="outline"
            onClick={currentStep === 1 ? onClose : handleBack}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            {currentStep === 1 ? 'Cancel' : 'Back'}
          </Button>
          {currentStep < 4 ? (
            <Button onClick={handleNext} disabled={!isStepValid()}>
              Next
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={!isStepValid()}>
              <CheckCircle2 className="w-4 h-4 mr-2" />
              Create Goal
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

