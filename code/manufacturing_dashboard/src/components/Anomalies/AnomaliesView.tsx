import React, { useState } from 'react';
import { Card } from '../common/Card';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { AnomalyCard } from './AnomalyCard';
import { useAnomalies, useGenerateRecommendation } from '../../hooks/useAnalytics';
import { Anomaly } from '../../types';
import { AlertTriangle, RefreshCw, Sparkles, Filter } from 'lucide-react';
import { getSeverityColor } from '../../utils';

export const AnomaliesView: React.FC = () => {
  const { data: anomalies = [], isLoading, refetch } = useAnomalies();
  const generateRecommendation = useGenerateRecommendation();
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');

  if (isLoading) {
    return <LoadingSpinner text="Detecting anomalies..." />;
  }

  // Filter anomalies
  const filteredAnomalies = anomalies.filter(anomaly => {
    const matchesSeverity = selectedSeverity === 'all' || anomaly.severity === selectedSeverity;
    const matchesType = selectedType === 'all' || anomaly.type === selectedType;
    return matchesSeverity && matchesType;
  });

  // Group anomalies by severity
  const anomaliesBySeverity = filteredAnomalies.reduce((acc, anomaly) => {
    if (!acc[anomaly.severity]) {
      acc[anomaly.severity] = [];
    }
    acc[anomaly.severity].push(anomaly);
    return acc;
  }, {} as Record<string, Anomaly[]>);

  const handleGenerateRecommendations = async () => {
    const anomalyContext = anomalies.map(a => ({
      type: a.type,
      severity: a.severity,
      description: a.description,
      metrics: a.metrics,
    }));

    const customPrompt = `
      Analyze the following production anomalies and provide specific recommendations:
      ${JSON.stringify(anomalyContext, null, 2)}
      
      For each anomaly, suggest:
      1. Immediate actions to mitigate the issue
      2. Root cause analysis steps
      3. Preventive measures for the future
      
      Prioritize recommendations by severity and potential impact.
    `;

    await generateRecommendation.mutateAsync(customPrompt);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">Production Anomalies</h2>
          <p className="mt-1 text-sm text-gray-500">
            Real-time detection and monitoring of production issues
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Filters */}
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">All Types</option>
              <option value="bottleneck">Bottleneck</option>
              <option value="efficiency">Efficiency</option>
              <option value="delay">Delay</option>
              <option value="quality">Quality</option>
            </select>
          </div>

          {/* Actions */}
          <button
            onClick={() => refetch()}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </button>
          
          {anomalies.length > 0 && (
            <button
              onClick={handleGenerateRecommendations}
              disabled={generateRecommendation.isPending}
              className="inline-flex items-center px-3 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Sparkles className="h-4 w-4 mr-2" />
              {generateRecommendation.isPending ? 'Generating...' : 'Get AI Recommendations'}
            </button>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Anomalies</p>
              <p className="text-2xl font-semibold mt-1">{anomalies.length}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-warning-500" />
          </div>
        </Card>
        
        {['critical', 'high', 'medium', 'low'].map((severity) => {
          const count = anomalies.filter(a => a.severity === severity).length;
          return (
            <Card key={severity} className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 capitalize">{severity} Severity</p>
                  <p className="text-2xl font-semibold mt-1">{count}</p>
                </div>
                <div className={`w-3 h-3 rounded-full ${
                  severity === 'critical' ? 'bg-danger-500' :
                  severity === 'high' ? 'bg-orange-500' :
                  severity === 'medium' ? 'bg-warning-500' :
                  'bg-blue-500'
                }`} />
              </div>
            </Card>
          );
        })}
      </div>

      {/* Anomalies List */}
      {filteredAnomalies.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No anomalies detected</p>
            <p className="text-sm text-gray-400 mt-2">
              {selectedSeverity !== 'all' || selectedType !== 'all' 
                ? 'Try adjusting your filters'
                : 'All systems are operating within normal parameters'}
            </p>
          </div>
        </Card>
      ) : (
        <div className="space-y-6">
          {(['critical', 'high', 'medium', 'low'] as const).map((severity) => {
            const severityAnomalies = anomaliesBySeverity[severity] || [];
            if (severityAnomalies.length === 0) return null;

            return (
              <div key={severity}>
                <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
                  <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                    severity === 'critical' ? 'bg-danger-500' :
                    severity === 'high' ? 'bg-orange-500' :
                    severity === 'medium' ? 'bg-warning-500' :
                    'bg-blue-500'
                  }`} />
                  {severity.charAt(0).toUpperCase() + severity.slice(1)} Priority
                  <span className="ml-2 text-sm text-gray-500">({severityAnomalies.length})</span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {severityAnomalies.map((anomaly) => (
                    <AnomalyCard key={anomaly.id} anomaly={anomaly} />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};