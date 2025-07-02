import React, { useState } from 'react';
import { 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Clock,
  TrendingDown,
  Activity,
  Filter
} from 'lucide-react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { useAnomalies, useGenerateRecommendation } from '../../hooks/useAnalytics';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ErrorMessage } from '../common/ErrorMessage';
import { formatDistanceToNow } from 'date-fns';
import { Anomaly } from '../../types';

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'critical':
      return 'bg-red-100 text-red-800 border-red-200';
    case 'high':
      return 'bg-orange-100 text-orange-800 border-orange-200';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'low':
      return 'bg-green-100 text-green-800 border-green-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'bottleneck':
      return Activity;
    case 'delay':
      return Clock;
    case 'efficiency':
      return TrendingDown;
    default:
      return AlertTriangle;
  }
};

export const AnomaliesView: React.FC = () => {
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedAnomaly, setSelectedAnomaly] = useState<Anomaly | null>(null);
  
  const { data: anomalies = [], isLoading, isError, error, refetch } = useAnomalies();
  const generateRecommendation = useGenerateRecommendation();

  const filteredAnomalies = anomalies.filter(anomaly => {
    if (selectedSeverity !== 'all' && anomaly.severity !== selectedSeverity) return false;
    if (selectedType !== 'all' && anomaly.type !== selectedType) return false;
    return true;
  });

  const handleRequestAnalysis = (anomaly: Anomaly) => {
    const prompt = `Analyze this specific anomaly and provide detailed recommendations: ${anomaly.description}. 
    Current value: ${anomaly.metrics.current_value}, Expected value: ${anomaly.metrics.expected_value}. 
    Please provide specific actions to resolve this issue.`;
    generateRecommendation.mutate(prompt);
  };

  if (isLoading) {
    return <LoadingSpinner text="Loading anomalies..." />;
  }

  if (isError) {
    return (
      <ErrorMessage 
        title="Failed to load anomalies"
        message={error?.message || 'An error occurred while loading anomalies.'}
        onRetry={refetch}
      />
    );
  }

  const severityCounts = {
    critical: anomalies.filter(a => a.severity === 'critical').length,
    high: anomalies.filter(a => a.severity === 'high').length,
    medium: anomalies.filter(a => a.severity === 'medium').length,
    low: anomalies.filter(a => a.severity === 'low').length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <AlertTriangle className="h-8 w-8 text-orange-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Production Anomalies</h1>
            <p className="text-gray-600">Real-time anomaly detection and management</p>
          </div>
        </div>
        <Button
          variant="outline"
          onClick={() => refetch()}
          icon={Activity}
        >
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className={selectedSeverity === 'critical' ? 'ring-2 ring-red-500' : ''}>
          <button
            onClick={() => setSelectedSeverity(selectedSeverity === 'critical' ? 'all' : 'critical')}
            className="w-full p-4 text-left hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Critical</p>
                <p className="text-2xl font-bold text-red-600">{severityCounts.critical}</p>
              </div>
              <div className="p-3 bg-red-100 rounded-lg">
                <XCircle className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </button>
        </Card>

        <Card className={selectedSeverity === 'high' ? 'ring-2 ring-orange-500' : ''}>
          <button
            onClick={() => setSelectedSeverity(selectedSeverity === 'high' ? 'all' : 'high')}
            className="w-full p-4 text-left hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">High</p>
                <p className="text-2xl font-bold text-orange-600">{severityCounts.high}</p>
              </div>
              <div className="p-3 bg-orange-100 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-orange-600" />
              </div>
            </div>
          </button>
        </Card>

        <Card className={selectedSeverity === 'medium' ? 'ring-2 ring-yellow-500' : ''}>
          <button
            onClick={() => setSelectedSeverity(selectedSeverity === 'medium' ? 'all' : 'medium')}
            className="w-full p-4 text-left hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Medium</p>
                <p className="text-2xl font-bold text-yellow-600">{severityCounts.medium}</p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </button>
        </Card>

        <Card className={selectedSeverity === 'low' ? 'ring-2 ring-green-500' : ''}>
          <button
            onClick={() => setSelectedSeverity(selectedSeverity === 'low' ? 'all' : 'low')}
            className="w-full p-4 text-left hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Low</p>
                <p className="text-2xl font-bold text-green-600">{severityCounts.low}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </button>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <div className="p-4">
          <div className="flex items-center gap-4">
            <Filter className="h-5 w-5 text-gray-500" />
            <div className="flex gap-2">
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="rounded-md border-gray-300 text-sm"
              >
                <option value="all">All Types</option>
                <option value="bottleneck">Bottleneck</option>
                <option value="delay">Delay</option>
                <option value="efficiency">Efficiency</option>
                <option value="quality">Quality</option>
                <option value="other">Other</option>
              </select>
            </div>
            {(selectedSeverity !== 'all' || selectedType !== 'all') && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSelectedSeverity('all');
                  setSelectedType('all');
                }}
              >
                Clear filters
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Anomalies List */}
      {filteredAnomalies.length === 0 ? (
        <Card>
          <div className="p-12 text-center">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No anomalies detected</h3>
            <p className="text-gray-600">
              {selectedSeverity !== 'all' || selectedType !== 'all' 
                ? 'No anomalies match the selected filters.'
                : 'All systems are operating within normal parameters.'}
            </p>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredAnomalies.map((anomaly) => {
            const Icon = getTypeIcon(anomaly.type);
            return (
              <Card key={anomaly.id} className="hover:shadow-md transition-shadow">
                <div className="p-6">
                  <div className="flex items-start gap-4">
                    <div className={`p-3 rounded-lg ${getSeverityColor(anomaly.severity)}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-medium text-gray-900">{anomaly.description}</h3>
                          <div className="flex items-center gap-4 mt-2">
                            {anomaly.machine && (
                              <span className="text-sm text-gray-600">
                                Machine: <span className="font-medium">{anomaly.machine}</span>
                              </span>
                            )}
                            {anomaly.phase && (
                              <span className="text-sm text-gray-600">
                                Phase: <span className="font-medium">{anomaly.phase}</span>
                              </span>
                            )}
                            <span className="text-sm text-gray-500">
                              Detected {formatDistanceToNow(new Date(anomaly.detected_at))} ago
                            </span>
                          </div>
                        </div>
                        <Badge variant={anomaly.severity as any}>
                          {anomaly.severity}
                        </Badge>
                      </div>
                      
                      <div className="mt-4 grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
                        <div>
                          <p className="text-xs text-gray-500">Current Value</p>
                          <p className="font-semibold text-gray-900">
                            {anomaly.metrics.current_value.toFixed(1)}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Expected Value</p>
                          <p className="font-semibold text-gray-900">
                            {anomaly.metrics.expected_value.toFixed(1)}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Deviation</p>
                          <p className="font-semibold text-red-600">
                            {anomaly.metrics.deviation_percentage.toFixed(1)}%
                          </p>
                        </div>
                      </div>
                      
                      <div className="mt-4 flex gap-2">
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => handleRequestAnalysis(anomaly)}
                          loading={generateRecommendation.isPending}
                        >
                          Get AI Recommendations
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedAnomaly(anomaly)}
                        >
                          View Details
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Detail Modal */}
      {selectedAnomaly && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Anomaly Details</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedAnomaly(null)}
                >
                  <XCircle className="h-5 w-5" />
                </Button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-500">Description</p>
                  <p className="font-medium">{selectedAnomaly.description}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Type</p>
                    <p className="font-medium capitalize">{selectedAnomaly.type}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Severity</p>
                    <Badge variant={selectedAnomaly.severity as any}>
                      {selectedAnomaly.severity}
                    </Badge>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="text-sm text-gray-500">Current Value</p>
                    <p className="text-lg font-semibold">{selectedAnomaly.metrics.current_value.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Expected Value</p>
                    <p className="text-lg font-semibold">{selectedAnomaly.metrics.expected_value.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Deviation</p>
                    <p className="text-lg font-semibold text-red-600">
                      {selectedAnomaly.metrics.deviation_percentage.toFixed(2)}%
                    </p>
                  </div>
                </div>
                
                <div className="pt-4 border-t">
                  <Button
                    variant="primary"
                    className="w-full"
                    onClick={() => {
                      handleRequestAnalysis(selectedAnomaly);
                      setSelectedAnomaly(null);
                    }}
                    loading={generateRecommendation.isPending}
                  >
                    Get Detailed AI Analysis
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};