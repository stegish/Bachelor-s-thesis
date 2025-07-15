// Analytics Types
export interface MachineMetrics {
  machine_name: string;
  is_active: boolean;
  queue_target_time: number;
  current_queue_length: number;
  total_phases_processed: number;
  completed_phases: number;
  in_progress_phases: number;
  avg_cycle_time: number;
  avg_actual_duration: number;
  avg_queue_delay: number;
  avg_finish_delay: number;
  total_quantity_processed: number;
  unique_operators: number;
  efficiency_percentage: number | null;
  utilization_percentage: number | null;
}

export interface OrderTimeline {
  order_id: string;
  article_code: string;
  product_family: string;
  quantity: number;
  priority: number;
  order_status: number;
  insert_date: string;
  start_date: string | null;
  deadline: string | null;
  real_finish_date: string | null;
  lead_time_days: number | null;
  delay_days: number | null;
  on_time: boolean | null;
  progress_percentage: number;
  total_phases: number;
  completed_phases: number;
}

export interface PhaseMetrics {
  order_id: string;
  order_status: number;
  phase_id: string;
  phase_name: string;
  phase_status: number;
  cycle_time: number;
  actual_duration: number | null;
  efficiency: number | null;
  queue_delay_hours: number | null;
  declared_quantity: number;
  operators: string;
  operator_count: number;
}

export interface QueueAnalysis {
  phase_name: string;
  avg_queue_delay: number;
  queue_delay_std: number;
  max_queue_delay: number;
  total_jobs: number;
  total_quantity: number;
  is_bottleneck: boolean;
}

export interface OperatorPerformance {
  operator: string;
  total_phases: number;
  avg_cycle_time: number;
  avg_actual_duration: number;
  total_quantity: number;
  efficiency: number | null;
}

export interface AnalyticsSummary {
  total_orders: number;
  completed_orders: number;
  active_machines: number;
  total_machines: number;
  avg_lead_time: number;
  on_time_rate: number;
  avg_utilization: number;
  avg_efficiency: number;
  bottleneck_machines: string[];
  total_operators: number;
}

// LLM Types
export interface Anomaly {
  id: string;
  type: 'bottleneck' | 'delay' | 'efficiency' | 'quality' | 'other';
  severity: 'low' | 'medium' | 'high' | 'critical';
  machine?: string;
  phase?: string;
  description: string;
  detected_at: string;
  metrics: {
    current_value: number;
    expected_value: number;
    deviation_percentage: number;
  };
}

export interface Recommendation {
  analysis_id: string;
  timestamp: string;
  analysis: string;
  recommendations: Array<{
    id: string;
    description: string;
    priority: 'low' | 'medium' | 'high';
    type: 'maintenance' | 'optimization' | 'alert' | 'improvement';
  }>;
  anomalies_detected: string[];
  priority_actions: Array<{
    id: string;
    description: string;
    urgency: 'high' | 'critical';
    estimated_impact: string;
    action?: string;
    parameters?: Record<string, any>;
  }>;
  metrics_analyzed: {
    avg_machine_utilization?: number;
    avg_machine_efficiency?: number;
    order_completion_rate?: number;
    on_time_delivery_rate?: number;
    avg_queue_delay_hours?: number;
    total_operators_active?: number;
    bottleneck_count?: number;  
  };
  processing_time: number;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  status: 'success' | 'error';
  message?: string;
  timestamp?: string;
}

// Status Types
export enum OrderStatus {
  PENDING = 0,
  IN_PROGRESS = 1,
  ON_HOLD = 2,
  QUALITY_CHECK = 3,
  COMPLETED = 4,
  CANCELLED = 5
}

export enum PhaseStatus {
  QUEUED = 0,
  IN_PROGRESS = 1,
  PAUSED = 2,
  QUALITY_CHECK = 3,
  COMPLETED = 4,
  FAILED = 5
}

// Se non hai già definito l'interfaccia OperatorPerformance, aggiungila:
export interface OperatorPerformance {
  operator: string;
  total_phases: number;
  avg_cycle_time: number;
  avg_actual_duration: number;
  total_quantity: number;
  efficiency: number | null;
}