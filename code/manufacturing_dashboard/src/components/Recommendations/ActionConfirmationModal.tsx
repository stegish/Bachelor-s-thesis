import React from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { XCircle } from 'lucide-react';

interface Action {
  id: string;
  description: string;
  action: string;
  parameters?: Record<string, any>;
}

interface Props {
  action: Action;
  onConfirm: () => void;
  onClose: () => void;
  loading?: boolean;
}

export const ActionConfirmationModal: React.FC<Props> = ({
  action,
  onConfirm,
  onClose,
  loading = false,
}) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="max-w-lg w-full">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Confirm Action</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <XCircle className="h-5 w-5" />
          </Button>
        </div>
        <div className="space-y-4">
          <p className="text-gray-700 whitespace-pre-wrap">{action.description}</p>
          <div>
            <p className="text-sm text-gray-500">Command</p>
            <p className="font-mono text-sm break-words">{action.action}</p>
          </div>
          {action.parameters && (
            <div>
              <p className="text-sm text-gray-500 mb-1">Parameters</p>
              <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto">
{JSON.stringify(action.parameters, null, 2)}
</pre>
            </div>
          )}
          <Button variant="primary" className="w-full" onClick={onConfirm} loading={loading}>
            Execute
          </Button>
        </div>
      </Card>
    </div>
  );
};
