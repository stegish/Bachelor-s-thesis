import React from 'react';

interface CardProps {
  title?: string;
  subtitle?: string;
  headerAction?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  footer?: React.ReactNode;
  noPadding?: boolean;
}

export const Card: React.FC<CardProps> = ({ 
  title, 
  subtitle,
  children, 
  className = '',
  onClick,
  footer,
  noPadding = false
}) => {
  return (
    <div 
      className={`bg-white rounded-lg shadow hover:shadow-md transition-shadow ${onClick ? 'cursor-pointer' : ''} ${className}`}
      onClick={onClick}
    >
      {/* Header */}
      {(title || subtitle) && (
        <div className={`${noPadding ? 'px-6 pt-6' : 'p-6 pb-4'} border-b border-gray-100`}>
          {title && (
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          )}
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
      )}
      
      {/* Content */}
      <div className={noPadding ? '' : 'p-6'}>
        {children}
      </div>
      
      {/* Footer */}
      {footer && (
        <div className="border-t border-gray-100 px-6 py-4 bg-gray-50 rounded-b-lg">
          {footer}
        </div>
      )}
    </div>
  );
};