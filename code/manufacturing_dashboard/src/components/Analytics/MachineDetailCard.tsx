import React from 'react';
import { Activity, User, Clock, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import { Card } from '../common/Card';
import { MachineMetrics } from '../../types';

interface MachineDetailCardProps {
  machine: MachineMetrics;
  isExpanded?: boolean;
  onToggle?: () => void;
}

export const MachineDetailCard: React.FC<MachineDetailCardProps> = ({ 
  machine, 
  isExpanded = false,
  onToggle 
}) => {
  const getStatusColor = (isActive: boolean) => {
    return isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (isActive: boolean) => {
    return isActive ? <Activity className="h-4 w-4" /> : <Clock className="h-4 w-4" />;
  };

  const getEfficiencyColor = (efficiency: number | null) => {
    if (efficiency === null) return 'text-gray-500';
    if (efficiency >= 80) return 'text-green-600';
    if (efficiency >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getUtilizationColor = (utilization: number | null) => {
    if (utilization === null) return 'text-gray-500';
    if (utilization >= 85) return 'text-green-600';
    if (utilization >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Card 
      className={`transition-all hover:shadow-lg ${onToggle ? 'cursor-pointer' : ''}`}
      onClick={onToggle}
    >
      <div className="space-y-4">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{machine.machine_name}</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(machine.is_active)}`}>
                {getStatusIcon(machine.is_active)}
                {machine.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
          <TrendingUp className="h-5 w-5 text-gray-400" />
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Utilization</p>
            <div className="flex items-baseline gap-2">
              <p className={`text-2xl font-bold ${getUtilizationColor(machine.utilization_percentage)}`}>
                {machine.utilization_percentage !== null 
                  ? `${machine.utilization_percentage.toFixed(1)}%`
                  : 'N/A'}
              </p>
              <span className="text-xs text-gray-500">target: 85%</span>
            </div>
            {machine.utilization_percentage !== null && (
              <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${machine.utilization_percentage >= 85 ? 'bg-green-500' : 'bg-yellow-500'}`}
                  style={{ width: `${Math.min(machine.utilization_percentage, 100)}%` }}
                />
              </div>
            )}
          </div>
          
          <div>
            <p className="text-sm text-gray-500">Efficiency</p>
            <div className="flex items-baseline gap-2">
              <p className={`text-2xl font-bold ${getEfficiencyColor(machine.efficiency_percentage)}`}>
                {machine.efficiency_percentage !== null 
                  ? `${machine.efficiency_percentage.toFixed(1)}%`
                  : 'N/A'}
              </p>
              <span className="text-xs text-gray-500">OEE</span>
            </div>
            {machine.efficiency_percentage !== null && (
              <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${machine.efficiency_percentage >= 75 ? 'bg-green-500' : 'bg-yellow-500'}`}
                  style={{ width: `${Math.min(machine.efficiency_percentage, 100)}%` }}
                />
              </div>
            )}
          </div>
        </div>

        {/* Queue and Phase Info */}
        <div className="border-t pt-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Queue Length</span>
              <p className="font-medium">{machine.current_queue_length} items</p>
            </div>
            <div>
              <span className="text-gray-500">Phases Processed</span>
              <p className="font-medium">{machine.total_phases_processed}</p>
            </div>
          </div>
        </div>

        {/* Expanded Details */}
        {isExpanded && (
          <div className="border-t pt-4 space-y-3">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Avg Cycle Time</span>
                <p className="font-medium">{machine.avg_cycle_time.toFixed(1)} min</p>
              </div>
              <div>
                <span className="text-gray-500">Avg Queue Delay</span>
                <p className="font-medium">{machine.avg_queue_delay.toFixed(1)} hrs</p>
              </div>
              <div>
                <span className="text-gray-500">Completed Phases</span>
                <p className="font-medium">{machine.completed_phases}</p>
              </div>
              <div>
                <span className="text-gray-500">In Progress</span>
                <p className="font-medium">{machine.in_progress_phases}</p>
              </div>
              <div>
                <span className="text-gray-500">Total Quantity</span>
                <p className="font-medium">{machine.total_quantity_processed} units</p>
              </div>
              <div>
                <span className="text-gray-500">Operators</span>
                <p className="font-medium">{machine.unique_operators}</p>
              </div>
            </div>

            {/* Performance Indicators */}
            <div className="flex items-center gap-2">
              {machine.efficiency_percentage !== null && machine.efficiency_percentage < 70 && (
                <div className="flex items-center gap-1 text-warning-600 text-sm">
                  <AlertTriangle className="h-4 w-4" />
                  <span>Low efficiency</span>
                </div>
              )}
              {machine.utilization_percentage !== null && machine.utilization_percentage < 70 && (
                <div className="flex items-center gap-1 text-warning-600 text-sm">
                  <AlertTriangle className="h-4 w-4" />
                  <span>Low utilization</span>
                </div>
              )}
              {machine.efficiency_percentage !== null && machine.efficiency_percentage >= 80 && (
                <div className="flex items-center gap-1 text-success-600 text-sm">
                  <CheckCircle className="h-4 w-4" />
                  <span>High performance</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};