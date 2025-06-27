# src/domain/entities/analytics_result.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List

@dataclass
class AnalyticsResult:
    """Analytics result domain entity"""
    timestamp: datetime
    total_orders: int
    completed_orders: int
    active_machines: int
    total_machines: int
    avg_order_lead_time: float
    on_time_delivery_rate: float
    avg_machine_utilization: float
    avg_machine_efficiency: float
    total_operators: int
    bottleneck_machines: List[str]
    files_generated: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'total_orders': self.total_orders,
            'completed_orders': self.completed_orders,
            'active_machines': self.active_machines,
            'total_machines': self.total_machines,
            'avg_order_lead_time': self.avg_order_lead_time,
            'on_time_delivery_rate': self.on_time_delivery_rate,
            'avg_machine_utilization': self.avg_machine_utilization,
            'avg_machine_efficiency': self.avg_machine_efficiency,
            'total_operators': self.total_operators,
            'bottleneck_machines': self.bottleneck_machines,
            'files_generated': self.files_generated
        }