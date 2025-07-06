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
  return useQuery(
    QUERY_KEYS.analytics.summary,
    analyticsService.getSummary,
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000,
    }
  );
};

export const useAnalyticsData = () => {
  return useQuery(
    QUERY_KEYS.analytics.allData,
    analyticsService.getAllData,
    {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
    }
  );
};

export const useAnalyticsStatus = () => {
  return useQuery(
    QUERY_KEYS.analytics.status,
    analyticsService.getStatus,
    {
      staleTime: 30 * 1000, // 30 seconds
      refetchInterval: 30 * 1000, // Poll every 30 seconds
    }
  );
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
  const query = useQuery({
    queryKey: QUERY_KEYS.recommendations.latest,
    queryFn: llmService.getLatestRecommendation,
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 1,
  });
  
  return query; // React Query già espone refetch
};

export const useRecommendationHistory = (days: number = 7) => {
  return useQuery(
    QUERY_KEYS.recommendations.history(days),
    () => llmService.getRecommendationHistory(days),
    {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
    }
  );
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

  return useQuery(
    QUERY_KEYS.anomalies,
    () => {
      if (!analyticsData) return [];
      return detectAnomalies(analyticsData);
    },
    {
      enabled: !!analyticsData,
      staleTime: 1 * 60 * 1000, // 1 minute
    }
  );
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

export const useExecuteMcpAction = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (payload: { action: string; parameters: Record<string, any> }) => {
      try {
        const response = await llmService.executeMcpAction(payload.action, payload.parameters);
        return response;
      } catch (error: any) {
        // Gestione specifica per errori di validazione
        if (error.response?.status === 404) {
          const errorDetail = error.response.data.detail;
          
          // Se l'errore contiene suggerimenti di ID validi
          if (errorDetail.available_order_ids_sample) {
            throw new Error(
              `Order "${errorDetail.error}". ` +
              `Available orders: ${errorDetail.available_order_ids_sample.join(', ')}. ` +
              `Please refresh the analysis to get current data.`
            );
          }
          
          throw new Error(errorDetail.message || errorDetail.error || 'Resource not found');
        }
        
        // Altri errori
        throw new Error(
          error.response?.data?.message || 
          error.message || 
          'Failed to execute action'
        );
      }
    },
    onError: (error: Error) => {
      // Log dell'errore per debugging
      console.error('MCP Action Error:', error);
    },
    onSuccess: () => {
      // Invalida le query correlate per forzare il refresh dei dati
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    }
  });
};

export const useValidateAction = () => {
  return useMutation({
    mutationFn: async (action: { action: string; parameters: Record<string, any> }) => {
      // Estrai gli ID dall'azione
      const orderIds = [];
      const machineIds = [];
      
      if (action.parameters.order_id) {
        orderIds.push(action.parameters.order_id);
      }
      if (action.parameters.machine_id) {
        machineIds.push(action.parameters.machine_id);
      }
      
      // Chiama l'endpoint di validazione
      const response = await fetch(`${process.env.REACT_APP_MCP_API}/tools/validate_ids`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          order_ids: orderIds,
          machine_ids: machineIds
        })
      });
      
      if (!response.ok) {
        throw new Error('Validation failed');
      }
      
      const result = await response.json();
      
      if (!result.all_valid) {
        const invalidItems = Object.entries(result.validation_results)
          .filter(([_, valid]) => !valid)
          .map(([key, _]) => key);
        
        throw new Error(
          `Invalid IDs found: ${invalidItems.join(', ')}. ` +
          'Please refresh the analysis to get current data.'
        );
      }
      
      return result;
    }
  });
};