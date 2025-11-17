import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Flame, BrainCircuit, Target, Clock, TrendingUp, Calendar, Activity, Award, Loader2 } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts'
import CalendarHeatmap from 'react-calendar-heatmap'
import 'react-calendar-heatmap/dist/styles.css'
import {
  useUserStats,
  useActivityHeatmap,
  usePerformanceHistory,
  useSkillBreakdown,
  useRecentActivities
} from '@/hooks/useProgress'

const ProgressPage = () => {
  const [timeRange, setTimeRange] = useState('30d')

  // Convert time range to days for API
  const rangeDays = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : timeRange === '90d' ? 90 : 365

  // Heatmap styles
  const heatmapStyles = `
    .react-calendar-heatmap .color-empty { fill: #f8fafc; stroke: #e2e8f0; }
    .react-calendar-heatmap .color-scale-1 { fill: #dcfce7; stroke: #16a34a; }
    .react-calendar-heatmap .color-scale-2 { fill: #bbf7d0; stroke: #16a34a; }
    .react-calendar-heatmap .color-scale-3 { fill: #4ade80; stroke: #15803d; }
    .react-calendar-heatmap .color-scale-4 { fill: #16a34a; stroke: #15803d; }
    .react-calendar-heatmap rect { rx: 2; }
    .react-calendar-heatmap .tooltip { position: relative; }
  `

  // Fetch data from APIs
  const { data: stats, isLoading: statsLoading } = useUserStats(rangeDays)
  const { data: activityHeatmap, isLoading: heatmapLoading } = useActivityHeatmap(rangeDays)
  const { data: performanceHistory, isLoading: performanceLoading } = usePerformanceHistory(rangeDays)
  const { data: skillBreakdown, isLoading: skillLoading } = useSkillBreakdown(rangeDays)
  const { data: recentActivities, isLoading: activitiesLoading } = useRecentActivities(10)

  // Map skill breakdown data for chart
  const skillChartData = skillBreakdown?.map(item => ({
    level: item.level,
    accuracy: item.accuracy,
    color: item.level === 'Easy' ? '#22c55e' : item.level === 'Medium' ? '#f59e0b' : '#ef4444'
  })) || []

  // Transform heatmap data for react-calendar-heatmap
  const heatmapData = activityHeatmap?.map(item => ({
    date: item.date,
    count: item.count
  })) || []

  // Get date range for heatmap (90 days back from today)
  const today = new Date()
  const startDate = new Date(today)
  startDate.setDate(today.getDate() - 90)

  // Custom color function for heatmap
  const getHeatmapColor = (value: any) => {
    if (!value || !value.count || value.count === 0) return 'color-empty'
    if (value.count <= 2) return 'color-scale-1'
    if (value.count <= 4) return 'color-scale-2'
    if (value.count <= 6) return 'color-scale-3'
    return 'color-scale-4'
  }

  const handleTimeRangeChange = (value: string) => {
    setTimeRange(value)
  }

  return (
    <div className="container mx-auto px-6 py-8 space-y-8">
      <style>{heatmapStyles}</style>
      {/* Header Section */}
      <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Your Learning Progress Report</h1>
          <p className="text-muted-foreground">
            Track your progress, discover your strengths and weaknesses through daily learning.
          </p>
        </div>

        {/* Time Range Filter */}
        <div className="flex items-center space-x-2">
          <Calendar className="h-4 w-4 text-muted-foreground" />
          <Select value={timeRange} onValueChange={handleTimeRangeChange}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Select time range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">This week</SelectItem>
              <SelectItem value="30d">This month</SelectItem>
              <SelectItem value="90d">3 months ago</SelectItem>
              <SelectItem value="all">All time</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* KPIs Section */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="relative overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Learning Streak</CardTitle>
            <Flame className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <div className="flex items-center justify-center h-12">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold">{stats?.study_streak || 0} days</div>
                <p className="text-xs text-muted-foreground">
                  Continuous learning streak. Keep it up!
                </p>
              </>
            )}
          </CardContent>
          <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-orange-100 to-orange-200 rounded-full -translate-y-8 translate-x-8 opacity-20" />
        </Card>

        <Card className="relative overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Words Mastered</CardTitle>
            <BrainCircuit className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <div className="flex items-center justify-center h-12">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold">{stats?.words_mastered || 0} words</div>
                <p className="text-xs text-muted-foreground">
                  Number of words in the flashcard deck that have been mastered.
                </p>
              </>
            )}
          </CardContent>
          <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-purple-100 to-purple-200 rounded-full -translate-y-8 translate-x-8 opacity-20" />
        </Card>

        <Card className="relative overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Accuracy</CardTitle>
            <Target className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <div className="flex items-center justify-center h-12">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold">{stats?.avg_accuracy || 0}%</div>
                <p className="text-xs text-muted-foreground">
                  Average accuracy in quiz attempts.
                </p>
              </>
            )}
          </CardContent>
          <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-green-100 to-green-200 rounded-full -translate-y-8 translate-x-8 opacity-20" />
        </Card>

        <Card className="relative overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Study Time</CardTitle>
            <Clock className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <div className="flex items-center justify-center h-12">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold">{stats?.total_study_time || 0} minutes</div>
                <p className="text-xs text-muted-foreground">
                  Total time spent studying and reviewing.
                </p>
              </>
            )}
          </CardContent>
          <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full -translate-y-8 translate-x-8 opacity-20" />
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Activity Heatmap */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Learning Activities
            </CardTitle>
            <CardDescription>
              Your level of dedication through each day
            </CardDescription>
          </CardHeader>
          <CardContent>
            {heatmapLoading ? (
              <div className="flex items-center justify-center h-48">
                <Loader2 className="h-8 w-8 animate-spin" />
              </div>
            ) : (
              <div className="space-y-4">
                {/* Legend */}
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>Less</span>
                  <div className="flex items-center space-x-1">
                    <div className="w-3 h-3 rounded-sm bg-slate-100 border"></div>
                    <div className="w-3 h-3 rounded-sm bg-green-200"></div>
                    <div className="w-3 h-3 rounded-sm bg-green-400"></div>
                    <div className="w-3 h-3 rounded-sm bg-green-600"></div>
                    <div className="w-3 h-3 rounded-sm bg-green-800"></div>
                  </div>
                  <span>More</span>
                </div>

                {/* Heatmap */}
                <div className="overflow-x-auto">
                  <CalendarHeatmap
                    startDate={startDate}
                    endDate={today}
                    values={heatmapData}
                    classForValue={getHeatmapColor}
                    showWeekdayLabels={true}
                    transformDayElement={(element: any, value: any, index: number) => (
                      <div
                        key={index}
                        className={`
                          ${value && value.count > 0 ? 'cursor-pointer hover:scale-110 transition-transform' : ''}
                          tooltip
                        `}
                        title={value ? `${value.count} activities on ${value.date}` : 'No data'}
                      >
                        {element}
                      </div>
                    )}
                  />
                </div>

                {/* Summary stats */}
                {heatmapData.length > 0 && (
                  <div className="text-sm text-muted-foreground">
                    Total active days: {heatmapData.filter(d => d.count > 0).length} / {heatmapData.length}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Performance Over Time */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Performance Over Time
            </CardTitle>
            <CardDescription>
              Your progress through each day of learning
            </CardDescription>
          </CardHeader>
          <CardContent>
            {performanceLoading ? (
              <div className="flex items-center justify-center h-48">
                <Loader2 className="h-8 w-8 animate-spin" />
              </div>
            ) : performanceHistory && performanceHistory.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={performanceHistory}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => new Date(value).toLocaleDateString('vi-VN', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                  <Tooltip
                    labelFormatter={(value) => new Date(value).toLocaleDateString('vi-VN')}
                    formatter={(value: number) => [`${value}%`, 'Accuracy']}
                  />
                  <Line
                    type="monotone"
                    dataKey="accuracy"
                    stroke="#22c55e"
                    strokeWidth={2}
                    dot={{ fill: '#22c55e', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-48 text-muted-foreground">
                <div className="text-center">
                  <TrendingUp className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No performance data</p>
                  <p className="text-sm">Complete a few quizzes to see the chart</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Skill Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5" />
            Skill Analysis
          </CardTitle>
          <CardDescription>
            Your strengths and weaknesses by difficulty level
          </CardDescription>
        </CardHeader>
        <CardContent>
          {skillLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
          ) : skillChartData && skillChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={skillChartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis dataKey="level" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(value: number) => [`${value}%`, 'Accuracy']} />
                <Bar dataKey="accuracy" radius={[4, 4, 0, 0]}>
                  {skillChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-muted-foreground">
              <div className="text-center">
                <Award className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No skill analysis data</p>
                <p className="text-sm">Complete quizzes with different difficulty levels to see the analysis</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Activities */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activities</CardTitle>
          <CardDescription>
            Your recent learning activities
          </CardDescription>
        </CardHeader>
        <CardContent>
          {activitiesLoading ? (
            <div className="flex items-center justify-center h-32">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          ) : recentActivities && recentActivities.length > 0 ? (
            <div className="space-y-4">
              {recentActivities.map((activity, index) => {
                const IconComponent = activity.type === 'quiz' ? Target :
                                    activity.type === 'flashcard' ? BrainCircuit : Activity
                return (
                  <div
                    key={`${activity.id ?? 'activity'}-${index}`}
                    className="flex items-center space-x-4 p-4 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors"
                  >
                    <div className={`p-2 rounded-full ${
                      activity.type === 'quiz' ? 'bg-green-100 text-green-600' :
                      activity.type === 'flashcard' ? 'bg-purple-100 text-purple-600' :
                      'bg-blue-100 text-blue-600'
                    }`}>
                      <IconComponent className="h-4 w-4" />
                    </div>

                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {activity.title}
                      </p>
                      {activity.score && (
                        <p className="text-sm text-muted-foreground">
                          {activity.score}
                        </p>
                      )}
                    </div>

                    <div className="text-sm text-muted-foreground">
                      {activity.time_ago}
                    </div>

                    <span className="ml-auto px-2 py-1 text-xs rounded-full border bg-background text-muted-foreground">
                      {activity.type === 'quiz' ? 'Quiz' :
                       activity.type === 'flashcard' ? 'Flashcard' : 'Document'}
                    </span>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="flex items-center justify-center h-32 text-muted-foreground">
              <div className="text-center">
                <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No activities</p>
                <p className="text-sm">Start learning to see your recent activities</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default ProgressPage
