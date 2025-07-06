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

// Mock hooks for the example
const useLatestRecommendation = () => ({
  data: null,
  isLoading: false,
  isError: false,
  error: null,
  refetch: () => {}
});

const useGenerateRecommendation = () => {
  const [isPending, setIsPending] = useState(false);
  
  return {
    mutate: (promptOrOptions) => {
      // Handle both string prompt or options object
      const prompt = typeof promptOrOptions === 'string' ? promptOrOptions : promptOrOptions?.prompt;
      const options = typeof promptOrOptions === 'object' ? promptOrOptions : {};
      
      console.log('Generating with prompt:', prompt);
      setIsPending(true);
      // Simulate async operation
      setTimeout(() => {
        setIsPending(false);
        if (options?.onSuccess) options.onSuccess();
      }, 1000);
    },
    isPending
  };
};

const useExecuteMcpAction = () => ({
  mutate: (action, options) => {
    console.log('Executing action:', action);
    options?.onSuccess?.({ message: 'Action executed successfully' });
  },
  isPending: false
});

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
    <div className={`fixed bottom-4 right-4 p-4 rounded-lg shadow-lg ${
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

  // Mock recommendation data for demo
  const mockRecommendation = {
    analysis_id: 'REC-001',
    timestamp: new Date(),
    metrics_analyzed: {
      avg_machine_utilization: 78.5,
      on_time_delivery_rate: 92.3,
      order_completion_rate: 88.7
    },
    anomalies_detected: [
      'Machine Filettatura-01 showing 40% higher defect rate than average',
      'Order ABC123 delayed by 48 hours due to material shortage'
    ],
    priority_actions: [
      {
        id: 'ACTION-001',
        description: 'Order ABC123 is blocking the production line and needs immediate priority adjustment',
        urgency: 'critical',
        estimated_impact: 'Will unblock 5 dependent orders and reduce delay by 24 hours',
        action: 'update_order_priority',
        parameters: { order_id: 'ABC123', priority: 1 }
      },
      {
        id: 'ACTION-002',
        description: 'Machine Filettatura-01 requires maintenance due to high defect rate',
        urgency: 'high',
        estimated_impact: 'Prevent further quality issues and reduce defect rate to normal levels',
        action: 'update_machine',
        parameters: { 
          machine_id: '678e38af83411cc4eac7bf51', 
          updates: { macchinarioActive: false, maintenanceRequired: true }
        }
      }
    ],
    recommendations: [
      {
        id: 'REC-001',
        description: 'Schedule preventive maintenance for all machines showing early warning signs',
        priority: 'medium',
        type: 'maintenance'
      }
    ]
  };

  const handleGenerateNew = (prompt?: string) => {
    generateMutation.mutate({
      prompt: prompt || '',
      onSuccess: () => {
        setToast({ message: 'New recommendations generated successfully', type: 'success' });
        setExecutedActions(new Set()); // Reset executed actions
      },
      onError: () => {
        setToast({ message: 'Failed to generate recommendations', type: 'error' });
      }
    });
    setCustomPrompt('');
    setShowCustomPrompt(false);
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
          // Refresh data after 2 seconds to show changes
          setTimeout(() => {
            refetch();
          }, 2000);
        },
        onError: (error) => {
          const errorMessage = error?.response?.data?.message || 
                             error?.message || 
                             'Failed to execute action';
          setToast({ message: errorMessage, type: 'error' });
        }
      }
    );
  };

  const displayRecommendation = mockRecommendation; // Use mock data for demo

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

        {/* Metrics Summary */}
        {displayRecommendation && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Machine Utilization</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {displayRecommendation.metrics_analyzed.avg_machine_utilization?.toFixed(1)}%
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
                    {displayRecommendation.metrics_analyzed.on_time_delivery_rate?.toFixed(1)}%
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
                    {displayRecommendation.anomalies_detected.length}
                  </p>
                </div>
                <AlertTriangle className="h-8 w-8 text-red-600" />
              </div>
            </Card>
          </div>
        )}

        {/* Priority Actions */}
        {displayRecommendation?.priority_actions.length > 0 && (
          <Card>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Database className="h-5 w-5 text-blue-600" />
                  Executable Database Actions ({displayRecommendation.priority_actions.length})
                </h3>
                <span className="text-sm text-gray-500">
                  Click to review and execute
                </span>
              </div>
              
              <div className="space-y-3">
                {displayRecommendation.priority_actions.map((action) => {
                  const isExecuted = executedActions.has(action.id);
                  
                  return (
                    <div
                      key={action.id}
                      className={`border rounded-lg p-4 cursor-pointer transition-all ${
                        isExecuted 
                          ? 'bg-green-50 border-green-300' 
                          : 'hover:border-blue-400 hover:shadow-md'
                      }`}
                      onClick={() => !isExecuted && setSelectedAction(action)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              action.urgency === 'critical' 
                                ? 'bg-red-100 text-red-700' 
                                : 'bg-yellow-100 text-yellow-700'
                            }`}>
                              {action.urgency.toUpperCase()}
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
                          <p className="text-gray-800">{action.description}</p>
                          {action.estimated_impact && (
                            <p className="text-sm text-gray-600 mt-1">
                              Impact: {action.estimated_impact}
                            </p>
                          )}
                        </div>
                        {!isExecuted && (
                          <ChevronRight className="h-5 w-5 text-gray-400 mt-1" />
                        )}
                      </div>
                    </div>
                  );
                })}
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