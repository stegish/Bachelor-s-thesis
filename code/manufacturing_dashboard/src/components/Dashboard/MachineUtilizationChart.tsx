// File: /code/manufacturing_dashboard/src/components/Dashboard/MachineUtilizationChart.tsx
// Versione corretta che gestisce il formato dati reale

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { MachineMetrics } from '../../types';

interface MachineUtilizationChartProps {
  data?: MachineMetrics[];
  height?: number;
}

const TARGET_UTILIZATION = 85; // Target standard

export const MachineUtilizationChart: React.FC<MachineUtilizationChartProps> = ({
  data = [],
  height = 300
}) => {
  // Transform data to the format expected by the chart
  const chartData = React.useMemo(() => {
    if (!data || data.length === 0) {
      // Return default data if no data is provided
      return [
        { machine: 'CNC-01', utilization: 85, target: TARGET_UTILIZATION },
        { machine: 'CNC-02', utilization: 78, target: TARGET_UTILIZATION },
        { machine: 'LATHE-01', utilization: 92, target: TARGET_UTILIZATION },
        { machine: 'MILL-01', utilization: 67, target: TARGET_UTILIZATION },
        { machine: 'MILL-02', utilization: 89, target: TARGET_UTILIZATION },
      ];
    }

    // Transform actual data from API
    return data
      .filter(machine => machine.utilization_percentage !== null && machine.utilization_percentage !== undefined)
      .map(machine => ({
        machine: machine.machine_name,
        utilization: Math.round(machine.utilization_percentage || 0),
        target: TARGET_UTILIZATION
      }))
      .slice(0, 10); // Limit to 10 machines for readability
  }, [data]);

  // Calculate summary statistics
  const stats = React.useMemo(() => {
    if (chartData.length === 0) {
      return { average: 0, meetingTarget: 0, belowTarget: 0 };
    }

    const total = chartData.reduce((sum, item) => sum + item.utilization, 0);
    const average = total / chartData.length;
    const meetingTarget = chartData.filter(item => item.utilization >= TARGET_UTILIZATION).length;
    const belowTarget = chartData.length - meetingTarget;

    return { average, meetingTarget, belowTarget };
  }, [chartData]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const utilization = payload[0].value;
      const isOnTarget = utilization >= TARGET_UTILIZATION;
      
      return (
        <div className="bg-white p-3 shadow-lg rounded-lg border border-gray-200">
          <p className="font-semibold text-gray-900">{label}</p>
          <p className="text-sm text-gray-600 mt-1">
            Utilization: <span className="font-medium">{utilization}%</span>
          </p>
          <p className="text-sm text-gray-600">
            Target: <span className="font-medium">{TARGET_UTILIZATION}%</span>
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {isOnTarget ? '✅ Meeting target' : '⚠️ Below target'}
          </p>
          {!isOnTarget && (
            <p className="text-xs text-red-600">
              Gap: {TARGET_UTILIZATION - utilization}%
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  const CustomLegend = () => {
    return (
      <div className="flex justify-center gap-4 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded"></div>
          <span className="text-sm text-gray-600">Actual Utilization</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-gray-300 rounded"></div>
          <span className="text-sm text-gray-600">Target ({TARGET_UTILIZATION}%)</span>
        </div>
      </div>
    );
  };

  // Show message if no data
  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <p className="text-lg font-medium">No machine data available</p>
          <p className="text-sm mt-1">Data will appear once machines report their status</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="machine" 
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
            interval={0}
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            domain={[0, 100]}
            ticks={[0, 25, 50, 75, 100]}
            label={{ value: 'Utilization %', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar 
            dataKey="utilization" 
            fill="#3b82f6"
            radius={[4, 4, 0, 0]}
            name="Utilization"
          />
          <Bar 
            dataKey="target" 
            fill="#e5e7eb"
            radius={[4, 4, 0, 0]}
            name="Target"
          />
        </BarChart>
      </ResponsiveContainer>
      
      <CustomLegend />
      
      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-3 gap-4 text-center">
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 uppercase">Average</p>
          <p className="text-lg font-bold text-gray-900">{stats.average.toFixed(1)}%</p>
        </div>
        <div className="bg-green-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 uppercase">Meeting Target</p>
          <p className="text-lg font-bold text-green-600">
            {stats.meetingTarget}/{chartData.length}
          </p>
        </div>
        <div className="bg-yellow-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 uppercase">Below Target</p>
          <p className="text-lg font-bold text-yellow-600">
            {stats.belowTarget}/{chartData.length}
          </p>
        </div>
      </div>
    </div>
  );
};