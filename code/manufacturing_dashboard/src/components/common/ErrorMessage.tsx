import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ 
  title = 'Error', 
  message,
  onRetry 
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className="bg-danger-50 rounded-lg p-6 max-w-md w-full">
        <div className="flex items-start">
          <AlertCircle className="h-5 w-5 text-danger-600 mt-0.5 mr-3 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="text-sm font-medium text-danger-800">{title}</h3>
            <p className="mt-1 text-sm text-danger-700">{message}</p>
            {onRetry && (
              <button
                onClick={onRetry}
                className="mt-3 inline-flex items-center px-3 py-1.5 border border-danger-300 text-sm font-medium rounded-md text-danger-700 bg-white hover:bg-danger-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-danger-500"
              >
                <RefreshCw className="h-4 w-4 mr-1.5" />
                Retry
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};