import React, { useState } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { XCircle } from 'lucide-react';

interface McpActionModalProps {
  description: string;
  onClose: () => void;
  onExecute: (action: string, params: Record<string, any>) => void;
  loading?: boolean;
}

export const McpActionModal: React.FC<McpActionModalProps> = ({
  description,
  onClose,
  onExecute,
  loading = false,
}) => {
  const [action, setAction] = useState('');
  const [paramsText, setParamsText] = useState('{}');
  const [error, setError] = useState<string | null>(null);

  const handleExecute = () => {
    try {
      const params = paramsText ? JSON.parse(paramsText) : {};
      setError(null);
      onExecute(action, params);
    } catch (e) {
      setError('Invalid JSON parameters');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="max-w-lg w-full">
        <div className="p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Execute MCP Action</h2>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <XCircle className="h-5 w-5" />
            </Button>
          </div>
          <p className="text-sm text-gray-600">{description}</p>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Action</label>
            <input
              className="w-full border rounded-md p-2 text-sm"
              value={action}
              onChange={(e) => setAction(e.target.value)}
              placeholder="schedule_order"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Parameters (JSON)</label>
            <textarea
              className="w-full border rounded-md p-2 text-sm"
              rows={4}
              value={paramsText}
              onChange={(e) => setParamsText(e.target.value)}
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button variant="primary" className="w-full" onClick={handleExecute} loading={loading}>
            Execute
          </Button>
        </div>
      </Card>
    </div>
  );
};
