import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { OrderStatus } from '../../types';
import { CHART_COLORS } from '../../utils';

interface OrderStatusChartProps {
  data: Array<{
    order_status: number;
    [key: string]: any;
  }>;
}

const STATUS_LABELS: Record<number, string> = {
  [OrderStatus.PENDING]: 'Pending',
  [OrderStatus.IN_PROGRESS]: 'In Progress',
  [OrderStatus.ON_HOLD]: 'On Hold',
  [OrderStatus.QUALITY_CHECK]: 'Quality Check',
  [OrderStatus.COMPLETED]: 'Completed',
  [OrderStatus.CANCELLED]: 'Cancelled',
};

export const OrderStatusChart: React.FC<OrderStatusChartProps> = ({ data }) => {
  // Group orders by status
  const statusCounts = data.reduce((acc, order) => {
    const status = order.order_status;
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, {} as Record<number, number>);

  const chartData = Object.entries(statusCounts).map(([status, count]) => ({
    name: STATUS_LABELS[parseInt(status)] || `Status ${status}`,
    value: count,
    status: parseInt(status),
  }));

  const renderCustomizedLabel = ({
    cx, cy, midAngle, innerRadius, outerRadius, percent
  }: any) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * Math.PI / 180);
    const y = cy + radius * Math.sin(-midAngle * Math.PI / 180);

    if (percent < 0.05) return null; // Don't show label for small slices

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        className="font-medium"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={renderCustomizedLabel}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {chartData.map((entry, index) => (
            <Cell 
              key={`cell-${entry.status}-${index}`} // FIX: Aggiungi key unica
              fill={CHART_COLORS.palette[index % CHART_COLORS.palette.length]} 
            />
          ))}
        </Pie>
        <Tooltip />
        <Legend 
          formatter={(value) => <span className="text-sm">{value}</span>}
          iconType="circle"
        />
      </PieChart>
    </ResponsiveContainer>
  );
};