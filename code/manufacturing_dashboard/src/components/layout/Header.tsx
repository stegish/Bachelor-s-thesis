import React from 'react';
import { Activity, RefreshCw, Bell, Settings } from 'lucide-react';
import { useAnalyticsStatus } from '../../hooks/useAnalytics';
import { formatRelativeTime } from '../../utils';

export const Header: React.FC = () => {
  const { data: status, refetch } = useAnalyticsStatus();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Title */}
          <div className="flex items-center">
            <Activity className="h-8 w-8 text-primary-600 mr-3" />
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Manufacturing Analytics</h1>
              <p className="text-sm text-gray-500">Real-time Production Monitoring</p>
            </div>
          </div>

          {/* Status and Actions */}
          <div className="flex items-center space-x-4">
            {/* Last Update Status */}
            {status?.last_run && (
              <div className="text-sm text-gray-600">
                Last update: {formatRelativeTime(status.last_run)}
              </div>
            )}

            {/* Refresh Button */}
            <button
              onClick={() => refetch()}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
              title="Refresh data"
            >
              <RefreshCw className="h-5 w-5" />
            </button>

            {/* Notifications (placeholder) */}
            <button
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors relative"
              title="Notifications"
            >
              <Bell className="h-5 w-5" />
              <span className="absolute top-0 right-0 h-2 w-2 bg-danger-500 rounded-full"></span>
            </button>

            {/* Settings (placeholder) */}
            <button
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
              title="Settings"
            >
              <Settings className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};