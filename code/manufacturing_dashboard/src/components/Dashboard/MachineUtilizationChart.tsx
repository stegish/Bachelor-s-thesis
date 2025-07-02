import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface MachineUtilizationData {
  machine: string;
  utilization: number;
  target: number;
}

interface MachineUtilizationChartProps {
  data?: MachineUtilizationData[];
  height?: number;
}

const defaultData: MachineUtilizationData[] = [
  { machine: 'CNC-01', utilization: 85, target: 85 },
  { machine: 'CNC-02', utilization: 78, target: 85 },
  { machine: 'LATHE-01', utilization: 92, target: 85 },
  { machine: 'MILL-01', utilization: 67, target: 85 },
  { machine: 'MILL-02', utilization: 89, target: 85 },
  { machine: 'DRILL-01', utilization: 73, target: 85 },
  { machine: 'WELD-01', utilization: 81, target: 85 },
  { machine: 'ASSM-01', utilization: 95, target: 85 }
];

export const MachineUtilizationChart: React.FC<MachineUtilizationChartProps> = ({
  data = defaultData,
  height = 300
}) => {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 shadow-lg rounded-lg border border-gray-200">
          <p className="font-semibold text-gray-900">{label}</p>
          <p className="text-sm text-gray-600 mt-1">
            Utilization: <span className="font-medium">{payload[0].value}%</span>
          </p>
          <p className="text-sm text-gray-600">
            Target: <span className="font-medium">{payload[1].value}%</span>
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {payload[0].value >= payload[1].value ? '✅ Meeting target' : '⚠️ Below target'}
          </p>
        </div>
      );
    }
    return null;
  };

  const CustomLegend = (props: any) => {
    return (
      <div className="flex justify-center gap-4 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded"></div>
          <span className="text-sm text-gray-600">Actual Utilization</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-gray-300 rounded"></div>
          <span className="text-sm text-gray-600">Target (85%)</span>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="machine" 
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            domain={[0, 100]}
            ticks={[0, 25, 50, 75, 100]}
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
          <p className="text-lg font-bold text-gray-900">81.3%</p>
        </div>
        <div className="bg-green-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 uppercase">Meeting Target</p>
          <p className="text-lg font-bold text-green-600">4/8</p>
        </div>
        <div className="bg-yellow-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 uppercase">Below Target</p>
          <p className="text-lg font-bold text-yellow-600">4/8</p>
        </div>
      </div>
    </div>
  );
};