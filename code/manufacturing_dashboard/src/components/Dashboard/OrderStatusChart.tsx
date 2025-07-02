import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Package, Clock, CheckCircle, AlertCircle, XCircle, Truck } from 'lucide-react';

interface OrderStatus {
  status: string;
  count: number;
  percentage: number;
  icon?: React.ReactNode;
}

interface OrderStatusChartProps {
  data?: OrderStatus[];
  showLegend?: boolean;
  height?: number;
}

// Definisci i colori come array per un facile accesso tramite indice
const CHART_COLORS = [
  '#10b981', // green - completed
  '#3b82f6', // blue - in progress
  '#f59e0b', // yellow - pending
  '#ef4444', // red - cancelled
  '#6b7280', // gray - on hold
  '#8b5cf6'  // purple - shipping
];

const defaultData: OrderStatus[] = [
  { status: 'Completed', count: 145, percentage: 35, icon: <CheckCircle className="h-4 w-4" /> },
  { status: 'In Progress', count: 89, percentage: 22, icon: <Clock className="h-4 w-4" /> },
  { status: 'Pending', count: 67, percentage: 16, icon: <Package className="h-4 w-4" /> },
  { status: 'On Hold', count: 45, percentage: 11, icon: <AlertCircle className="h-4 w-4" /> },
  { status: 'Shipping', count: 38, percentage: 9, icon: <Truck className="h-4 w-4" /> },
  { status: 'Cancelled', count: 28, percentage: 7, icon: <XCircle className="h-4 w-4" /> }
];

export const OrderStatusChart: React.FC<OrderStatusChartProps> = ({ 
  data = defaultData,
  showLegend = true,
  height = 300
}) => {
  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      case 'in progress':
        return <Clock className="h-4 w-4" />;
      case 'pending':
        return <Package className="h-4 w-4" />;
      case 'on hold':
        return <AlertCircle className="h-4 w-4" />;
      case 'shipping':
        return <Truck className="h-4 w-4" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4" />;
      default:
        return <Package className="h-4 w-4" />;
    }
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="bg-white p-3 shadow-lg rounded-lg border border-gray-200">
          <div className="flex items-center gap-2 mb-1">
            {getStatusIcon(data.name)}
            <p className="font-semibold text-gray-900">{data.name}</p>
          </div>
          <p className="text-sm text-gray-600">Count: {data.value}</p>
          <p className="text-sm text-gray-600">Percentage: {data.payload.percentage}%</p>
        </div>
      );
    }
    return null;
  };

  const CustomLegend = (props: any) => {
    const { payload } = props;
    return (
      <ul className="flex flex-wrap gap-3 justify-center mt-4">
        {payload.map((entry: any, index: number) => (
          <li key={`item-${index}`} className="flex items-center gap-2">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-sm text-gray-600">{entry.value}</span>
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ percentage }) => `${percentage}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="count"
            nameKey="status"
          >
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={CHART_COLORS[index % CHART_COLORS.length]} 
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          {showLegend && <Legend content={<CustomLegend />} />}
        </PieChart>
      </ResponsiveContainer>
      
      {/* Status Summary */}
      <div className="mt-6 grid grid-cols-2 sm:grid-cols-3 gap-3">
        {data.map((status, index) => (
          <div
            key={status.status}
            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }}
              />
              <span className="text-sm font-medium text-gray-700">{status.status}</span>
            </div>
            <span className="text-sm font-bold text-gray-900">{status.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
};