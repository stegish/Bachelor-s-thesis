import React from 'react';
import { 
  Wrench, 
  TrendingUp, 
  AlertCircle, 
  Lightbulb,
  CheckCircle,
  ChevronRight
} from 'lucide-react';
import { Card } from '../common/Card';

interface RecommendationCardProps {
  recommendation: {
    id: string;
    description: string;
    priority: 'low' | 'medium' | 'high';
    type: 'maintenance' | 'optimization' | 'alert' | 'improvement';
  };
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation }) => {
  const typeConfig = {
    maintenance: {
      icon: Wrench,
      color: 'text-orange-600 bg-orange-50',
      label: 'Maintenance',
    },
    optimization: {
      icon: TrendingUp,
      color: 'text-primary-600 bg-primary-50',
      label: 'Optimization',
    },
    alert: {
      icon: AlertCircle,
      color: 'text-danger-600 bg-danger-50',
      label: 'Alert',
    },
    improvement: {
      icon: Lightbulb,
      color: 'text-success-600 bg-success-50',
      label: 'Improvement',
    },
  };

  const priorityColors = {
    low: 'border-gray-200',
    medium: 'border-warning-200',
    high: 'border-danger-200',
  };

  const config = typeConfig[recommendation.type];
  const Icon = config.icon;

  return (
    <Card className={`border-2 ${priorityColors[recommendation.priority]} hover:shadow-md transition-all`}>
      <div className="flex items-start">
        <div className={`p-3 rounded-lg ${config.color} mr-4`}>
          <Icon className="h-6 w-6" />
        </div>
        
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-900">{config.label}</span>
            <span className={`text-xs px-2 py-1 rounded-full ${
              recommendation.priority === 'high' ? 'bg-danger-100 text-danger-700' :
              recommendation.priority === 'medium' ? 'bg-warning-100 text-warning-700' :
              'bg-gray-100 text-gray-700'
            }`}>
              {recommendation.priority} priority
            </span>
          </div>
          
          <p className="text-sm text-gray-700 mb-3">{recommendation.description}</p>
          
          <div className="flex items-center justify-between">
            <button className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center">
              <CheckCircle className="h-4 w-4 mr-1" />
              Mark as Done
            </button>
            <button className="text-sm text-gray-500 hover:text-gray-700 flex items-center">
              Details
              <ChevronRight className="h-4 w-4 ml-1" />
            </button>
          </div>
        </div>
      </div>
    </Card>
  );
};