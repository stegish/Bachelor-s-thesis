import React from 'react';
import { Activity, User, Clock, TrendingUp } from 'lucide-react';
import { Card } from '../common/Card';

interface Machine {
  id: string;
  name: string;
  status: 'running' | 'idle' | 'maintenance' | 'error';
  utilization: number;
  efficiency: number;
  operator: string;
  lastMaintenance: string;
  currentOrder?: string;
  producedToday: number;
  targetToday: number;
}

interface MachineDetailCardProps {
  machine: Machine;
  onClick?: (machine: Machine) => void;
}

export const MachineDetailCard: React.FC<MachineDetailCardProps> = ({ 
  machine, 
  onClick 
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-green-100 text-green-800';
      case 'idle':
        return 'bg-yellow-100 text-yellow-800';
      case 'maintenance':
        return 'bg-blue-100 text-blue-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Activity className="h-4 w-4" />;
      case 'idle':
        return <Clock className="h-4 w-4" />;
      case 'maintenance':
        return <Clock className="h-4 w-4" />;
      case 'error':
        return <Activity className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  const handleClick = () => {
    if (onClick) {
      onClick(machine);
    }
  };

  return (
    <Card 
      className={`transition-all hover:shadow-lg ${onClick ? 'cursor-pointer' : ''}`}
      onClick={handleClick}
    >
      <div className="space-y-4">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{machine.name}</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(machine.status)}`}>
                {getStatusIcon(machine.status)}
                {machine.status.charAt(0).toUpperCase() + machine.status.slice(1)}
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
              <p className="text-2xl font-bold text-gray-900">{machine.utilization}%</p>
              <span className="text-xs text-gray-500">target: 85%</span>
            </div>
            <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${machine.utilization >= 85 ? 'bg-green-500' : 'bg-yellow-500'}`}
                style={{ width: `${machine.utilization}%` }}
              />
            </div>
          </div>
          
          <div>
            <p className="text-sm text-gray-500">Efficiency</p>
            <div className="flex items-baseline gap-2">
              <p className="text-2xl font-bold text-gray-900">{machine.efficiency}%</p>
              <span className="text-xs text-gray-500">OEE</span>
            </div>
            <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${machine.efficiency >= 75 ? 'bg-green-500' : 'bg-yellow-500'}`}
                style={{ width: `${machine.efficiency}%` }}
              />
            </div>
          </div>
        </div>

        {/* Production Info */}
        <div className="border-t pt-4">
          <div className="flex justify-between items-center mb-2">
            <p className="text-sm text-gray-500">Today's Production</p>
            <p className="text-sm font-medium">
              {machine.producedToday} / {machine.targetToday} units
            </p>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="h-2 rounded-full bg-blue-500"
              style={{ width: `${(machine.producedToday / machine.targetToday) * 100}%` }}
            />
          </div>
        </div>

        {/* Additional Info */}
        <div className="border-t pt-4 space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500 flex items-center gap-1">
              <User className="h-4 w-4" />
              Operator
            </span>
            <span className="font-medium">{machine.operator}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500 flex items-center gap-1">
              <Clock className="h-4 w-4" />
              Last Maintenance
            </span>
            <span className="font-medium">{machine.lastMaintenance}</span>
          </div>
          {machine.currentOrder && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Current Order</span>
              <span className="font-medium">{machine.currentOrder}</span>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};