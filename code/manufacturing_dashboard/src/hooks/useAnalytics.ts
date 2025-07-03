import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { analyticsService, llmService, detectAnomalies } from '../services/api';
import { AnalyticsSummary, Recommendation, Anomaly } from '../types';

// Query keys
const QUERY_KEYS = {
  analytics: {
    summary: ['analytics', 'summary'] as const,
    allData: ['analytics', 'allData'] as const,
    status: ['analytics', 'status'] as const,
    files: ['analytics', 'files'] as const,
  },
  recommendations: {
    latest: ['recommendations', 'latest'] as const,
    history: (days: number) => ['recommendations', 'history', days] as const,
    byId: (id: string) => ['recommendations', id] as const,
  },
  anomalies: ['anomalies'] as const,
};

// Analytics hooks
export const useAnalyticsSummary = () => {
  return useQuery({
    queryKey: QUERY_KEYS.analytics.summary,
    queryFn: analyticsService.getSummary,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
  });
};

export const useAnalyticsData = () => {
  return useQuery({
    queryKey: QUERY_KEYS.analytics.allData,
    queryFn: analyticsService.getAllData,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

export const useAnalyticsStatus = () => {
  return useQuery({
    queryKey: QUERY_KEYS.analytics.status,
    queryFn: analyticsService.getStatus,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 30 * 1000, // Poll every 30 seconds
  });
};

export const useRunAnalytics = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (force: boolean = false) => analyticsService.runAnalytics(force),
    onSuccess: () => {
      // Invalidate all analytics queries to refetch fresh data
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.anomalies });
    },
  });
};

export const useLatestRecommendation = () => {
  return useQuery({
    queryKey: QUERY_KEYS.recommendations.latest,
    queryFn: async () => {
      try {
        return await llmService.getLatestRecommendation();
      } catch (error: any) {
        // Se è un 404, restituisci null invece di lanciare l'errore
        if (error?.response?.status === 404) {
          console.log('No recommendations found yet - this is normal for new installations');
          return null;
        }
        // Per altri errori, rilancia
        throw error;
      }
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    retry: (failureCount, error: any) => {
      // Non fare retry su 404
      if (error?.response?.status === 404) return false;
      return failureCount < 3;
    },
  });
};

export const useRecommendationHistory = (days: number = 7) => {
  return useQuery({
    queryKey: QUERY_KEYS.recommendations.history(days),
    queryFn: () => llmService.getRecommendationHistory(days),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

export const useGenerateRecommendation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (customPrompt?: string) => llmService.generateRecommendation(customPrompt),
    onSuccess: (data) => {
      // Update the latest recommendation cache
      queryClient.setQueryData(QUERY_KEYS.recommendations.latest, data);
      // Invalidate history to include the new recommendation
      queryClient.invalidateQueries({ 
        queryKey: ['recommendations', 'history'] 
      });
    },
  });
};

// Anomalies hook
export const useAnomalies = () => {
  const { data: analyticsData } = useAnalyticsData();
  
  return useQuery({
    queryKey: QUERY_KEYS.anomalies,
    queryFn: () => {
      if (!analyticsData) return [];
      return detectAnomalies(analyticsData);
    },
    enabled: !!analyticsData,
    staleTime: 1 * 60 * 1000, // 1 minute
  });
};

// Combined dashboard data hook
export const useDashboardData = () => {
  const summary = useAnalyticsSummary();
  const data = useAnalyticsData();
  const anomalies = useAnomalies();
  const recommendation = useLatestRecommendation();
  const status = useAnalyticsStatus();

  const isLoading = summary.isLoading || data.isLoading;
  const isError = summary.isError || data.isError;
  const error = summary.error || data.error;

  return {
    summary: summary.data,
    analyticsData: data.data,
    anomalies: anomalies.data || [],
    recommendation: recommendation.data,
    status: status.data,
    isLoading,
    isError,
    error,
    refetch: () => {
      summary.refetch();
      data.refetch();
      anomalies.refetch();
      recommendation.refetch();
      status.refetch();
    },
  };
};