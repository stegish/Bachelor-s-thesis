from typing import List, Dict, Any, Optional
import pandas as pd
from ...domain.entities import Machine, Order

class MachineAnalyzer:
    """Service for analyzing machine metrics following SRP"""
    
    def analyze_machines(self, machines: List[Machine], orders: List[Order]) -> pd.DataFrame:
        """Analyze machine-level metrics"""
        # First, extract phase data from orders
        phase_data = self._extract_phase_data(orders)
        phase_df = pd.DataFrame(phase_data)
        
        # Then analyze each machine
        machine_metrics = []
        
        for machine in machines:
            metrics = self._calculate_machine_metrics(machine, phase_df)
            machine_metrics.append(metrics)
        
        return pd.DataFrame(machine_metrics)
    
    def _extract_phase_data(self, orders: List[Order]) -> List[Dict[str, Any]]:
        """Extract phase data from orders"""
        phase_data = []
        
        for order in orders:
            for phase in order.phases:
                phase_data.append({
                    'phase_name': phase.name,
                    'phase_status': phase.status.value,
                    'cycle_time': phase.cycle_time,
                    'actual_duration_minutes': phase.actual_duration,
                    'queue_delay_hours': phase.queue_delay_hours,
                    'finish_delay_hours': phase.finish_delay_hours,
                    'declared_quantity': phase.declared_quantity,
                    'operators': ','.join(phase.operators),
                    'queue_real_insert_date': phase.queue_real_insert_date,
                    'real_finish_date': phase.real_finish_date
                })
        
        return phase_data
    
    def _calculate_machine_metrics(self, machine: Machine, phase_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate metrics for a single machine"""
        # Filter phases for this machine
        if not phase_df.empty and 'phase_name' in phase_df.columns:
            machine_phases = phase_df[phase_df['phase_name'] == machine.name]
        else:
            machine_phases = pd.DataFrame()
        
        if machine_phases.empty:
            return {
                'machine_name': machine.name,
                'is_active': machine.is_active,
                'queue_target_time': machine.queue_target_time,
                'current_queue_length': machine.queue_length,
                'total_phases_processed': 0,
                'completed_phases': 0,
                'in_progress_phases': 0,
                'avg_cycle_time': 0,
                'avg_actual_duration': 0,
                'avg_queue_delay': 0,
                'avg_finish_delay': 0,
                'total_quantity_processed': 0,
                'unique_operators': 0,
                'efficiency_percentage': None,
                'utilization_percentage': None
            }
        
        metrics = {
            'machine_name': machine.name,
            'is_active': machine.is_active,
            'queue_target_time': machine.queue_target_time,
            'current_queue_length': machine.queue_length,
            'total_phases_processed': len(machine_phases),
            'completed_phases': len(machine_phases[machine_phases['phase_status'] == 4]),
            'in_progress_phases': len(
                machine_phases[machine_phases['phase_status'].isin([1, 2, 3])]
            ),
            'avg_cycle_time': machine_phases['cycle_time'].mean(),
            'avg_actual_duration': machine_phases['actual_duration_minutes'].mean(),
            'avg_queue_delay': machine_phases['queue_delay_hours'].mean(),
            'avg_finish_delay': machine_phases['finish_delay_hours'].mean(),
            'total_quantity_processed': machine_phases['declared_quantity'].sum(),
            'unique_operators': len(
                set(','.join(machine_phases['operators'].fillna('')).split(','))
            )
        }
        
        # Calculate efficiency
        if (metrics['avg_cycle_time'] > 0 and 
            not pd.isna(metrics['avg_actual_duration']) and 
            metrics['avg_actual_duration'] > 0):
            metrics['efficiency_percentage'] = (
                metrics['avg_cycle_time'] / metrics['avg_actual_duration']
            ) * 100
        else:
            metrics['efficiency_percentage'] = None
        
        # Calculate utilization
        metrics['utilization_percentage'] = self._calculate_utilization(machine_phases)
        
        return metrics
    
    def _calculate_utilization(self, machine_phases: pd.DataFrame) -> Optional[float]:
        """Calculate machine utilization percentage"""
        if machine_phases.empty:
            return None
        
        completed = machine_phases[machine_phases['real_finish_date'].notna()]
        if completed.empty:
            return None
        
        first_start = machine_phases['queue_real_insert_date'].min()
        last_finish = machine_phases['real_finish_date'].max()
        
        if pd.isna(first_start) or pd.isna(last_finish):
            return None
        
        date_range = last_finish - first_start
        working_days = date_range.days
        
        if working_days > 0:
            total_working_minutes = working_days * 8 * 60  # 8-hour workday
            total_actual_minutes = machine_phases['actual_duration_minutes'].sum()
            return (total_actual_minutes / total_working_minutes) * 100
        
        return None