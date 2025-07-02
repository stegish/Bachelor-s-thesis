import React, { useState } from 'react';
import { Card } from '../common/Card';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ErrorMessage } from '../common/ErrorMessage';
import { RecommendationCard } from './RecommendationCard';
import { PriorityActionCard } from './PriorityActionCard';
import { useLatestRecommendation, useGenerateRecommendation, useRecommendationHistory } from '../../hooks/useAnalytics';
import { 
  Lightbulb, 
  RefreshCw, 
  Clock, 
  Target,
  TrendingUp,
  AlertTriangle,
  History
} from 'lucide-react';
import { formatRelativeTime, formatPercentage } from '../../utils';

export const RecommendationsView: React.FC = () => {
  const { data: latestRecommendation, isLoading, isError, refetch } = useLatestRecommendation();
  const generateRecommendation = useGenerateRecommendation();
  const { data: history } = useRecommendationHistory(7);
  const [showHistory, setShowHistory] = useState(false);

  const handleGenerateNew = async () => {
    //await generateRecommendation.mutateAsync();
  };

  if (isLoading) {
    return <LoadingSpinner text="Loading AI recommendations..." />;
  }

  if (isError && !latestRecommendation) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">AI Insights & Recommendations</h2>
            <p className="mt-1 text-sm text-gray-500">
              Intelligent analysis and optimization suggestions
            </p>
          </div>
        </div>
        
        <Card>
          <div className="text-center py-12">
            <Lightbulb className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No recommendations available yet</p>
            <button
              onClick={handleGenerateNew}
              disabled={generateRecommendation.isPending}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${generateRecommendation.isPending ? 'animate-spin' : ''}`} />
              {generateRecommendation.isPending ? 'Generating...' : 'Generate Analysis'}
            </button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">AI Insights & Recommendations</h2>
          <p className="mt-1 text-sm text-gray-500">
            Intelligent analysis and optimization suggestions
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <History className="h-4 w-4 mr-2" />
            History
          </button>
          
          <button
            onClick={handleGenerateNew}
            disabled={generateRecommendation.isPending}
            className="inline-flex items-center px-3 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${generateRecommendation.isPending ? 'animate-spin' : ''}`} />
            {generateRecommendation.isPending ? 'Generating...' : 'Generate New Analysis'}
          </button>
        </div>
      </div>

      {latestRecommendation && (
        <>
          {/* Metrics Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Machine Utilization</p>
                  <p className="text-2xl font-semibold mt-1">
                    {formatPercentage(latestRecommendation.metrics_analyzed.avg_machine_utilization || 0)}
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-primary-500" />
              </div>
            </Card>
            
            <Card className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">On-Time Delivery</p>
                  <p className="text-2xl font-semibold mt-1">
                    {formatPercentage(latestRecommendation.metrics_analyzed.on_time_delivery_rate || 0)}
                  </p>
                </div>
                <Target className="h-8 w-8 text-success-500" />
              </div>
            </Card>
            
            <Card className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Anomalies Detected</p>
                  <p className="text-2xl font-semibold mt-1">
                    {latestRecommendation.anomalies_detected.length}
                  </p>
                </div>
                <AlertTriangle className="h-8 w-8 text-warning-500" />
              </div>
            </Card>
            
            <Card className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Last Analysis</p>
                  <p className="text-lg font-medium mt-1">
                    {formatRelativeTime(latestRecommendation.timestamp)}
                  </p>
                </div>
                <Clock className="h-8 w-8 text-gray-400" />
              </div>
            </Card>
          </div>

          {/* Analysis Summary */}
          <Card title="Analysis Summary" subtitle={`Generated ${formatRelativeTime(latestRecommendation.timestamp)}`}>
            <div className="prose max-w-none">
              <p className="text-gray-700 whitespace-pre-wrap">{latestRecommendation.analysis}</p>
            </div>
          </Card>

          {/* Priority Actions */}
          {latestRecommendation.priority_actions.length > 0 && (
            <Card title="Priority Actions" subtitle="Immediate actions required">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {latestRecommendation.priority_actions.map((action) => (
                  <PriorityActionCard key={action.id} action={action} />
                ))}
              </div>
            </Card>
          )}

          {/* Recommendations */}
          <Card title="Recommendations" subtitle="AI-generated optimization suggestions">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {latestRecommendation.recommendations.map((rec) => (
                <RecommendationCard key={rec.id} recommendation={rec} />
              ))}
            </div>
          </Card>

          {/* Anomalies Detected */}
          {latestRecommendation.anomalies_detected.length > 0 && (
            <Card title="Anomalies Detected" subtitle="Issues identified during analysis">
              <ul className="space-y-2">
                {latestRecommendation.anomalies_detected.map((anomaly, index) => (
                  <li key={index} className="flex items-start">
                    <AlertTriangle className="h-5 w-5 text-warning-500 mt-0.5 mr-2 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{anomaly}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </>
      )}

      {/* History Modal/Drawer */}
      {showHistory && history && (
        <Card 
          title="Recommendation History" 
          subtitle="Past 7 days"
          headerAction={
            <button
              onClick={() => setShowHistory(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          }
        >
          <div className="space-y-3">
            {history.recommendations.map((rec: any) => (
              <div key={rec.analysis_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {formatRelativeTime(rec.timestamp)}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {rec.anomalies_count} anomalies • {rec.recommendations_count} recommendations
                  </p>
                </div>
                <button
                  onClick={() => window.location.href = `/recommendations/${rec.analysis_id}`}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  View →
                </button>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};