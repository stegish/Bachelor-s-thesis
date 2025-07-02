import axios, { AxiosInstance } from 'axios';
import {
  AnalyticsSummary,
  MachineMetrics,
  OrderTimeline,
  PhaseMetrics,
  QueueAnalysis,
  OperatorPerformance,
  Recommendation,
  Anomaly
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
  },

  // Download all CSV files as ZIP
  downloadAllFiles: async (): Promise<Blob> => {
    const response = await analyticsApi.get('/api/v1/csv/download-all', {
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
  getRecommendationById: async (analysisId: string): Promise<Recommendation> => {
    const response = await llmApi.get(`/api/v1/recommendations/${analysisId}`);
    return response.data;
  },

  // Generate and notify
  generateAndNotify: async (customPrompt?: string): Promise<any> => {
    const response = await llmApi.post('/api/v1/recommendations/generate-and-notify', {
      custom_prompt: customPrompt
    });
    return response.data;
  },

  // Chat with LLM
  chat: async (message: string, sessionId?: string): Promise<any> => {
    const response = await llmApi.post('/api/v1/chat', {
      message,
      session_id: sessionId
    });
    return response.data;
  },

  // Analyze custom question
  analyze: async (question: string, includeContext: boolean = true): Promise<any> => {
    const response = await llmApi.post('/api/v1/analyze', {
      question,
      include_db_context: includeContext
    });
    return response.data;
  }
};

// Anomaly detection function
export const detectAnomalies = (analyticsData: any): Anomaly[] => {
  const anomalies: Anomaly[] = [];
  
  // Check machine metrics for anomalies
  if (analyticsData.machine_metrics) {
    analyticsData.machine_metrics.forEach((machine: MachineMetrics) => {
      // Low efficiency anomaly
      if (machine.efficiency_percentage && machine.efficiency_percentage < 70) {
        anomalies.push({
          id: `anomaly-eff-${machine.machine_name}`,
          type: 'efficiency',
          severity: machine.efficiency_percentage < 50 ? 'critical' : 'high',
          machine: machine.machine_name,
          description: `Low efficiency: ${machine.efficiency_percentage.toFixed(1)}%`,
          detected_at: new Date().toISOString(),
          metrics: {
            current_value: machine.efficiency_percentage,
            expected_value: 85,
            deviation_percentage: ((85 - machine.efficiency_percentage) / 85) * 100
          }
        });
      }
      
      // High queue delay anomaly
      if (machine.avg_queue_delay > 4) {
        anomalies.push({
          id: `anomaly-queue-${machine.machine_name}`,
          type: 'delay',
          severity: machine.avg_queue_delay > 8 ? 'critical' : 'medium',
          machine: machine.machine_name,
          description: `High queue delay: ${machine.avg_queue_delay.toFixed(1)} hours`,
          detected_at: new Date().toISOString(),
          metrics: {
            current_value: machine.avg_queue_delay,
            expected_value: 2,
            deviation_percentage: ((machine.avg_queue_delay - 2) / 2) * 100
          }
        });
      }
    });
  }
  
  // Check order timeline for delays
  if (analyticsData.order_timeline) {
    const delayedOrders = analyticsData.order_timeline.filter(
      (order: OrderTimeline) => order.delay_days && order.delay_days > 2
    );
    
    if (delayedOrders.length > 0) {
      const avgDelay = delayedOrders.reduce((sum: number, order: OrderTimeline) => 
        sum + (order.delay_days || 0), 0) / delayedOrders.length;
      
      anomalies.push({
        id: 'anomaly-delivery-delays',
        type: 'delay',
        severity: avgDelay > 5 ? 'high' : 'medium',
        description: `${delayedOrders.length} orders with delivery delays (avg: ${avgDelay.toFixed(1)} days)`,
        detected_at: new Date().toISOString(),
        metrics: {
          current_value: avgDelay,
          expected_value: 0,
          deviation_percentage: 100
        }
      });
    }
  }
  
  // Check for bottlenecks
  if (analyticsData.queue_analysis) {
    analyticsData.queue_analysis.forEach((queue: QueueAnalysis) => {
      if (queue.is_bottleneck) {
        anomalies.push({
          id: `anomaly-bottleneck-${queue.phase_name}`,
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

// Export all services
export default {
  analytics: analyticsService,
  llm: llmService,
  detectAnomalies
};