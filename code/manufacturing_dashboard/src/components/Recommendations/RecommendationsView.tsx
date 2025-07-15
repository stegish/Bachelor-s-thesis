// File: /code/manufacturing_dashboard/src/components/Recommendations/RecommendationsView.tsx
// Versione corretta con tutti i tipi allineati

import React, { useState } from 'react';
import { 
  Sparkles, 
  RefreshCw, 
  MessageSquare, 
  TrendingUp,
  Clock,
  AlertTriangle,
  CheckCircle,
  Users,
  Zap,
  Target,
  ChevronDown,
  ChevronUp,
  Info
} from 'lucide-react';  // Rimosso AlertCircle
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ErrorMessage } from '../common/ErrorMessage';
import { Toast } from '../common/Toast';
import { 
  useRecommendationsWithOperators, 
  useGenerateRecommendation 
} from '../../hooks/useAnalytics';
import { formatDate } from '../../utils';

// Type guard per error
const getErrorMessage = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'An unknown error occurred';
};

// Markdown-like text processor
const formatMarkdownText = (text: string): string => {
  if (!text) return '';
  
  // Process line by line
  let formatted = text
    .split('\n')
    .map(line => {
      // H2 headers
      if (line.startsWith('## ')) {
        return `<h2 class="text-xl font-semibold mb-3 text-gray-800 mt-6">${line.substring(3)}</h2>`;
      }
      // H3 headers
      if (line.startsWith('### ')) {
        return `<h3 class="text-lg font-medium mb-2 text-gray-700 mt-4">${line.substring(4)}</h3>`;
      }
      // Bold text
      line = line.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>');
      
      // Lists
      if (line.startsWith('- ')) {
        return `<li class="text-gray-600 ml-4 mb-1">• ${line.substring(2)}</li>`;
      }
      if (line.match(/^\d+\. /)) {
        const content = line.substring(line.indexOf('. ') + 2);
        const number = line.substring(0, line.indexOf('.'));
        return `<li class="text-gray-600 ml-4 mb-1"><span class="font-medium">${number}.</span> ${content}</li>`;
      }
      
      // Regular paragraphs
      if (line.trim() && !line.startsWith('<')) {
        return `<p class="mb-3 text-gray-600 leading-relaxed">${line}</p>`;
      }
      return line;
    })
    .join('\n');

  // Wrap consecutive list items
  formatted = formatted.replace(/(<li.*?<\/li>\n?)+/g, (match) => {
    const isNumbered = match.includes('<span class="font-medium">');
    const listType = isNumbered ? 'ol' : 'ul';
    const listClass = isNumbered ? 'list-decimal' : 'list-none';
    return `<${listType} class="mb-4 space-y-1 ${listClass}">${match}</${listType}>`;
  });
  
  return formatted;
};

// Type-safe priority color mapping
type BadgeVariant = "default" | "success" | "info" | "warning" | "danger" | "primary" | "low" | "medium" | "high" | "critical";

const getPriorityColor = (priority: string): BadgeVariant => {
  const colors: Record<string, BadgeVariant> = {
    low: 'info',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  };
  return colors[priority] || 'default';
};

export const RecommendationsView: React.FC = () => {
  const { 
    recommendation, 
    operators, 
    isLoading, 
    isError, 
    error, 
    refetch 
  } = useRecommendationsWithOperators();
  
  const generateMutation = useGenerateRecommendation();
  
  const [showCustomPrompt, setShowCustomPrompt] = useState(false);
  const [customPrompt, setCustomPrompt] = useState('');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [expandedSections, setExpandedSections] = useState({
    analysis: true,
    metrics: true,
    operators: false,
    recommendations: true,
    actions: true
  });

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleGenerateNew = async (prompt?: string) => {
    try {
      await generateMutation.mutateAsync(prompt || customPrompt || undefined);
      setToast({ 
        message: 'New recommendation generated successfully!', 
        type: 'success' 
      });
      setShowCustomPrompt(false);
      setCustomPrompt('');
    } catch (error) {
      setToast({ 
        message: 'Failed to generate recommendation. Please try again.', 
        type: 'error' 
      });
    }
  };

  const getTypeIcon = (type: string) => {
    const icons: Record<string, any> = {
      optimization: Target,
      improvement: TrendingUp,
      maintenance: Zap,
      alert: AlertTriangle
    };
    return icons[type] || Info;
  };

  const executeAction = async (action: any) => {
    try {
      // Here you would call the MCP server to execute the action
      console.log('Executing action:', action);
      setToast({ 
        message: `Action "${action.description}" queued for execution.`, 
        type: 'success'  // Changed from 'info' to 'success'
      });
    } catch (error) {
      setToast({ 
        message: 'Failed to execute action.', 
        type: 'error' 
      });
    }
  };

  if (isLoading) {
    return <LoadingSpinner text="Loading AI insights..." />;
  }

  if (isError) {
    return (
      <ErrorMessage 
        title="Failed to load recommendations"
        message={getErrorMessage(error)}
        onRetry={refetch}
      />
    );
  }

  return (
    <>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="h-8 w-8 text-purple-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AI Insights & Recommendations</h1>
              <p className="text-gray-600">AI-powered analysis with executable database modifications</p>
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

        {/* Custom Prompt */}
        {showCustomPrompt && (
          <Card>
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-purple-600" />
                <h3 className="text-lg font-semibold text-gray-900">Custom Analysis Prompt</h3>
              </div>
              <p className="text-sm text-gray-600">
                Provide specific instructions for the AI analysis. You can ask about particular orders, 
                machines, or request focused insights on specific aspects of production.
              </p>
              <textarea
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="Example: Analyze the efficiency of machine M-ASSEMBLY-01 and suggest improvements..."
                className="w-full h-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
              <div className="flex gap-2">
                <Button 
                  variant="primary" 
                  onClick={() => handleGenerateNew(customPrompt)}
                  disabled={!customPrompt.trim()}
                  loading={generateMutation.isPending}
                >
                  Analyze
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setShowCustomPrompt(false);
                    setCustomPrompt('');
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </Card>
        )}

        {recommendation && (
          <>
            {/* Metrics Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Machine Utilization</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {recommendation.metrics_analyzed?.avg_machine_utilization?.toFixed(1) || '0'}%
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-blue-600" />
                </div>
              </Card>
              
              <Card>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">On-Time Delivery</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {recommendation.metrics_analyzed?.on_time_delivery_rate?.toFixed(1) || '0'}%
                    </p>
                  </div>
                  <Clock className="h-8 w-8 text-green-600" />
                </div>
              </Card>

              <Card>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Active Operators</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {operators.length || 0}
                    </p>
                  </div>
                  <Users className="h-8 w-8 text-purple-600" />
                </div>
              </Card>

              <Card>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Anomalies</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {recommendation.anomalies_detected?.length || 0}
                    </p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-red-600" />
                </div>
              </Card>
            </div>

            {/* AI Analysis */}
            <Card>
              <div 
                className="flex items-center justify-between cursor-pointer mb-4"
                onClick={() => toggleSection('analysis')}
              >
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-purple-600" />
                  AI Analysis
                </h3>
                {expandedSections.analysis ? <ChevronUp /> : <ChevronDown />}
              </div>
              
              {expandedSections.analysis && (
                <div className="prose prose-sm max-w-none">
                  <div dangerouslySetInnerHTML={{ __html: formatMarkdownText(recommendation.analysis) }} />
                </div>
              )}
            </Card>

            {/* Operator Performance */}
            {operators.length > 0 && (
              <Card>
                <div 
                  className="flex items-center justify-between cursor-pointer mb-4"
                  onClick={() => toggleSection('operators')}
                >
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <Users className="h-5 w-5 text-purple-600" />
                    Operator Performance
                  </h3>
                  {expandedSections.operators ? <ChevronUp /> : <ChevronDown />}
                </div>
                
                {expandedSections.operators && (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Operator
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Phases Completed
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Avg Cycle Time
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Efficiency
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Total Quantity
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {operators.slice(0, 10).map((operator, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {operator.operator}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {operator.total_phases}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {operator.avg_cycle_time?.toFixed(1) || '0'} min
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center">
                                <span className="text-sm text-gray-900">
                                  {operator.efficiency?.toFixed(1) || '0'}%
                                </span>
                                {operator.efficiency && operator.efficiency > 90 && (
                                  <CheckCircle className="ml-2 h-4 w-4 text-green-500" />
                                )}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {operator.total_quantity?.toLocaleString() || '0'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {operators.length > 10 && (
                      <p className="text-sm text-gray-500 mt-2 text-center">
                        Showing top 10 of {operators.length} operators
                      </p>
                    )}
                  </div>
                )}
              </Card>
            )}

            {/* Recommendations */}
            {recommendation.recommendations?.length > 0 && (
              <Card>
                <div 
                  className="flex items-center justify-between cursor-pointer mb-4"
                  onClick={() => toggleSection('recommendations')}
                >
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <Target className="h-5 w-5 text-purple-600" />
                    Recommendations ({recommendation.recommendations.length})
                  </h3>
                  {expandedSections.recommendations ? <ChevronUp /> : <ChevronDown />}
                </div>
                
                {expandedSections.recommendations && (
                  <div className="space-y-3">
                    {recommendation.recommendations.map((rec) => {
                      const Icon = getTypeIcon(rec.type);
                      return (
                        <div key={rec.id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                          <Icon className="h-5 w-5 text-purple-600 mt-0.5 flex-shrink-0" />
                          <div className="flex-1">
                            <p className="text-sm text-gray-900">{rec.description}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge variant={getPriorityColor(rec.priority)}>
                                {rec.priority}
                              </Badge>
                              <span className="text-xs text-gray-500">{rec.type}</span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </Card>
            )}

            {/* Priority Actions */}
            {recommendation.priority_actions?.length > 0 && (
              <Card>
                <div 
                  className="flex items-center justify-between cursor-pointer mb-4"
                  onClick={() => toggleSection('actions')}
                >
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <Zap className="h-5 w-5 text-yellow-600" />
                    Priority Actions ({recommendation.priority_actions.length})
                  </h3>
                  {expandedSections.actions ? <ChevronUp /> : <ChevronDown />}
                </div>
                
                {expandedSections.actions && (
                  <div className="space-y-3">
                    {recommendation.priority_actions.map((action) => (
                      <div key={action.id} className="border border-yellow-200 bg-yellow-50 rounded-lg p-4">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{action.description}</p>
                            <p className="text-sm text-gray-600 mt-1">{action.estimated_impact}</p>
                            <div className="flex items-center gap-2 mt-2">
                              <Badge variant="danger">{action.urgency}</Badge>
                              {action.action && (
                                <code className="text-xs bg-gray-100 px-2 py-1 rounded font-mono">
                                  {action.action}
                                </code>
                              )}
                            </div>
                          </div>
                          <Button 
                            variant="primary"  // Changed from 'success' to 'primary'
                            onClick={() => executeAction(action)}
                            size="sm"
                          >
                            Execute
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            )}

            {/* Processing Info */}
            <div className="text-center text-sm text-gray-500">
              Analysis generated in {recommendation.processing_time?.toFixed(1) || '0'}s • 
              Last updated: {formatDate(recommendation.timestamp)}
            </div>
          </>
        )}

        {!recommendation && !isLoading && (
          <Card>
            <div className="text-center py-12">
              <Sparkles className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No recommendations yet</h3>
              <p className="text-gray-600 mb-6">
                Generate your first AI-powered analysis to get started
              </p>
              <Button 
                variant="primary" 
                onClick={() => handleGenerateNew()}
                icon={RefreshCw}
              >
                Generate Analysis
              </Button>
            </div>
          </Card>
        )}
      </div>

      {/* Toast notifications */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </>
  );
};