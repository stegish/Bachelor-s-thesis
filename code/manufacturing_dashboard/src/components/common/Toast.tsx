import React, { useEffect } from 'react';
import { CheckCircle, XCircle, X } from 'lucide-react';

interface ToastProps {
  message: string;
  type: 'success' | 'error';
  onClose: () => void;
  duration?: number;
}

export const Toast: React.FC<ToastProps> = ({ 
  message, 
  type, 
  onClose, 
  duration = 5000 
}) => {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const bgColor = type === 'success' ? 'bg-green-50' : 'bg-red-50';
  const borderColor = type === 'success' ? 'border-green-200' : 'border-red-200';
  const textColor = type === 'success' ? 'text-green-800' : 'text-red-800';
  const Icon = type === 'success' ? CheckCircle : XCircle;
  const iconColor = type === 'success' ? 'text-green-600' : 'text-red-600';

  return (
    <div 
      className={`fixed top-4 right-4 z-50 animate-fade-in ${bgColor} ${borderColor} border rounded-lg shadow-lg p-4 max-w-md flex items-start gap-3`}
    >
      <Icon className={`h-5 w-5 ${iconColor} mt-0.5`} />
      <p className={`flex-1 text-sm ${textColor}`}>{message}</p>
      <button
        onClick={onClose}
        className={`${textColor} hover:opacity-70`}
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
};