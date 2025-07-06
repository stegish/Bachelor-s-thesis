import React, { useState, useEffect } from 'react';
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
  Send,
  Database,
  Activity,
  ChevronRight,
  XCircle
} from 'lucide-react';

// Import the hooks from your actual implementation
import { 
  useLatestRecommendation, 
  useGenerateRecommendation, 
  useExecuteMcpAction 
} from '../../hooks/useAnalytics';

// Type definitions
interface AxiosError extends Error {
  response?: {
    data?: {
      detail?: {
        message?: string;
      };
      message?: string;
    };
    status?: number;
  };
}

// Type guard for axios error
const isAxiosError = (error: any): error is AxiosError => {
  return error?.response !== undefined;
};

// Components
const Card = ({ children, className = '' }) => (
  <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
    {children}
  </div>
);

const Button = ({ children = null, variant = 'primary', onClick, loading = false, icon: Icon = null, disabled = false, className = '' }) => {
  const hasOnlyIcon = Icon && !children && !loading;
  const baseClasses = `${hasOnlyIcon ? 'p-2' : 'px-4 py-2'} rounded-md font-medium transition-colors flex items-center gap-2`;
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-300',
    outline: 'border border-gray-300 text-gray-700 hover:bg-gray-50',
    ghost: 'text-gray-600 hover:bg-gray-100'
  };
  
  return (
    <button 
      className={`${baseClasses} ${variants[variant]} ${className}`}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {Icon && <Icon className="h-4 w-4" />}
      {loading ? 'Loading...' : children}
    </button>
  );
};

const Toast = ({ message, type, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 5000);
    return () => clearTimeout(timer);
  }, [onClose]);
  
  return (
    <div className={`fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
      type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
    }`}>
      <div className="flex items-center gap-2">
        {type === 'success' ? <CheckCircle className="h-5 w-5" /> : <AlertCircle className="h-5 w-5" />}
        {message}
      </div>
    </div>
  );
};

const ActionConfirmationModal = ({ action, onConfirm, onClose, loading = false }) => {
  const [showChanges, setShowChanges] = useState(false);
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Database className="h-5 w-5 text-blue-600" />
            Confirm Database Modification
          </h2>
          <Button variant="ghost" onClick={onClose} icon={XCircle} />
        </div>
        
        <div className="space-y-4">
          {/* Action Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Activity className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="flex-1">
                <p className="font-medium text-blue-900">Proposed Action</p>
                <p className="text-blue-800 mt-1">{action.description}</p>
              </div>
            </div>
          </div>
          
          {/* Technical Details */}
          <div className="space-y-3">
            <div>
              <p className="text-sm font-medium text-gray-600">Action Type</p>
              <code className="bg-gray-100 px-2 py-1 rounded text-sm">{action.action}</code>
            </div>
            
            {action.parameters && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-gray-600">Parameters</p>
                  <button
                    className="text-xs text-blue-600 hover:text-blue-700"
                    onClick={() => setShowChanges(!showChanges)}
                  >
                    {showChanges ? 'Hide' : 'Show'} Details
                  </button>
                </div>
                {showChanges && (
                  <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
{JSON.stringify(action.parameters, null, 2)}
                  </pre>
                )}
              </div>
            )}
          </div>
          
          {/* Expected Impact */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div className="flex-1">
                <p className="font-medium text-yellow-900">Expected Impact</p>
                <p className="text-yellow-800 text-sm mt-1">
                  {action.estimated_impact || 'This change will be applied immediately to the production database.'}
                </p>
              </div>
            </div>
          </div>
          
          {/* Warning */}
          <div className="text-sm text-gray-600 italic">
            ⚠️ This action will modify the production database. Changes will take effect immediately.
          </div>
          
          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            <Button 
              variant="primary" 
              className="flex-1" 
              onClick={onConfirm} 
              loading={loading}
              icon={CheckCircle}
            >
              Execute Action
            </Button>
            <Button 
              variant="outline" 
              onClick={onClose}
              disabled={loading}
              icon={null}
            >
              Cancel
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

// Main Component
export const RecommendationsView = () => {
  const [customPrompt, setCustomPrompt] = useState('');
  const [showCustomPrompt, setShowCustomPrompt] = useState(false);
  const [selectedAction, setSelectedAction] = useState(null);
  const [toast, setToast] = useState(null);
  const [executedActions, setExecutedActions] = useState(new Set());

  const { data: recommendation, isLoading, isError, error, refetch } = useLatestRecommendation();
  const generateMutation = useGenerateRecommendation();
  const executeMutation = useExecuteMcpAction();

  // Detect if the analysis is for a specific action
  // Check if this is a specific action by looking at the prompt or analysis content
  const isSpecificAction = (() => {
    if (!recommendation) return false;
    
    // Check if the analysis mentions specific order modifications
    const analysisText = recommendation.analysis?.toLowerCase() || '';
    const promptText = (recommendation as any)?.prompt_used?.toLowerCase() || '';
    
    // Keywords that indicate a specific action request
    const actionKeywords = ['modifica', 'cambia', 'aggiorna', 'update', 'change', 'modify', 'priorità', 'priority'];
    const hasActionKeywords = actionKeywords.some(keyword => 
      analysisText.includes(keyword) || promptText.includes(keyword)
    );
    
    // Check if there's only one priority action (typical for specific requests)
    const hasSingleAction = recommendation.priority_actions?.length === 1;
    
    // Check if recommendations and anomalies are empty (typical for specific actions)
    const noGeneralAnalysis = (!recommendation.recommendations || recommendation.recommendations.length === 0) && 
                             (!recommendation.anomalies_detected || recommendation.anomalies_detected.length === 0);
    
    return hasActionKeywords && (hasSingleAction || noGeneralAnalysis);
  })();

  const handleGenerateNew = (prompt?: string) => {
    const finalPrompt = prompt || customPrompt || undefined;
    
    generateMutation.mutate(finalPrompt, {
      onSuccess: () => {
        setToast({ message: 'New recommendations generated successfully', type: 'success' });
        setExecutedActions(new Set());
        setCustomPrompt('');
        setShowCustomPrompt(false);
      },
      onError: (error: unknown) => {
        // Type safe error handling
        const errorMessage = error instanceof Error ? error.message : 'Failed to generate recommendations';
        setToast({ 
          message: errorMessage, 
          type: 'error' 
        });
      }
    });
  };

  const handleActionClick = (action) => {
    // Validazione base prima di mostrare il modal
    if (!action.parameters?.order_id && !action.parameters?.machine_id) {
      setToast({
        message: 'Invalid action: missing target ID',
        type: 'error'
      });
      return;
    }
    setSelectedAction(action);
  };

  const handleConfirmAction = () => {
    if (!selectedAction) return;
    
    executeMutation.mutate(
      { action: selectedAction.action, parameters: selectedAction.parameters || {} },
      {
        onSuccess: (data) => {
          const message = data?.message || `Successfully executed: ${selectedAction.description}`;
          setToast({ message, type: 'success' });
          setExecutedActions(prev => new Set(prev).add(selectedAction.id));
          setSelectedAction(null);
          setTimeout(() => {
            refetch();
          }, 2000);
        },
        onError: (error: unknown) => {
          // Type safe error handling with axios error check
          let errorMessage = 'Failed to execute action';
          
          if (isAxiosError(error)) {
            errorMessage = error.response?.data?.detail?.message || 
                          error.response?.data?.message || 
                          error.message;
          } else if (error instanceof Error) {
            errorMessage = error.message;
          }
          
          // Gestione specifica per ordini non trovati
          if (errorMessage.includes('not found')) {
            setToast({ 
              message: 'The referenced order/machine no longer exists. Please refresh the analysis.', 
              type: 'error' 
            });
            // Auto-refresh dopo 3 secondi
            setTimeout(() => {
              handleGenerateNew();
            }, 3000);
          } else {
            setToast({ message: errorMessage, type: 'error' });
          }
        }
      }
    );
  };

  // Get error message safely
  const getErrorMessage = (error: unknown): string => {
    if (error instanceof Error) {
      return error.message;
    }
    return 'An unknown error occurred';
  };

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

        {/* Custom Prompt Form */}
        {showCustomPrompt && (
          <Card>
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-purple-600" />
                <h3 className="text-lg font-semibold text-gray-900">Custom Analysis Prompt</h3>
              </div>
              
              <div className="space-y-3">
                <p className="text-sm text-gray-600">
                  Provide specific instructions for the AI analysis. You can ask about particular orders, 
                  machines, or request focused insights on specific aspects of production.
                </p>
                
                <textarea
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  placeholder="Example: Analyze the bottlenecks in the Filettatura phase and suggest optimizations for orders with high priority..."
                  className="w-full min-h-[120px] p-3 border border-gray-300 rounded-lg 
                            focus:ring-2 focus:ring-purple-500 focus:border-transparent
                            resize-y text-sm"
                />
                
                <div className="flex gap-2 justify-end">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setCustomPrompt('');
                      setShowCustomPrompt(false);
                    }}
                    disabled={generateMutation.isPending}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    onClick={() => handleGenerateNew(customPrompt)}
                    loading={generateMutation.isPending}
                    disabled={!customPrompt.trim()}
                    icon={Send}
                  >
                    Generate Analysis
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Loading State */}
        {isLoading && (
          <Card>
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="h-8 w-8 text-gray-400 animate-spin" />
              <span className="ml-2 text-gray-600">Loading recommendations...</span>
            </div>
          </Card>
        )}

        {/* Error State */}
        {isError && (
          <Card>
            <div className="flex items-center gap-3 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <p>Failed to load recommendations: {getErrorMessage(error)}</p>
            </div>
          </Card>
        )}

        {/* LLM Analysis Response - for specific actions */}
        {recommendation && isSpecificAction && (
          <Card>
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-purple-600" />
                AI Response
              </h3>
              <div className="prose prose-sm max-w-none">
                <div className="whitespace-pre-wrap text-gray-700 text-sm bg-gray-50 p-4 rounded-lg">
                  {recommendation.analysis}
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Metrics Summary - Only show for general analysis */}
        {recommendation && !isLoading && !isSpecificAction && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Machine Utilization</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {recommendation.metrics_analyzed?.avg_machine_utilization?.toFixed(1) || '75.0'}%
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
                    {recommendation.metrics_analyzed?.on_time_delivery_rate?.toFixed(1) || '90.0'}%
                  </p>
                </div>
                <Clock className="h-8 w-8 text-green-600" />
              </div>
            </Card>
            
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Anomalies Detected</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {recommendation.anomalies_detected?.length || 0}
                  </p>
                </div>
                <AlertTriangle className="h-8 w-8 text-red-600" />
              </div>
            </Card>
          </div>
        )}

        {/* No Data State */}
        {!recommendation && !isLoading && !isError && (
          <Card>
            <div className="text-center py-8">
              <Sparkles className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Recommendations Available</h3>
              <p className="text-gray-600 mb-4">Generate your first AI-powered analysis to get started.</p>
              <Button
                variant="primary"
                onClick={() => handleGenerateNew()}
                loading={generateMutation.isPending}
                icon={RefreshCw}
              >
                Generate Analysis
              </Button>
            </div>
          </Card>
        )}

        {/* Anomalies Section - Only show for general analysis */}
        {recommendation?.anomalies_detected?.length > 0 && !isSpecificAction && (
          <Card>
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-600" />
                Detected Anomalies
              </h3>
              <ul className="space-y-2">
                {recommendation.anomalies_detected.map((anomaly, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-orange-500 mt-0.5">•</span>
                    <span className="text-gray-700">{anomaly}</span>
                  </li>
                ))}
              </ul>
            </div>
          </Card>
        )}

        {/* Priority Actions */}
        {recommendation?.priority_actions?.length > 0 && (
          <Card>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Database className="h-5 w-5 text-blue-600" />
                  Executable Database Actions ({recommendation.priority_actions.length})
                </h3>
                <span className="text-sm text-gray-500">
                  Click to review and execute
                </span>
              </div>
              
              <div className="space-y-3">
                {recommendation.priority_actions.map((action) => {
                  const isExecuted = executedActions.has(action.id);
                  
                  return (
                    <div
                      key={action.id}
                      className={`border rounded-lg p-4 cursor-pointer transition-all ${
                        isExecuted 
                          ? 'bg-green-50 border-green-300 cursor-default' 
                          : 'hover:border-blue-400 hover:shadow-md border-gray-200'
                      }`}
                      onClick={() => !isExecuted && handleActionClick(action)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              action.urgency === 'critical' 
                                ? 'bg-red-100 text-red-700' 
                                : action.urgency === 'high' 
                                ? 'bg-orange-100 text-orange-700'
                                : 'bg-yellow-100 text-yellow-700'
                            }`}>
                              {action.urgency?.toUpperCase() || 'MEDIUM'}
                            </span>
                            <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                              {action.action}
                            </code>
                            {isExecuted && (
                              <span className="text-xs text-green-600 flex items-center gap-1">
                                <CheckCircle className="h-3 w-3" />
                                Executed
                              </span>
                            )}
                          </div>
                          <p className="text-gray-800 font-medium">{action.description}</p>
                          {action.estimated_impact && (
                            <p className="text-sm text-gray-600 mt-1">
                              <span className="font-medium">Impact:</span> {action.estimated_impact}
                            </p>
                          )}
                          {/* Mostra l'ID target per trasparenza */}
                          <div className="mt-2 flex items-center gap-2">
                            <span className="text-xs text-gray-500">Target:</span>
                            <code className="text-xs text-gray-700 font-mono bg-gray-100 px-2 py-0.5 rounded">
                              {action.parameters?.order_id || action.parameters?.machine_id || 'N/A'}
                            </code>
                          </div>
                        </div>
                        {!isExecuted && (
                          <ChevronRight className="h-5 w-5 text-gray-400 mt-1 flex-shrink-0" />
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </Card>
        )}

        {/* Recommendations - Only show for general analysis */}
        {recommendation?.recommendations?.length > 0 && !isSpecificAction && (
          <Card>
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Wrench className="h-5 w-5 text-gray-600" />
                General Recommendations
              </h3>
              <div className="space-y-3">
                {recommendation.recommendations.map((rec, index) => (
                  <div key={rec.id || index} className="border-l-4 border-gray-300 pl-4">
                    <p className="text-gray-800">{rec.description}</p>
                    <span className={`text-xs mt-1 inline-block px-2 py-1 rounded ${
                      rec.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                      rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {rec.priority || 'medium'} priority
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        )}
      </div>
      
      {/* Modals and Toasts */}
      {selectedAction && (
        <ActionConfirmationModal
          action={selectedAction}
          onConfirm={handleConfirmAction}
          onClose={() => setSelectedAction(null)}
          loading={executeMutation.isPending}
        />
      )}
      
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