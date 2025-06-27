# src/application/services/phase_analyzer.py
from typing import List, Dict, Any
import pandas as pd
from ...domain.entities import Phase, Order

class PhaseAnalyzer:
    """Service for analyzing phase metrics following SRP"""
    
    def analyze_phases(self, orders: List[Order]) -> pd.DataFrame:
        """Extract and analyze phase-level metrics"""
        phase_data = []
        
        for order in orders:
            for phase in order.phases:
                phase_record = {
                    'order_id': order.order_id,
                    'order_status': order.status.value,
                    'phase_id': phase.phase_id,
                    'phase_name': phase.name,
                    'phase_status': phase.status.value,
                    'cycle_time': phase.cycle_time,
                    'actual_duration': phase.actual_duration,
                    'efficiency': phase.efficiency,
                    'queue_delay_hours': phase.queue_delay_hours,
                    'operators': ','.join(phase.operators),
                    'operator_count': len(phase.operators)
                }
                phase_data.append(phase_record)
        
        return pd.DataFrame(phase_data)