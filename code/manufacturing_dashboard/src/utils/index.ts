import { format, formatDistance, parseISO } from 'date-fns';
import { OrderStatus, PhaseStatus } from '../types';

// Date formatting utilities
export const formatDate = (date: string | Date | null): string => {
  if (!date) return 'N/A';
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'MMM dd, yyyy');
  } catch {
    return 'Invalid date';
  }
};

export const formatDateTime = (date: string | Date | null): string => {
  if (!date) return 'N/A';
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'MMM dd, yyyy HH:mm');
  } catch {
    return 'Invalid date';
  }
};

export const formatRelativeTime = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatDistance(dateObj, new Date(), { addSuffix: true });
  } catch {
    return 'Unknown';
  }
};

// Number formatting utilities
export const formatNumber = (num: number | null | undefined, decimals: number = 0): string => {
  if (num === null || num === undefined) return 'N/A';
  return num.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

export const formatPercentage = (num: number | null | undefined): string => {
  if (num === null || num === undefined) return 'N/A';
  return `${num.toFixed(1)}%`;
};

export const formatDuration = (hours: number | null | undefined): string => {
  if (hours === null || hours === undefined) return 'N/A';
  if (hours < 1) return `${Math.round(hours * 60)}m`;
  if (hours < 24) return `${hours.toFixed(1)}h`;
  return `${(hours / 24).toFixed(1)}d`;
};

// Status utilities
export const getOrderStatusLabel = (status: number): string => {
  const labels: Record<OrderStatus, string> = {
    [OrderStatus.PENDING]: 'Pending',
    [OrderStatus.IN_PROGRESS]: 'In Progress',
    [OrderStatus.ON_HOLD]: 'On Hold',
    [OrderStatus.QUALITY_CHECK]: 'Quality Check',
    [OrderStatus.COMPLETED]: 'Completed',
    [OrderStatus.CANCELLED]: 'Cancelled',
  };
  return labels[status as OrderStatus] || 'Unknown';
};

export const getOrderStatusColor = (status: number): string => {
  const colors: Record<OrderStatus, string> = {
    [OrderStatus.PENDING]: 'text-gray-600 bg-gray-100',
    [OrderStatus.IN_PROGRESS]: 'text-blue-600 bg-blue-100',
    [OrderStatus.ON_HOLD]: 'text-yellow-600 bg-yellow-100',
    [OrderStatus.QUALITY_CHECK]: 'text-purple-600 bg-purple-100',
    [OrderStatus.COMPLETED]: 'text-green-600 bg-green-100',
    [OrderStatus.CANCELLED]: 'text-red-600 bg-red-100',
  };
  return colors[status as OrderStatus] || 'text-gray-600 bg-gray-100';
};

export const getPhaseStatusLabel = (status: number): string => {
  const labels: Record<PhaseStatus, string> = {
    [PhaseStatus.QUEUED]: 'Queued',
    [PhaseStatus.IN_PROGRESS]: 'In Progress',
    [PhaseStatus.PAUSED]: 'Paused',
    [PhaseStatus.QUALITY_CHECK]: 'Quality Check',
    [PhaseStatus.COMPLETED]: 'Completed',
    [PhaseStatus.FAILED]: 'Failed',
  };
  return labels[status as PhaseStatus] || 'Unknown';
};

// Chart utilities
export const CHART_COLORS = {
  primary: '#3b82f6',
  secondary: '#8b5cf6',
  success: '#22c55e',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#06b6d4',
  gray: '#6b7280',
  
  // Extended palette for multiple series
  palette: [
    '#3b82f6', // blue
    '#22c55e', // green
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // violet
    '#06b6d4', // cyan
    '#ec4899', // pink
    '#10b981', // emerald
    '#f97316', // orange
    '#6366f1', // indigo
  ],
};

// Severity utilities
export const getSeverityColor = (severity: 'low' | 'medium' | 'high' | 'critical'): string => {
  const colors = {
    low: 'bg-blue-100 text-blue-800 border-blue-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    critical: 'bg-red-100 text-red-800 border-red-200',
  };
  return colors[severity] || colors.medium;
};

export const getSeverityIcon = (severity: 'low' | 'medium' | 'high' | 'critical'): string => {
  const icons = {
    low: 'Info',
    medium: 'AlertTriangle',
    high: 'AlertCircle',
    critical: 'XCircle',
  };
  return icons[severity] || 'AlertTriangle';
};

// Data transformation utilities
export const groupBy = <T>(array: T[], key: keyof T): Record<string, T[]> => {
  return array.reduce((result, item) => {
    const group = String(item[key]);
    if (!result[group]) result[group] = [];
    result[group].push(item);
    return result;
  }, {} as Record<string, T[]>);
};

export const sortByDate = <T extends { [key: string]: any }>(
  array: T[],
  dateKey: keyof T,
  ascending: boolean = true
): T[] => {
  return [...array].sort((a, b) => {
    const dateA = new Date(a[dateKey]).getTime();
    const dateB = new Date(b[dateKey]).getTime();
    return ascending ? dateA - dateB : dateB - dateA;
  });
};

// Validation utilities
export const isValidDate = (date: any): boolean => {
  if (!date) return false;
  const parsed = typeof date === 'string' ? parseISO(date) : date;
  return parsed instanceof Date && !isNaN(parsed.getTime());
};

// Export utilities
export const downloadCSV = (data: any[], filename: string) => {
  // Convert data to CSV format
  const headers = Object.keys(data[0] || {}).join(',');
  const rows = data.map(row => 
    Object.values(row).map(val => 
      typeof val === 'string' && val.includes(',') ? `"${val}"` : val
    ).join(',')
  );
  const csv = [headers, ...rows].join('\n');
  
  // Create and trigger download
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};