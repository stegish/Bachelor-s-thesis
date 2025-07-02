import React from 'react';
import { 
  Zap, 
  AlertTriangle,
  ArrowRight,
  Clock
} from 'lucide-react';
import { Card } from '../common/Card';

interface PriorityActionCardProps {
  action: {
    id: string;
    description: string;
    urgency: 'high' | 'critical';
    estimated_impact: string;
  };
}

export const PriorityActionCard: React.FC<PriorityActionCardProps> = ({ action }) => {
  const urgencyConfig = {
    critical: {
      color: 'bg-danger-50 border-danger-200 text-danger-800',
      icon: AlertTriangle,
      label: 'Critical - Immediate Action Required',
      iconColor: 'text-danger-600',
    },
    high: {
      color: 'bg-orange-50 border-orange-200 text-orange-800',
      icon: Zap,
      label: 'High Priority',
      iconColor: 'text-orange-600',
    },
  };

  const config = urgencyConfig[action.urgency];
  const Icon = config.icon;

  return (
    <Card className={`border-2 ${config.color}`}>
      <div className="flex items-start">
        <Icon className={`h-6 w-6 ${config.iconColor} mt-1 mr-3 flex-shrink-0`} />
        
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold">{config.label}</span>
            <Clock className="h-4 w-4 text-gray-400" />
          </div>
          
          <p className="text-sm mb-3">{action.description}</p>
          
          <div className="flex items-center justify-between bg-white bg-opacity-60 rounded-lg p-2">
            <span className="text-xs text-gray-600">Expected Impact:</span>
            <span className="text-xs font-medium">{action.estimated_impact}</span>
          </div>
          
          <button className="mt-3 w-full flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-gray-900 hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900">
            Take Action
            <ArrowRight className="ml-2 h-4 w-4" />
          </button>
        </div>
      </div>
    </Card>
  );
};