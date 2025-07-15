// File: /code/manufacturing_dashboard/src/hooks/useAnalytics.ts
// Versione corretta con import di detectAnomalies e sintassi mutation fix

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { analyticsService, llmService, detectAnomalies } from '../services/api'; // Aggiungi detectAnomalies
import { 
  AnalyticsSummary, 
  Anomaly, 
  Recommendation
} from '../types';
import { OperatorPerformance } from '../types';  // Solo questo

// Analytics Summary Hook
export const useAnalyticsSummary = () => {
  return useQuery({
    queryKey: ['analytics-summary'],
    queryFn: analyticsService.getSummary,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 60 * 1000, // Refetch every minute
  });
};

// Latest Analytics Data Hook
export const useLatestAnalytics = () => {
  return useQuery({
    queryKey: ['latest-analytics'],
    queryFn: analyticsService.getAllData,
    staleTime: 5 * 60 * 1000,
    refetchInterval: 60 * 1000,
  });
};

// Anomalies Hook
export const useAnomalies = () => {
  return useQuery({
    queryKey: ['anomalies'],
    queryFn: async () => {
      try {
        const analyticsData = await analyticsService.getAllData();
        return detectAnomalies(analyticsData); // Usa detectAnomalies importata
      } catch (error) {
        console.error('Failed to detect anomalies:', error);
        return [];
      }
    },
    staleTime: 5 * 60 * 1000,
  });
};

// Latest Recommendation Hook
export const useLatestRecommendation = () => {
  return useQuery({
    queryKey: ['latest-recommendation'],
    queryFn: llmService.getLatestRecommendation,
    staleTime: 5 * 60 * 1000,
  });
};

// Recommendation History Hook
export const useRecommendationHistory = (days: number = 7) => {
  return useQuery({
    queryKey: ['recommendation-history', days],
    queryFn: () => llmService.getRecommendationHistory(days),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Analytics Status Hook
export const useAnalyticsStatus = () => {
  return useQuery({
    queryKey: ['analytics-status'],
    queryFn: analyticsService.getStatus,
    refetchInterval: 30 * 1000, // Every 30 seconds
  });
};

// Generate Analytics Mutation
export const useGenerateAnalytics = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (force: boolean = false) => analyticsService.runAnalytics(force),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['analytics-summary'] });
      queryClient.invalidateQueries({ queryKey: ['latest-analytics'] });
      queryClient.invalidateQueries({ queryKey: ['analytics-status'] });
      queryClient.invalidateQueries({ queryKey: ['anomalies'] });
    },
  });
};

// Generate Recommendation Mutation
export const useGenerateRecommendation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (customPrompt?: string) => {
      return await llmService.generateRecommendation(customPrompt);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['latest-recommendation'] });
      queryClient.invalidateQueries({ queryKey: ['recommendation-history'] });
      queryClient.setQueryData(['latest-recommendation'], data);
    },
    onError: (error) => {
      console.error('Failed to generate recommendation:', error);
    }
  });
};

// Execute MCP Action Mutation
export const useExecuteMcpAction = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (params: { action: string; parameters: Record<string, any> }) => 
      llmService.executeMcpAction(params.action, params.parameters),
    onSuccess: () => {
      // Refresh data after MCP action
      queryClient.invalidateQueries({ queryKey: ['analytics-summary'] });
      queryClient.invalidateQueries({ queryKey: ['latest-analytics'] });
    },
  });
};

// Dashboard Data Hook
export const useDashboardData = () => {
  const summaryQuery = useAnalyticsSummary();
  const analyticsQuery = useLatestAnalytics();
  const anomaliesQuery = useAnomalies();

  return {
    summary: summaryQuery.data,
    analyticsData: analyticsQuery.data,
    anomalies: anomaliesQuery.data || [],
    isLoading: summaryQuery.isLoading || analyticsQuery.isLoading || anomaliesQuery.isLoading,
    isError: summaryQuery.isError || analyticsQuery.isError || anomaliesQuery.isError,
    error: summaryQuery.error || analyticsQuery.error || anomaliesQuery.error,
    refetch: () => {
      summaryQuery.refetch();
      analyticsQuery.refetch();
      anomaliesQuery.refetch();
    }
  };
};

// Operator Performance Hook
export const useOperatorPerformance = () => {
  return useQuery({
    queryKey: ['operator-performance'],
    queryFn: async () => {
      try {
        const allData = await analyticsService.getAllData();
        const operatorData = allData?.operator_performance?.data || [];
        
        return operatorData.sort((a: OperatorPerformance, b: OperatorPerformance) => 
          (b.efficiency || 0) - (a.efficiency || 0)
        );
      } catch (error) {
        console.error('Failed to fetch operator performance:', error);
        return [];
      }
    },
    staleTime: 5 * 60 * 1000,
    refetchInterval: 60 * 1000,
  });
};

// Recommendations with Operators Hook
export const useRecommendationsWithOperators = () => {
  const recommendationQuery = useLatestRecommendation();
  const operatorQuery = useOperatorPerformance();
  
  return {
    recommendation: recommendationQuery.data,
    operators: operatorQuery.data || [],
    isLoading: recommendationQuery.isLoading || operatorQuery.isLoading,
    isError: recommendationQuery.isError || operatorQuery.isError,
    error: recommendationQuery.error || operatorQuery.error,
    refetch: () => {
      recommendationQuery.refetch();
      operatorQuery.refetch();
    }
  };
};

// Operator Performance by Shift Hook
export const useOperatorPerformanceByShift = (shift?: string) => {
  return useQuery({
    queryKey: ['operator-performance-shift', shift],
    queryFn: async () => {
      const allData = await analyticsService.getAllData();
      const allOperators = allData?.operator_performance?.data || [];
      
      if (!shift) return allOperators;
      
      return allOperators.filter((op: OperatorPerformance) => 
        true // Replace with actual shift filtering logic when available
      );
    },
    enabled: true,
    staleTime: 5 * 60 * 1000,
  });
};

// Top Performers Hook
export const useTopPerformers = (limit: number = 5) => {
  return useQuery({
    queryKey: ['top-performers', limit],
    queryFn: async () => {
      const allData = await analyticsService.getAllData();
      const operators = allData?.operator_performance?.data || [];
      
      return operators
        .sort((a: OperatorPerformance, b: OperatorPerformance) => 
          (b.efficiency || 0) - (a.efficiency || 0)
        )
        .slice(0, limit);
    },
    staleTime: 5 * 60 * 1000,
  });
};

// Operator Metrics Summary Hook
export const useOperatorMetricsSummary = () => {
  return useQuery({
    queryKey: ['operator-metrics-summary'],
    queryFn: async () => {
      const allData = await analyticsService.getAllData();
      const operators = allData?.operator_performance?.data || [];
      
      if (operators.length === 0) {
        return {
          totalOperators: 0,
          avgEfficiency: 0,
          avgCycleTime: 0,
          totalQuantityProduced: 0,
          topPerformer: null,
          bottomPerformer: null
        };
      }
      
      const efficiencies = operators.map((op: OperatorPerformance) => op.efficiency || 0);
      const cycleTimes = operators.map((op: OperatorPerformance) => op.avg_cycle_time || 0);
      const totalQuantity = operators.reduce((sum: number, op: OperatorPerformance) => 
        sum + (op.total_quantity || 0), 0
      );
      
      const sortedByEfficiency = [...operators].sort((a: OperatorPerformance, b: OperatorPerformance) => 
        (b.efficiency || 0) - (a.efficiency || 0)
      );
      
      return {
        totalOperators: operators.length,
        avgEfficiency: efficiencies.length > 0 
          ? efficiencies.reduce((a, b) => a + b, 0) / efficiencies.length 
          : 0,
        avgCycleTime: cycleTimes.length > 0 
          ? cycleTimes.reduce((a, b) => a + b, 0) / cycleTimes.length 
          : 0,
        totalQuantityProduced: totalQuantity,
        topPerformer: sortedByEfficiency[0] || null,
        bottomPerformer: sortedByEfficiency[sortedByEfficiency.length - 1] || null
      };
    },
    staleTime: 5 * 60 * 1000,
  });
};