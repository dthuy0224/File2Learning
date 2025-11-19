import { QueryClient } from '@tanstack/react-query'

const PROGRESS_QUERY_KEYS: Array<unknown[]> = [
  ['userStats'],
  ['activityHeatmap'],
  ['performanceHistory'],
  ['skillBreakdown'],
  ['recentActivities'],
  ['fullProgress'],
]

interface InvalidationOptions {
  includeTodayPlan?: boolean
}

export const invalidateProgressQueries = (
  queryClient: QueryClient,
  options?: InvalidationOptions
) => {
  PROGRESS_QUERY_KEYS.forEach((key) => {
    queryClient.invalidateQueries({ queryKey: key })
  })

  if (options?.includeTodayPlan) {
    queryClient.invalidateQueries({ queryKey: ['todayPlan'] })
  }
}

