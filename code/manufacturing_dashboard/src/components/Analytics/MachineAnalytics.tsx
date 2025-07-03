import React, { useState } from 'react';
import { Card } from '../common/Card';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ErrorMessage } from '../common/ErrorMessage';
import { MachineDetailCard } from './MachineDetailCard';
import { useAnalyticsData } from '../../hooks/useAnalytics';
import { MachineMetrics } from '../../types';
import { Search, Filter } from 'lucide-react';

export const MachineAnalytics: React.FC = () => {
  const { data: analyticsData, isLoading, isError, refetch } = useAnalyticsData();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterActive, setFilterActive] = useState<boolean | null>(null);
  const [selectedMachine, setSelectedMachine] = useState<string | null>(null);

  if (isLoading) {
    return <LoadingSpinner text="Loading machine data..." />;
  }

  if (isError) {
    return (
      <ErrorMessage
        title="Failed to load machine analytics"
        message="Unable to retrieve machine data. Please try again."
        onRetry={refetch}
      />
    );
  }

  const machines: MachineMetrics[] = analyticsData?.machine_metrics?.data || [];

  // Filter machines based on search and active filter
  const filteredMachines = machines.filter(machine => {
    const matchesSearch = machine.machine_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterActive === null || machine.is_active === filterActive;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6">
      {/* Header and Filters */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">Machine Analytics</h2>
          <p className="mt-1 text-sm text-gray-500">
            Monitor performance and efficiency of production machines
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search machines..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          {/* Filter */}
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={filterActive === null ? 'all' : filterActive ? 'active' : 'inactive'}
              onChange={(e) => {
                const value = e.target.value;
                setFilterActive(value === 'all' ? null : value === 'active');
              }}
              className="border border-gray-300 rounded-md px-3 py-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">All Machines</option>
              <option value="active">Active Only</option>
              <option value="inactive">Inactive Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-gray-500">Total Machines</div>
          <div className="text-2xl font-semibold mt-1">{machines.length}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-500">Active Machines</div>
          <div className="text-2xl font-semibold mt-1 text-success-600">
            {machines.filter(m => m.is_active).length}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-500">Avg. Efficiency</div>
          <div className="text-2xl font-semibold mt-1">
            {(
              machines
                .filter(m => m.efficiency_percentage !== null)
                .reduce((sum, m) => sum + (m.efficiency_percentage || 0), 0) /
              machines.filter(m => m.efficiency_percentage !== null).length || 0
            ).toFixed(1)}%
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-500">Machines Below Target</div>
          <div className="text-2xl font-semibold mt-1 text-warning-600">
            {machines.filter(m => 
              m.efficiency_percentage !== null && m.efficiency_percentage < 70
            ).length}
          </div>
        </Card>
      </div>

      {/* Machine Grid */}
      {filteredMachines.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <p className="text-gray-500">No machines found matching your criteria</p>
          </div>
        </Card>
      ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredMachines.map((machine) => (
              <MachineDetailCard
                key={machine.machine_name}
                machine={machine}
                isExpanded={selectedMachine === machine.machine_name}
                onToggle={() => setSelectedMachine(
                  selectedMachine === machine.machine_name ? null : machine.machine_name
                )}
              />
            ))}
          </div>
      )}
    </div>
  );
};