import React, { useState } from 'react';
import { 
  Sparkles, 
  RefreshCw, 
  AlertTriangle, 
  CheckCircle,
  Clock,
  TrendingUp,
  Wrench,
  AlertCircle,
  MessageSquare,
  Send
} from 'lucide-react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ErrorMessage } from '../common/ErrorMessage';
import { useLatestRecommendation, useGenerateRecommendation } from '../../hooks/useAnalytics';
import { formatDistanceToNow } from 'date-fns';

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'critical':
    case 'high':
      return 'text-red-600 bg-red-50';
    case 'medium':
      return 'text-yellow-600 bg-yellow-50';
    case 'low':
      return 'text-green-600 bg-green-50';
    default:
      return 'text-gray-600 bg-gray-50';
  }
};

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'maintenance':
      return Wrench;
    case 'optimization':
      return TrendingUp;
    case 'alert':
      return AlertCircle;
    default:
      return CheckCircle;
  }
};

export const RecommendationsView: React.FC = () => {
  const [customPrompt, setCustomPrompt] = useState('');
  const [showCustomPrompt, setShowCustomPrompt] = useState(false);
  
  const { data: recommendation, isLoading, isError, error } = useLatestRecommendation();
  const generateMutation = useGenerateRecommendation();

  const handleGenerateNew = (prompt?: string) => {
    generateMutation.mutate(prompt);
    setCustomPrompt('');
    setShowCustomPrompt(false);
  };

  if (isLoading) {
    return <LoadingSpinner text="Loading recommendations..." />;
  }

  if (isError && error?.response?.status !== 404) {
    return (
      <ErrorMessage 
        title="Failed to load recommendations"
        message={error?.message || 'An error occurred while loading recommendations.'}
        onRetry={() => window.location.reload()}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Sparkles className="h-8 w-8 text-purple-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Insights & Recommendations</h1>
            <p className="text-gray-600">AI-powered analysis and actionable recommendations</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setShowCustomPrompt(!showCustomPrompt)}
            icon={MessageSquare}
          >
            Custom Analysis
          </Button>
          <Button
            variant="primary"
            onClick={() => handleGenerateNew()}
            loading={generateMutation.isPending}
            icon={RefreshCw}
          >
            Generate New
          </Button>
        </div>
      </div>

      {/* Custom Prompt Input */}
      {showCustomPrompt && (
        <Card>
          <div className="p-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Custom Analysis Prompt
            </label>
            <div className="flex gap-2">
              <textarea
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="Ask a specific question about your manufacturing data..."
                className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                rows={3}
              />
              <Button
                variant="primary"
                onClick={() => handleGenerateNew(customPrompt)}
                disabled={!customPrompt.trim()}
                loading={generateMutation.isPending}
                icon={Send}
              >
                Analyze
              </Button>
            </div>
          </div>
        </Card>
      )}

      {!recommendation && !generateMutation.isPending ? (
        <Card>
          <div className="p-12 text-center">
            <Sparkles className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No recommendations yet</h3>
            <p className="text-gray-600 mb-6">Generate your first AI-powered analysis to get started</p>
            <Button
              variant="primary"
              onClick={() => handleGenerateNew()}
              icon={RefreshCw}
            >
              Generate Recommendations
            </Button>
          </div>
        </Card>
      ) : recommendation ? (
        <>
          {/* Analysis Summary */}
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Latest Analysis</h2>
                <span className="text-sm text-gray-500">
                  Generated {formatDistanceToNow(new Date(recommendation.timestamp))} ago
                </span>
              </div>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{recommendation.analysis}</p>
              </div>
            </div>
          </Card>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Machine Utilization</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {recommendation.metrics_analyzed.avg_machine_utilization?.toFixed(1) || 'N/A'}%
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-blue-600" />
                </div>
              </div>
            </Card>
            
            <Card>
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">On-Time Delivery</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {recommendation.metrics_analyzed.on_time_delivery_rate?.toFixed(1) || 'N/A'}%
                    </p>
                  </div>
                  <Clock className="h-8 w-8 text-green-600" />
                </div>
              </div>
            </Card>
            
            <Card>
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Anomalies Detected</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {recommendation.anomalies_detected.length}
                    </p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-red-600" />
                </div>
              </div>
            </Card>
          </div>

          {/* Priority Actions */}
          {recommendation.priority_actions.length > 0 && (
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Priority Actions</h3>
                <div className="space-y-3">
                  {recommendation.priority_actions.map((action) => (
                    <div
                      key={action.id}
                      className="flex items-start gap-3 p-4 bg-red-50 rounded-lg border border-red-200"
                    >
                      <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{action.description}</p>
                        {action.estimated_impact && (
                          <p className="text-sm text-gray-600 mt-1">
                            Expected Impact: {action.estimated_impact}
                          </p>
                        )}
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        action.urgency === 'critical' ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'
                      }`}>
                        {action.urgency}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          )}

          {/* Recommendations */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recommendation.recommendations.map((rec) => {
                  const Icon = getTypeIcon(rec.type);
                  return (
                    <div
                      key={rec.id}
                      className="p-4 border rounded-lg hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-lg ${getPriorityColor(rec.priority)}`}>
                          <Icon className="h-5 w-5" />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{rec.description}</p>
                          <div className="flex items-center gap-4 mt-2">
                            <span className="text-xs text-gray-500">Type: {rec.type}</span>
                            <span className={`text-xs font-medium ${
                              rec.priority === 'high' ? 'text-red-600' :
                              rec.priority === 'medium' ? 'text-yellow-600' :
                              'text-green-600'
                            }`}>
                              {rec.priority} priority
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </Card>

          {/* Detected Anomalies */}
          {recommendation.anomalies_detected.length > 0 && (
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Detected Anomalies</h3>
                <ul className="space-y-2">
                  {recommendation.anomalies_detected.map((anomaly, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <AlertCircle className="h-4 w-4 text-orange-600" />
                      <span className="text-gray-700">{anomaly}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </Card>
          )}
        </>
      ) : null}

      {/* Loading state for new generation */}
      {generateMutation.isPending && (
        <Card>
          <div className="p-12 text-center">
            <LoadingSpinner text="Generating AI recommendations..." />
            <p className="text-sm text-gray-600 mt-4">
              This may take a moment as we analyze your production data...
            </p>
          </div>
        </Card>
      )}
    </div>
  );
};