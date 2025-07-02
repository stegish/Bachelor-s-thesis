import React from 'react';
import { AlertTriangle, Clock, Package } from 'lucide-react';
import { QueueAnalysis } from '../../types';
import { formatDuration, formatNumber } from '../../utils';

interface BottlenecksListProps {
  data: QueueAnalysis[];
}

export const BottlenecksList: React.FC<BottlenecksListProps> = ({ data }) => {
  const bottlenecks = data
    .filter(item => item.is_bottleneck)
    .sort((a, b) => b.avg_queue_delay - a.avg_queue_delay);

  if (bottlenecks.length === 0) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500">No bottlenecks detected</p>
        <p className="text-sm text-gray-400 mt-2">
          All production phases are running within acceptable parameters
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Phase
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Avg Queue Delay
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Max Delay
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Jobs in Queue
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Total Quantity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Severity
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {bottlenecks.map((bottleneck, index) => {
              const severity = bottleneck.avg_queue_delay > 10 ? 'critical' : 
                             bottleneck.avg_queue_delay > 5 ? 'high' : 'medium';
              
              const severityColors = {
                critical: 'bg-danger-100 text-danger-800',
                high: 'bg-orange-100 text-orange-800',
                medium: 'bg-warning-100 text-warning-800',
              };

              return (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <AlertTriangle className="h-4 w-4 text-warning-500 mr-2" />
                      <span className="text-sm font-medium text-gray-900">
                        {bottleneck.phase_name}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center text-sm text-gray-900">
                      <Clock className="h-4 w-4 text-gray-400 mr-1" />
                      {formatDuration(bottleneck.avg_queue_delay)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDuration(bottleneck.max_queue_delay)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatNumber(bottleneck.total_jobs)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center text-sm text-gray-900">
                      <Package className="h-4 w-4 text-gray-400 mr-1" />
                      {formatNumber(bottleneck.total_quantity)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${severityColors[severity]}`}>
                      {severity}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};