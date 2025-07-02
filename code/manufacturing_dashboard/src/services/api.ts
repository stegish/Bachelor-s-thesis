import axios, { AxiosInstance } from 'axios';
import {
  AnalyticsSummary,
  MachineMetrics,
  OrderTimeline,
  PhaseMetrics,
  QueueAnalysis,
  OperatorPerformance,
  Recommendation,
  Anomaly,
  ApiResponse
} from '../types';

// API URLs from environment variables
const ANALYTICS_API_URL = process.env.REACT_APP_ANALYTICS_API || 'http://localhost:5000';
const LLM_API_URL = process.env.REACT_APP_LLM_API || 'http://localhost:5001';

// Create axios instances
const analyticsApi: AxiosInstance = axios.create({
  baseURL: ANALYTICS_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const llmApi: AxiosInstance = axios.create({
  baseURL: LLM_API_URL,
  timeout: 60000, // Longer timeout for LLM operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request/response interceptors for error handling
[analyticsApi, llmApi].forEach(api => {
  api.interceptors.response.use(
    response => response,
    error => {
      console.error('API Error:', error);
      if (error.response?.status === 401) {
        // Handle unauthorized - redirect to login if needed
      }
      return Promise.reject(error);
    }
  );
});

// Analytics API Services
export const analyticsService = {
  // Get analytics summary
  getSummary: async (): Promise<AnalyticsSummary> => {
    const response = await analyticsApi.get('/api/v1/analytics/summary');
    return response.data;
  },

  // Get all CSV data as JSON
  getAllData: async () => {
    const response = await analyticsApi.get('/api/v1/csv/download-all-json');
    return response.data;
  },

  // Run analytics generation
  runAnalytics: async (force: boolean = false): Promise<any> => {
    const response = await analyticsApi.post('/api/v1/analytics/run', null, {
      params: { force }
    });
    return response.data;
  },

  // Get analytics status
  getStatus: async (): Promise<any> => {
    const response = await analyticsApi.get('/api/v1/analytics/status');
    return response.data;
  },

  // List available CSV files
  listFiles: async (): Promise<any> => {
    const response = await analyticsApi.get('/api/v1/csv/list');
    return response.data;
  },

  // Download specific CSV file
  downloadFile: async (filename: string): Promise<Blob> => {
    const response = await analyticsApi.get(`/api/v1/csv/download/${filename}`, {
      responseType: 'blob'
    });
    return response.data;
  }
};

// LLM API Services
export const llmService = {
  // Generate new recommendation
  generateRecommendation: async (customPrompt?: string): Promise<Recommendation> => {
    const response = await llmApi.post('/api/v1/recommendations/generate', {
      custom_prompt: customPrompt
    });
    return response.data;
  },

  // Get latest recommendation
  getLatestRecommendation: async (): Promise<Recommendation> => {
    const response = await llmApi.get('/api/v1/recommendations/latest');
    return response.data;
  },

  // Get recommendation history
  getRecommendationHistory: async (days: number = 7): Promise<any> => {
    const response = await llmApi.get('/api/v1/recommendations/history', {
      params: { days }
    });
    return response.data;
  },

  // Get specific recommendation by ID
  getRecommendationById: async (id: string): Promise<Recommendation> => {
    const response = await llmApi.get(`/api/v1/recommendations/${id}`);
    return response.data;
  },

  // Analyze with custom question
  analyze: async (question: string, includeContext: boolean = true): Promise<any> => {
    const response = await llmApi.post('/api/v1/analysis', {
      question,
      include_db_context: includeContext
    });
    return response.data;
  },

  // Chat with context
  chat: async (message: string, sessionId: string): Promise<any> => {
    const response = await llmApi.post('/api/v1/chat', {
      message,
      session_id: sessionId
    });
    return response.data;
  },

  // Get suggestions based on metrics
  getSuggestions: async (metrics: any): Promise<any> => {
    const response = await llmApi.post('/api/v1/suggestions', {
      metrics
    });
    return response.data;
  }
};

// Utility function to detect anomalies from data
export const detectAnomalies = (data: any): Anomaly[] => {
  const anomalies: Anomaly[] = [];
  
  // Check machine efficiency
  if (data.machine_metrics?.data) {
    data.machine_metrics.data.forEach((machine: MachineMetrics) => {
      if (machine.efficiency_percentage !== null && machine.efficiency_percentage < 70) {
        anomalies.push({
          id: `anomaly-${machine.machine_name}-efficiency`,
          type: 'efficiency',
          severity: machine.efficiency_percentage < 50 ? 'high' : 'medium',
          machine: machine.machine_name,
          description: `Machine ${machine.machine_name} efficiency is ${machine.efficiency_percentage.toFixed(1)}%`,
          detected_at: new Date().toISOString(),
          metrics: {
            current_value: machine.efficiency_percentage,
            expected_value: 85,
            deviation_percentage: ((85 - machine.efficiency_percentage) / 85) * 100
          }
        });
      }
    });
  }
  
  // Check queue delays
  if (data.queue_analysis?.data) {
    data.queue_analysis.data.forEach((queue: QueueAnalysis) => {
      if (queue.is_bottleneck) {
        anomalies.push({
          id: `anomaly-${queue.phase_name}-bottleneck`,
          type: 'bottleneck',
          severity: queue.avg_queue_delay > 10 ? 'critical' : 'high',
          phase: queue.phase_name,
          description: `${queue.phase_name} is a bottleneck with ${queue.avg_queue_delay.toFixed(1)} hours average queue delay`,
          detected_at: new Date().toISOString(),
          metrics: {
            current_value: queue.avg_queue_delay,
            expected_value: 2,
            deviation_percentage: ((queue.avg_queue_delay - 2) / 2) * 100
          }
        });
      }
    });
  }
  
  return anomalies;
};