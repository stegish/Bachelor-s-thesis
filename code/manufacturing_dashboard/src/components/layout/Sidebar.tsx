import React from 'react';
import { 
  LayoutDashboard, 
  BarChart3, 
  AlertTriangle, 
  Lightbulb,
  FileText,
  Settings,
  HelpCircle
} from 'lucide-react';

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
}

interface SidebarProps {
  activeView: string;
  onViewChange: (view: string) => void;
  anomalyCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  activeView, 
  onViewChange,
  anomalyCount = 0 
}) => {
  const navItems: NavItem[] = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'analytics', label: 'Machine Analytics', icon: BarChart3 },
    { id: 'anomalies', label: 'Anomalies', icon: AlertTriangle, badge: anomalyCount },
    { id: 'recommendations', label: 'AI Insights', icon: Lightbulb },
  ];

  const bottomNavItems: NavItem[] = [
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'help', label: 'Help', icon: HelpCircle },
  ];

  const renderNavItem = (item: NavItem) => {
    const isActive = activeView === item.id;
    const Icon = item.icon;

    return (
      <button
        key={item.id}
        onClick={() => onViewChange(item.id)}
        className={`
          w-full flex items-center justify-between px-3 py-2 rounded-md text-sm font-medium transition-colors
          ${isActive 
            ? 'bg-primary-100 text-primary-700' 
            : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
          }
        `}
      >
        <div className="flex items-center">
          <Icon className={`mr-3 h-5 w-5 ${isActive ? 'text-primary-600' : 'text-gray-400'}`} />
          <span>{item.label}</span>
        </div>
        {item.badge && item.badge > 0 && (
          <span className={`
            ml-2 px-2 py-0.5 text-xs rounded-full
            ${isActive 
              ? 'bg-primary-200 text-primary-800' 
              : 'bg-danger-100 text-danger-700'
            }
          `}>
            {item.badge}
          </span>
        )}
      </button>
    );
  };

  return (
    <aside className="w-64 bg-white shadow-sm h-full">
      <nav className="h-full flex flex-col">
        {/* Main Navigation */}
        <div className="flex-1 px-4 py-4">
          <div className="space-y-1">
            {navItems.map(renderNavItem)}
          </div>
        </div>

        {/* Bottom Navigation */}
        <div className="border-t border-gray-200 px-4 py-4">
          <div className="space-y-1">
            {bottomNavItems.map(renderNavItem)}
          </div>
        </div>
      </nav>
    </aside>
  );
};