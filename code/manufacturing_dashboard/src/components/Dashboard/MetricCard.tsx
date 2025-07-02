import React from 'react';
import { TrendingUp, TrendingDown, Minus, type LucideIcon } from 'lucide-react';

export interface MetricCardProps {
  title: string;
  value: string;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: LucideIcon;
  color?: string;
  subtitle?: string;
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  trend = 'neutral',
  icon: Icon,
  color = 'text-gray-600',
  subtitle,
  onClick
}) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      case 'neutral':
        return <Minus className="h-4 w-4 text-gray-400" />;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      case 'neutral':
        return 'text-gray-600';
    }
  };

  return (
    <div 
      className={`bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Title */}
          <p className="text-sm font-medium text-gray-600">{title}</p>
          
          {/* Value */}
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
          
          {/* Change and Trend */}
          {change && (
            <div className="mt-2 flex items-center gap-2">
              {getTrendIcon()}
              <span className={`text-sm font-medium ${getTrendColor()}`}>
                {change}
              </span>
              {subtitle && (
                <span className="text-sm text-gray-500">{subtitle}</span>
              )}
            </div>
          )}
        </div>
        
        {/* Icon */}
        {Icon && (
          <div className={`p-3 rounded-full bg-gray-50 ${color}`}>
            <Icon className="h-6 w-6" />
          </div>
        )}
      </div>
    </div>
  );
};