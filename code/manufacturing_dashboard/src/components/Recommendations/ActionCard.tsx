import React from 'react';
import { AlertTriangle, Zap, CheckCircle, XCircle } from 'lucide-react';
import { Button } from '../common/Button';

interface ActionCardProps {
  action: {
    id: string;
    description: string;
    urgency: string;
    action?: string;
    parameters?: Record<string, any>;
    estimated_impact?: string;
  };
  onExecute: () => void;
  onReject?: () => void;
  loading?: boolean;
}

export const ActionCard: React.FC<ActionCardProps> = ({
  action,
  onExecute,
  onReject,
  loading = false
}) => {
  const urgencyConfig = {
    critical: {
      color: 'border-red-500 bg-red-50',
      icon: AlertTriangle,
      iconColor: 'text-red-600'
    },
    high: {
      color: 'border-orange-500 bg-orange-50', 
      icon: Zap,
      iconColor: 'text-orange-600'
    }
  };

  const config = urgencyConfig[action.urgency] || urgencyConfig.high;
  const Icon = config.icon;

  return (
    <div className={`p-4 border-2 rounded-lg ${config.color} transition-all hover:shadow-lg`}>
      <div className="flex items-start gap-3">
        <Icon className={`h-6 w-6 ${config.iconColor} mt-1`} />
        
        <div className="flex-1">
          <div className="mb-2">
            <span className={`text-xs font-semibold uppercase ${config.iconColor}`}>
              {action.urgency} ACTION REQUIRED
            </span>
          </div>
          
          <p className="text-gray-800 font-medium mb-3">{action.description}</p>
          
          {action.action && action.parameters && (
            <div className="bg-white bg-opacity-60 rounded p-3 mb-3">
              <p className="text-xs text-gray-600 mb-1">Command to execute:</p>
              <code className="text-sm font-mono block mb-2">{action.action}</code>
              
              <p className="text-xs text-gray-600 mb-1">Parameters:</p>
              <pre className="text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                {JSON.stringify(action.parameters, null, 2)}
              </pre>
            </div>
          )}
          
          {action.estimated_impact && (
            <p className="text-sm text-gray-600 mb-3">
              <strong>Expected Impact:</strong> {action.estimated_impact}
            </p>
          )}
          
          <div className="flex gap-2">
            {action.action && action.parameters ? (
              <>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={onExecute}
                  loading={loading}
                  className="flex-1"
                >
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Execute Action
                </Button>
                {onReject && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={onReject}
                    disabled={loading}
                  >
                    <XCircle className="h-4 w-4 mr-1" />
                    Reject
                  </Button>
                )}
              </>
            ) : (
              <p className="text-sm text-gray-500 italic">
                No executable action available - manual intervention required
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};