import React from 'react';
import { 
  AlertTriangle, 
  Clock, 
  TrendingDown, 
  Gauge,
  ChevronRight,
  AlertCircle,
  Info,
  XCircle
} from 'lucide-react';
import { Anomaly } from '../../types';
import { Card } from '../common/Card';
import { formatRelativeTime, formatPercentage, getSeverityColor, getSeverityIcon } from '../../utils';

interface AnomalyCardProps {
  anomaly: Anomaly;
  onSelect?: () => void;
}

export const AnomalyCard: React.FC<AnomalyCardProps> = ({ anomaly, onSelect }) => {
  const typeIcons = {
    bottleneck: Clock,
    efficiency: TrendingDown,
    delay: Clock,
    quality: AlertCircle,
    other: Info,
  };

  const severityIcons = {
    low: Info,
    medium: AlertTriangle,
    high: AlertCircle,
    critical: XCircle,
  };

  const TypeIcon = typeIcons[anomaly.type] || Info;
  const SeverityIcon = severityIcons[anomaly.severity];

  return (
    <Card 
      className={`hover:shadow-md transition-all cursor-pointer border-l-4 ${
        anomaly.severity === 'critical' ? 'border-l-danger-500' :
        anomaly.severity === 'high' ? 'border-l-orange-500' :
        anomaly.severity === 'medium' ? 'border-l-warning-500' :
        'border-l-blue-500'
      }`}
      onClick={onSelect}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-start">
          <div className={`p-2 rounded-lg ${getSeverityColor(anomaly.severity)} mr-3`}>
            <SeverityIcon className="h-5 w-5" />
          </div>
          <div>
            <h4 className="font-medium text-gray-900">
              {anomaly.machine && `${anomaly.machine} - `}
              {anomaly.phase || anomaly.type.charAt(0).toUpperCase() + anomaly.type.slice(1)}
            </h4>
            <p className="text-sm text-gray-500 mt-1">
              Detected {formatRelativeTime(anomaly.detected_at)}
            </p>
          </div>
        </div>
        
        {/* Severity Badge */}
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${getSeverityColor(anomaly.severity)}`}>
          {anomaly.severity}
        </span>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-700 mb-4">{anomaly.description}</p>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="text-center p-2 bg-gray-50 rounded">
          <Gauge className="h-4 w-4 text-gray-400 mx-auto mb-1" />
          <p className="text-xs text-gray-500">Current</p>
          <p className="text-sm font-medium">
            {anomaly.metrics.current_value.toFixed(1)}
          </p>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded">
          <TypeIcon className="h-4 w-4 text-gray-400 mx-auto mb-1" />
          <p className="text-xs text-gray-500">Expected</p>
          <p className="text-sm font-medium">
            {anomaly.metrics.expected_value.toFixed(1)}
          </p>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded">
          <TrendingDown className="h-4 w-4 text-gray-400 mx-auto mb-1" />
          <p className="text-xs text-gray-500">Deviation</p>
          <p className="text-sm font-medium text-danger-600">
            {formatPercentage(anomaly.metrics.deviation_percentage)}
          </p>
        </div>
      </div>

      {/* Action */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-200">
        <span className="text-sm text-gray-500">
          Type: <span className="font-medium capitalize">{anomaly.type}</span>
        </span>
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center">
          View Details
          <ChevronRight className="h-4 w-4 ml-1" />
        </button>
      </div>
    </Card>
  );
};