import React from 'react';
import { 
  Package, 
  Cpu, 
  TrendingUp, 
  Clock,
  AlertTriangle,
  Users
} from 'lucide-react';
import { Card } from '../common/Card';
import { MetricCard } from './MetricCard';
import { MachineUtilizationChart } from './MachineUtilizationChart';
import { OrderStatusChart } from './OrderStatusChart';
import { BottlenecksList } from './BottlenecksList';
import { useDashboardData } from '../../hooks/useAnalytics';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ErrorMessage } from '../common/ErrorMessage';
import { formatNumber, formatPercentage } from '../../utils';


export const OverviewDashboard: React.FC = () => {
  const { summary, analyticsData, anomalies, isLoading, isError, error, refetch } = useDashboardData();

  if (isLoading) {
    return <LoadingSpinner text="Loading dashboard data..." />;
  }

  if (isError) {
    return (
      <ErrorMessage 
        title="Failed to load dashboard"
        message={error?.message || 'An error occurred while loading the dashboard data.'}
        onRetry={refetch}
      />
    );
  }

  const metrics = [
    {
      title: 'Total Orders',
      value: formatNumber(summary?.total_orders || 0),
      change: '+12%',
      trend: 'up' as const,
      icon: Package,
      color: 'primary' as const,
    },
    {
      title: 'Active Machines',
      value: `${summary?.active_machines || 0}/${summary?.total_machines || 0}`,
      change: formatPercentage((summary?.active_machines || 0) / (summary?.total_machines || 1) * 100),
      trend: 'up' as const,
      icon: Cpu,
      color: 'success' as const,
    },
    {
      title: 'Avg. Efficiency',
      value: formatPercentage(summary?.avg_efficiency || 0),
      change: '+5%',
      trend: 'up' as const,
      icon: TrendingUp,
      color: 'info' as const,
    },
    {
      title: 'On-Time Delivery',
      value: formatPercentage(summary?.on_time_rate || 0),
      change: '-3%',
      trend: 'down' as const,
      icon: Clock,
      color: 'warning' as const,
    },
    {
      title: 'Active Anomalies',
      value: formatNumber(anomalies.length),
      change: anomalies.length > 0 ? 'Active' : 'None',
      trend: anomalies.length > 0 ? 'down' : 'neutral' as const,
      icon: AlertTriangle,
      color: anomalies.length > 0 ? 'danger' : 'success' as const,
    },
    {
      title: 'Total Operators',
      value: formatNumber(summary?.total_operators || 0),
      change: 'Active',
      trend: 'neutral' as const,
      icon: Users,
      color: 'secondary' as const,
    },
  ] as const;

  return (
    <div className="space-y-6">
      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {metrics.map((metric, index) => (
          <MetricCard key={index} {...metric} />
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Machine Utilization" subtitle="Current utilization vs target">
          <MachineUtilizationChart data={analyticsData?.machine_metrics?.data || []} />
        </Card>

        <Card title="Order Status Distribution" subtitle="Orders by current status">
          <OrderStatusChart data={analyticsData?.order_timeline?.data || []} />
        </Card>
      </div>

      {/* Bottlenecks Section */}
      <Card 
        title="Production Bottlenecks" 
        subtitle="Phases with highest queue delays"
        className="col-span-full"
      >
        <BottlenecksList data={analyticsData?.queue_analysis?.data || []} />
      </Card>
    </div>
  );
};