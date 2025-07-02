import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { OverviewDashboard } from './components/Dashboard/OverviewDashboard';
import { MachineAnalytics } from './components/Analytics/MachineAnalytics';
import { AnomaliesView } from './components/Anomalies/AnomaliesView';
import { RecommendationsView } from './components/Recommendations/RecommendationsView';
import { useAnomalies } from './hooks/useAnalytics';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function AppContent() {
  const [activeView, setActiveView] = useState('overview');
  const { data: anomalies = [] } = useAnomalies();

  const renderContent = () => {
    switch (activeView) {
      case 'overview':
        return <OverviewDashboard />;
      case 'analytics':
        return <MachineAnalytics />;
      case 'anomalies':
        return <AnomaliesView />;
      case 'recommendations':
        return <RecommendationsView />;
      default:
        return (
          <div className="text-center py-12">
            <p className="text-gray-500">View not implemented yet: {activeView}</p>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex h-[calc(100vh-4rem)]">
        <Sidebar 
          activeView={activeView} 
          onViewChange={setActiveView}
          anomalyCount={anomalies.length}
        />
        <main className="flex-1 overflow-y-auto">
          <div className="p-6">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;