import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Sparkles, RefreshCw, TrendingUp, CheckCircle2, XCircle, 
  Eye, Clock, Target, AlertCircle, Calendar 
} from 'lucide-react';
import toast from 'react-hot-toast';
import recommendationService, { 
  Recommendation, 
  RecommendationType, 
  RecommendationPriority 
} from '../services/recommendationService';
import dailyPlanService from '../services/dailyPlanService';

const RecommendationsPage = () => {
  const queryClient = useQueryClient();
  const [filterType, setFilterType] = useState<RecommendationType | 'all'>('all');
  const [filterPriority, setFilterPriority] = useState<RecommendationPriority | 'all'>('all');
  const [showActiveOnly, setShowActiveOnly] = useState(true);

  // Fetch recommendations
  const { data: recommendationsData, isLoading } = useQuery({
    queryKey: ['recommendations', filterType, filterPriority, showActiveOnly],
    queryFn: () => recommendationService.getRecommendations({
      active_only: showActiveOnly,
      type_filter: filterType === 'all' ? undefined : filterType,
      priority_filter: filterPriority === 'all' ? undefined : filterPriority,
      limit: 100
    })
  });

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ['recommendation-stats'],
    queryFn: () => recommendationService.getStats()
  });

  // Fetch today's plan to check which recommendations are included
  const { data: todayPlanData } = useQuery({
    queryKey: ['today-plan'],
    queryFn: () => dailyPlanService.getTodayPlan()
  });

  // Get list of recommendation IDs that are in today's plan
  const recommendationsInPlan = todayPlanData?.plan?.source_recommendation_ids || [];

  // Generate recommendations mutation
  const generateMutation = useMutation({
    mutationFn: () => recommendationService.generateRecommendations(10),
    onSuccess: (data) => {
      toast.success(data.message);
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      queryClient.invalidateQueries({ queryKey: ['recommendation-stats'] });
    },
    onError: () => {
      toast.error('Failed to generate recommendations');
    }
  });

  // Mark viewed mutation
  const viewedMutation = useMutation({
    mutationFn: (id: number) => recommendationService.markViewed(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    }
  });

  // Mark accepted mutation
  const acceptMutation = useMutation({
    mutationFn: (id: number) => recommendationService.markAccepted(id),
    onSuccess: () => {
      toast.success('Recommendation accepted!');
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      queryClient.invalidateQueries({ queryKey: ['recommendation-stats'] });
    }
  });

  // Mark dismissed mutation
  const dismissMutation = useMutation({
    mutationFn: (id: number) => recommendationService.markDismissed(id),
    onSuccess: () => {
      toast.success('Recommendation dismissed');
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      queryClient.invalidateQueries({ queryKey: ['recommendation-stats'] });
    }
  });

  const handleAccept = (rec: Recommendation) => {
    acceptMutation.mutate(rec.id);
  };

  const handleDismiss = (rec: Recommendation) => {
    dismissMutation.mutate(rec.id);
  };

  const handleView = (rec: Recommendation) => {
    if (!rec.is_viewed) {
      viewedMutation.mutate(rec.id);
    }
  };

  const getPriorityBadge = (priority: RecommendationPriority) => {
    const styles = {
      urgent: 'bg-red-100 text-red-800 border-red-300',
      high: 'bg-orange-100 text-orange-800 border-orange-300',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      low: 'bg-gray-100 text-gray-800 border-gray-300'
    };
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full border ${styles[priority]}`}>
        {priority.toUpperCase()}
      </span>
    );
  };

  const getTypeDisplay = (type: RecommendationType) => {
    return recommendationService.getTypeDisplay(type);
  };

  const isInTodayPlan = (recId: number) => {
    return recommendationsInPlan.includes(recId);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const recommendations = recommendationsData?.recommendations || [];
  const activeCount = recommendationsData?.active_count || 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Sparkles className="w-8 h-8 text-indigo-600" />
              Smart Recommendations
            </h1>
            <p className="mt-2 text-gray-600">
              AI-powered personalized learning suggestions based on your progress
            </p>
          </div>
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${generateMutation.isPending ? 'animate-spin' : ''}`} />
            Generate New
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active</p>
                <p className="text-2xl font-bold text-indigo-600">{stats.active_recommendations}</p>
              </div>
              <Target className="w-8 h-8 text-indigo-600" />
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Accepted</p>
                <p className="text-2xl font-bold text-green-600">{stats.accepted_count}</p>
              </div>
              <CheckCircle2 className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Acceptance Rate</p>
                <p className="text-2xl font-bold text-purple-600">{stats.acceptance_rate.toFixed(0)}%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-600" />
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Generated</p>
                <p className="text-2xl font-bold text-gray-700">{stats.total_generated}</p>
              </div>
              <Sparkles className="w-8 h-8 text-gray-700" />
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6 border border-gray-200">
        <div className="flex flex-wrap gap-4 items-center">
          <div>
            <label className="text-sm font-medium text-gray-700 mr-2">Show:</label>
            <button
              onClick={() => setShowActiveOnly(!showActiveOnly)}
              className={`px-3 py-1 rounded ${
                showActiveOnly ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              {showActiveOnly ? 'Active Only' : 'All'}
            </button>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Type:</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as RecommendationType | 'all')}
              className="px-3 py-1 border border-gray-300 rounded"
            >
              <option value="all">All Types</option>
              {Object.values(RecommendationType).map((type) => (
                <option key={type} value={type}>
                  {getTypeDisplay(type).label}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Priority:</label>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value as RecommendationPriority | 'all')}
              className="px-3 py-1 border border-gray-300 rounded"
            >
              <option value="all">All Priorities</option>
              {Object.values(RecommendationPriority).map((priority) => (
                <option key={priority} value={priority}>
                  {priority.toUpperCase()}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Recommendations List */}
      {recommendations.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center border border-gray-200">
          <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No recommendations yet</h3>
          <p className="text-gray-600 mb-6">
            Click "Generate New" to get personalized recommendations based on your learning activity
          </p>
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Generate Recommendations
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec) => {
            const typeDisplay = getTypeDisplay(rec.type);
            return (
              <div
                key={rec.id}
                onClick={() => handleView(rec)}
                className={`bg-white rounded-lg shadow p-6 border-l-4 ${
                  rec.is_dismissed
                    ? 'opacity-50 border-gray-400'
                    : rec.is_accepted
                    ? 'border-green-500'
                    : `border-${typeDisplay.color}-500`
                } hover:shadow-md transition-shadow cursor-pointer`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">{typeDisplay.icon}</span>
                      <h3 className="text-lg font-semibold text-gray-900">{rec.title}</h3>
                      {getPriorityBadge(rec.priority)}
                      {!rec.is_viewed && (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          NEW
                        </span>
                      )}
                      {isInTodayPlan(rec.id) && (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 border border-green-300 flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          In Today's Plan
                        </span>
                      )}
                    </div>
                    {rec.description && (
                      <p className="text-gray-700 mb-2">{rec.description}</p>
                    )}
                    {rec.reason && (
                      <p className="text-sm text-gray-500 italic mb-4">💡 {rec.reason}</p>
                    )}
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      {rec.is_viewed && (
                        <span className="flex items-center gap-1">
                          <Eye className="w-4 h-4" />
                          Viewed
                        </span>
                      )}
                      {rec.is_accepted && (
                        <span className="flex items-center gap-1 text-green-600">
                          <CheckCircle2 className="w-4 h-4" />
                          Accepted
                        </span>
                      )}
                      {rec.is_dismissed && (
                        <span className="flex items-center gap-1 text-gray-600">
                          <XCircle className="w-4 h-4" />
                          Dismissed
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {new Date(rec.created_at).toLocaleDateString()}
                      </span>
                      <span>
                        Impact: {(rec.expected_impact * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  {!rec.is_accepted && !rec.is_dismissed && (
                    <div className="flex gap-2 ml-4">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAccept(rec);
                        }}
                        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                      >
                        Accept
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDismiss(rec);
                        }}
                        className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 text-sm"
                      >
                        Dismiss
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default RecommendationsPage;

